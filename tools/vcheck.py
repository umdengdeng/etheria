# -*- coding: utf-8 -*-
"""비주얼 연출 검사기 — 「그림이 있냐」가 아니라 「연출이 있냐」를 본다.

    python tools/vcheck.py                 전체
    python tools/vcheck.py serenia         키에 serenia 가 들어간 것만
    python tools/vcheck.py --verbose       통과한 것도 수치까지 보여준다

check.js 가 잡는 것 = 키가 안 풀린다 / 에셋이 방치됐다 / 대사와 그림이 다르다.
이건 그걸로는 절대 안 걸리는 것을 본다:

    「그림은 멀쩡한데 연출이 없다」

세레니아 오프닝이 그랬다. 인물이 화면 정중앙에, 좌우 완벽 대칭으로,
두 팔을 T 자로 벌리고, 카메라와 정확히 같은 눈높이에 서 있었다.
자료 사진으로는 맞는데 연출로는 죽은 컷이다.

--- 무엇을 재나 ---------------------------------------------------------

1) 좌우대칭   윤곽 에너지가 좌우로 어떻게 분포하는지 본다.
              (통째로 뒤집어 픽셀을 비교하면 흰 배경이 넓은 그림에서 오판한다)
              분포가 같을수록 「정면 박제」. T 포즈·증명사진 구도가 여기 걸린다.
2) 무게중심   윤곽선 에너지의 x·y 중심. 정확히 한가운데면 구도가 심심하다.
              삼분할선(1/3·2/3) 근처가 살아 있는 위치다.
3) 시선높이   에너지의 y 중심이 정확히 절반이면 아이레벨 정면. 컷마다 같으면 단조롭다.
4) 명암폭     밝기 표준편차. 좁으면 평평해서 깊이가 안 생긴다.
5) 헤드룸     위쪽이 텅 비었는지 / 인물이 천장에 닿는지.

+ 프롬프트 검사: asset-history.json 에 남은 프롬프트에 연출 지시어가
  하나도 없으면 경고한다. 연출은 우연히 나오지 않는다. 적어야 나온다.

수치는 판사가 아니라 눈을 돌릴 곳을 알려주는 장치다.
걸렸다고 무조건 다시 뽑을 필요는 없다 — 다만 걸린 컷은 반드시 눈으로 볼 것.
"""
import base64
import io
import json
import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageFilter

# 윈도우 콘솔이 cp949 라 「—」 같은 글자에서 죽는다. 출력만 utf-8 로 바꾼다
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
HISTORY = Path(__file__).parent / "asset-history.json"

# 연출을 지시하는 말들. 프롬프트에 이 중 하나도 없으면 정면 증명사진이 나온다.
STAGING_WORDS = [
    "앵글", "로우", "하이", "올려다", "내려다", "부감", "앙각",
    "역광", "실루엣", "그림자", "측광",
    "비대칭", "한쪽", "기울", "젖히", "숙이", "굽히",
    "측면", "반측면", "옆", "뒤에서", "어깨너머", "돌아보",
    "클로즈업", "익스트림", "원경",
    "시선", "뻗", "내밀", "쥐", "기대", "걸터", "웅크",
    "움직", "흔들", "휘날", "쏠",
    "off-center", "low angle", "high angle", "backlit", "rim light",
    "over the shoulder", "dutch", "asymmetric", "three-quarter",
]

# 정면 대칭이 오히려 맞는 것들 — 여기 걸려도 넘어간다
# 문·복도·제단은 정면이어야 문답고, 뒤로 빠지는 컷(pull)은 좌우가 같아야
# 「카메라가 멀어진다」로 읽힌다. 비대칭으로 만들면 오히려 틀린 그림이 된다.
SYMMETRY_OK = ("gate", "hall", "door", "corridor", "shrine", "altar", "pull", "tunnel")

# 그림이 아니라 화면 전환 장치다. 연출을 따지지 않는다
BLANKS = ("bg_black", "bg_white")


def load_assets():
    """index.html 의 window.BGS 에서 배경만 꺼낸다."""
    src = INDEX.read_text(encoding="utf-8")
    i = src.index("window.BGS={")
    blk = src[i:src.index("};", i)]
    out = {}
    for m in re.finditer(r'"([A-Za-z0-9_]+)"\s*:\s*"data:image/[a-z]+;base64,([^"]+)"', blk):
        out[m.group(1)] = m.group(2)
    return out, src


def tone_of(src, asset_id):
    """BG_LIB 에 적힌 tone 을 되찾는다. 밤 컷을 「평평하다」고 잡지 않기 위해서다."""
    m = re.search(r'\{[^}]*src\s*:\s*"%s"[^}]*tone\s*:\s*"([a-z]+)"' % re.escape(asset_id), src)
    return m.group(1) if m else None


def key_of(src, asset_id):
    """에셋을 부르는 배경 키를 되찾는다. 어느 장면 것인지 알아야 처방이 나온다."""
    m = re.search(r'"([a-z0-9]+\.[a-z0-9]+\.[a-z0-9]+)"\s*:\s*\{[^}]*src\s*:\s*"%s"' % re.escape(asset_id), src)
    return m.group(1) if m else None


def measure(im):
    """작게 줄여서 잰다. 연출은 큰 덩어리의 문제라 해상도가 필요 없다."""
    g = im.convert("L").resize((96, 54), Image.LANCZOS)
    px = list(g.getdata())
    W, H = 96, 54

    # --- 윤곽 에너지 ------------------------------------------------------
    e = list(g.filter(ImageFilter.FIND_EDGES).getdata())
    tot = sum(e) or 1
    cx = sum(v * (i % W) for i, v in enumerate(e)) / tot / (W - 1)
    cy = sum(v * (i // W) for i, v in enumerate(e)) / tot / (H - 1)

    # --- 4) 명암폭 --------------------------------------------------------
    mean = sum(px) / len(px)
    sd = math.sqrt(sum((v - mean) ** 2 for v in px) / len(px)) / 255.0

    # --- 5) 헤드룸 : 위 20% 와 아래 20% 에 에너지가 얼마나 있나 -------------
    top = sum(e[: W * (H // 5)]) / tot
    bot = sum(e[W * (H - H // 5):]) / tot

    # --- 6) 주피사체가 있는 그림인가 ---------------------------------------
    # 숲·성벽처럼 결이 고르게 깔린 그림은 윤곽 에너지가 온 화면에 퍼져 있어
    # 무게중심이 무조건 정가운데로 나온다. 거기에 대고 「정중앙이다」라고
    # 하면 전부 걸린다. 그래서 「덩어리가 있는 그림」에만 구도를 따진다.
    # 세로 줄별 에너지 분포의 엔트로피 — 1에 가까울수록 고르게 퍼진 결.
    col = [sum(e[y * W + x] for y in range(H)) / tot for x in range(W)]
    ent = -sum(c * math.log(c) for c in col if c > 0) / math.log(W)

    # --- 1) 좌우대칭 -------------------------------------------------------
    # 처음엔 그림을 통째로 뒤집어 픽셀 차이를 쟀다. 그런데 흰 공간처럼
    # 배경이 화면의 90% 인 그림에서는 인물을 오른쪽 끝으로 밀어놔도
    # 평균 차이가 거의 안 움직여서 「정면 대칭」으로 잘못 잡혔다.
    # (2026-08-25 세레니아 wide 컷이 실제로 그렇게 오판됐다)
    # → 픽셀이 아니라 **윤곽 에너지가 좌우로 어떻게 분포하는가**를 본다.
    #    배경 넓이에 휘둘리지 않고 「어디에 뭐가 있나」만 남는다.
    sym = sum(abs(col[x] - col[W - 1 - x]) for x in range(W)) / 2.0

    return {"sym": sym, "cx": cx, "cy": cy, "sd": sd, "top": top, "bot": bot, "ent": ent}


def judge(asset_id, key, m, prompt):
    """수치를 사람 말로 옮기고, 무엇을 바꿔야 하는지까지 적는다."""
    bad, warn = [], []
    name = key or asset_id
    sym_exempt = any(w in name for w in SYMMETRY_OK)

    # 화면 전환용 공백은 연출을 따질 대상이 아니다
    if asset_id in BLANKS:
        return [], []

    # 덩어리가 있는 그림에만 구도를 따진다 (숲·성벽은 무게중심이 늘 한가운데다)
    has_subject = m["ent"] < 0.93
    # 어두운 게 맞는 컷인지는 이름이 아니라 라이브러리의 tone 으로 판단한다.
    # tone 은 실제 이미지를 눈으로 확인하고 적어둔 값이라 파일명보다 믿을 만하다.
    flat_ok = m.get("tone") in ("night", "dim", "flat", "white")

    if m["sym"] < 0.05 and not sym_exempt:
        bad.append((
            "정면대칭",
            "윤곽이 좌우로 거의 똑같이 퍼져 있다 (%.3f). 정면에 놓고 한가운데 세운 증명사진 구도다." % m["sym"],
            "몸을 반측면으로 틀거나, 한쪽 팔만 올리거나, 카메라를 조금 옆·아래로 옮긴다.",
        ))
    elif m["sym"] < 0.09 and not sym_exempt:
        warn.append(("대칭기울음", "좌우 분포가 꽤 닮았다 (%.3f)." % m["sym"], "한쪽에만 무게를 준다."))

    if has_subject and abs(m["cx"] - 0.5) < 0.035:
        bad.append((
            "정중앙",
            "주피사체가 화면 한가운데 박혀 있다 (x=%.2f)." % m["cx"],
            "삼분할선(x≈0.33 또는 0.67)으로 밀고, 빈 쪽을 시선이 향하는 방향으로 비운다.",
        ))

    if has_subject and abs(m["cy"] - 0.5) < 0.04:
        warn.append((
            "아이레벨",
            "시선 높이가 정확히 화면 절반이다 (y=%.2f)." % m["cy"],
            "올려다보거나 내려다본다. 같은 장면이 이어질 때 높이를 바꾸면 리듬이 생긴다.",
        ))

    if m["sd"] < 0.085 and not flat_ok:
        bad.append((
            "명암없음",
            "밝기 폭이 거의 없다 (%.3f). 깊이가 안 생기고 인물이 배경에 붙는다." % m["sd"],
            "역광이나 측광을 넣어 인물 윤곽만이라도 떼어낸다.",
        ))
    elif m["sd"] < 0.085:
        warn.append(("의도된평평", "밝기 폭이 거의 없다 (%.3f). tone 상 의도된 것으로 보이지만 한 번 볼 것." % m["sd"],
                     "광원을 하나 정해 밝은 점을 만들면 깊이가 생긴다."))

    if has_subject and m["top"] < 0.05:
        warn.append(("헤드룸과다", "위쪽 1/5 가 텅 비었다 (%.2f)." % m["top"], "인물을 올리거나 위를 잘라낸다."))

    if prompt is not None and not any(w in prompt for w in STAGING_WORDS):
        warn.append((
            "연출지시없음",
            "프롬프트에 앵글·시선·자세를 지시한 말이 하나도 없다.",
            "「반측면으로」「올려다보는 각도」「한 손만 뻗어」처럼 적어야 그렇게 나온다.",
        ))
    return bad, warn


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    verbose = "--verbose" in sys.argv
    filt = args[0] if args else None

    assets, src = load_assets()
    prompts = {}
    if HISTORY.exists():
        for e in json.loads(HISTORY.read_text(encoding="utf-8")).get("entries", []):
            prompts[e["asset"]] = e.get("prompt", "")

    rows = []
    for aid, b64 in assets.items():
        key = key_of(src, aid)
        if filt and filt not in aid and filt not in (key or ""):
            continue
        im = Image.open(io.BytesIO(base64.b64decode(b64)))
        m = measure(im)
        m["tone"] = tone_of(src, aid)
        bad, warn = judge(aid, key, m, prompts.get(aid))
        rows.append((aid, key, m, bad, warn))

    rows.sort(key=lambda r: (-len(r[3]), -len(r[4])))
    nbad = sum(1 for r in rows if r[3])
    nwarn = sum(1 for r in rows if not r[3] and r[4])

    print("비주얼 연출 검사 — 배경 %d장 · 연출 죽은 컷 %d · 살펴볼 것 %d" % (len(rows), nbad, nwarn))
    print()

    for aid, key, m, bad, warn in rows:
        if not bad and not warn and not verbose:
            continue
        head = "%s%s" % (key or aid, "" if key else "  (라이브러리 미등록)")
        print("── %s" % head)
        if verbose:
            print("     대칭 %.3f · 중심 x%.2f y%.2f · 명암폭 %.3f · 위 %.2f 아래 %.2f"
                  % (m["sym"], m["cx"], m["cy"], m["sd"], m["top"], m["bot"]))
        for tag, why, fix in bad:
            print("  ✗ [%s] %s" % (tag, why))
            print("     → %s" % fix)
        for tag, why, fix in warn:
            print("  · [%s] %s" % (tag, why))
            print("     → %s" % fix)
        print()

    if nbad:
        print("걸린 컷은 반드시 눈으로 볼 것. 수치는 어디를 볼지 알려줄 뿐이다.")


if __name__ == "__main__":
    main()
