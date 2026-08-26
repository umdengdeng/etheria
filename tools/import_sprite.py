# -*- coding: utf-8 -*-
"""흰 배경 인물 그림을 **투명 스프라이트**로 만들어 게임에 등록한다.

    python tools/import_sprite.py .shots/expr/serenia_sad.png serenia_sad
    python tools/import_sprite.py .shots/expr/serenia_*.png          # 이름 자동(파일명 그대로)

하는 일
    1) 흰 배경을 지워 알파를 만든다 (기존 스프라이트가 전부 RGBA webp 라 맞춘다)
    2) 내용에 맞춰 여백을 잘라내고 세로 820px 로 맞춘다 (엘리아나 535x820 기준)
    3) window.SPRITES 에 base64 webp 로 넣는다 (같은 이름 있으면 교체)

대사에서 쓰는 법
    {sp:"serenia_sad", name:"세레니아", text:"…미안해요."}
    setSp() 가 SPR["eliana_"+k] || SPR[k] 순으로 찾으므로
    **엘리아나가 아닌 캐릭터는 `캐릭터_표정` 전체 이름을 그대로 준다.**

경계 처리
    생성 그림의 배경이 완전한 순백이 아닐 때가 많아서 임계값을 조금 낮게 잡고,
    가장자리 한 겹을 반투명으로 남겨 계단현상을 줄인다.
"""
import base64
import io
import re
import sys
from pathlib import Path

from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
TARGET_H = 820
# 순백(255,255,255)에서 이만큼 떨어지면 인물로 본다.
# LO 이하는 완전 투명, HI 이상은 완전 불투명, 사이는 부드럽게.
LO, HI = 26, 70   # 배경색과 이만큼 떨어지면 인물. 크로마키라 넉넉히 잡아도 된다


def cut_bg(im):
    """배경을 지워 알파를 만든다. **테두리에서 배경색을 직접 읽어** 쓴다.

    ★여기까지 오는 데 세 번 틀렸다.
      ① 「밝으면 배경」(임계 232) → **흰 드레스가 통째로 뚫렸다**
      ② 테두리 flood fill → 머리카락 사이 **갇힌 흰 구멍이 남고**,
         치마 밑단은 아래 테두리와 이어져 **거꾸로 파먹혔다**
      ③ 「순백과의 거리」 → 갇힌 구멍은 지워졌지만
         **비치는 흰 소매가 배경과 색이 완전히 같아서** 같이 지워졌다.
         흰 배경 + 흰 옷은 **색으로는 원리적으로 못 나눈다.**
      → ④ 그래서 배경을 **초록(크로마키)** 으로 뽑는다. 인물 팔레트가
         흰·검정·붉은 눈뿐이라 초록과 절대 안 겹친다. 이제 분리가 확실하다.

    despill(초록 물빼기)까지 한다 — 안 하면 머리카락 가장자리가 초록으로 뜬다.
    """
    import numpy as np

    im = im.convert("RGB")
    a = np.asarray(im).astype(np.float32)
    H, W, _ = a.shape

    # 테두리에서 배경색을 읽는다 (사람이 테두리에 닿아 있어도 중앙값이면 버틴다)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]], axis=0)
    bg = np.median(border, axis=0)

    dist = np.abs(a - bg).max(axis=2)

    # ★비치는 천이 문제였다.
    #   얇은 천이 초록 배경 위에 겹치면 렌더 결과가 「흰색+초록」의 중간색이 된다.
    #   거리로만 알파를 매기면 그 부분이 **반투명**으로 남아, 게임에서 뒤 배경이
    #   그대로 비쳐 보인다 (자주색 배경에 올려보니 드레스가 얼룩덜룩해 보였다).
    #   → 실루엣 **안쪽은 무조건 불투명**으로 채우고, 부드럽게 깎는 건
    #     바깥 경계 한 겹에서만 한다.
    solid = dist > LO                      # 배경이 아니라고 볼 수 있는 곳
    from scipy import ndimage             # noqa
    filled = ndimage.binary_fill_holes(solid)
    alpha = np.where(filled, 255.0, 0.0)
    # 경계만 살짝 부드럽게 (계단 방지)
    edge = np.clip((dist - LO) * (255.0 / (HI - LO)), 0, 255)
    boundary = filled & (ndimage.binary_erosion(filled, iterations=2) == False)
    alpha[boundary] = np.minimum(alpha[boundary], edge[boundary])

    # despill — 초록물만 뺀다.
    # ★기준을 R·B **평균**으로 잡으면 피부까지 깎여서 보랏빛이 된다.
    #   피부는 R > G > B 라 평균보다는 늘 높기 때문이다. (2026-08-26에 그렇게 됐다)
    #   R·B 중 **큰 값**을 넘을 때만 깎아야 초록이 실제로 튄 곳만 잡힌다.
    if bg[1] > bg[0] and bg[1] > bg[2]:
        rb = np.maximum(a[:, :, 0], a[:, :, 2])
        over = np.clip(a[:, :, 1] - rb, 0, None)
        a[:, :, 1] -= over

        # ★어두운 머리카락 가장자리는 이것만으로 안 빠진다.
        #   검은 머리에 초록이 섞이면 G 를 깎아도 (R, B, B) 꼴이 남아 **청록**으로 뜬다.
        #   그래서 어두운 픽셀 중 G·B 가 R 보다 뜬 곳은 무채색으로 눌러버린다.
        #   밝은 드레스는 luminance 조건에 안 걸려서 안전하다.
        # ★밝기 조건을 걸면 머리 **끝쪽의 밝은 청록**이 안 잡힌다.
        #   이 캐릭터의 팔레트에는 초록·청록이 아예 없다(흰 드레스·검은 머리·붉은 눈·은관).
        #   그러니 G·B 가 R 보다 뜨는 곳은 전부 배경물이 든 것으로 봐도 된다.
        #   흰 드레스는 R≈G≈B, 피부는 R>G>B 라 안 걸린다.
        teal = (a[:, :, 1] > a[:, :, 0] + 6) & (a[:, :, 2] > a[:, :, 0] + 6)
        if teal.any():
            r = a[:, :, 0]
            a[:, :, 1] = np.where(teal, r, a[:, :, 1])
            a[:, :, 2] = np.where(teal, r, a[:, :, 2])

    out = np.dstack([np.clip(a, 0, 255), alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def to_upper(im, ratio=0.60):
    """전신 그림을 대사용 상반신으로 잘라낸다.

    ★전신으로 뽑는 이유는 **머리가 안 잘리게 여백을 확보하려고**다.
      상반신으로 직접 뽑으면 이 모델은 인물로 프레임을 꽉 채워서 머리카락이 잘린다.
      그래서 전신으로 뽑고 여기서 자른다.
    """
    import numpy as np
    a = np.asarray(im.convert("RGB")).astype(float)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]], axis=0)
    bg = np.median(border, axis=0)
    subj = np.abs(a - bg).max(axis=2) > 40
    ys, xs = np.where(subj)
    if not len(ys):
        return im
    top, bot = ys.min(), ys.max()
    cut = int(top + (bot - top) * ratio)
    pad = 12
    return im.crop((max(0, xs.min() - pad), max(0, top - pad),
                    min(im.width, xs.max() + pad), min(im.height, cut)))


def trim(im):
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def put_sprite(src, name, data_url):
    pat = r'"%s"\s*:\s*"data:image/[a-z]+;base64,[^"]*"' % re.escape(name)
    m = re.search(pat, src)
    if m:
        return src[:m.start()] + '"%s": "%s"' % (name, data_url) + src[m.end():], True
    anchor = "window.SPRITES={"
    i = src.index(anchor) + len(anchor)
    return src[:i] + '"%s": "%s",\n' % (name, data_url) + src[i:], False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    # 마지막 인자가 파일이 아니면 이름으로 본다
    name_arg = None
    if len(args) == 2 and not Path(args[1]).exists():
        name_arg = args[1]; args = args[:1]

    src = INDEX.read_text(encoding="utf-8")
    for path in args:
        p = Path(path)
        if not p.exists():
            print("  없다: %s" % p); continue
        name = name_arg or p.stem
        raw = Image.open(p)
        if "--upper" in sys.argv:
            raw = to_upper(raw)
        im = trim(cut_bg(raw))
        w = max(1, round(im.width * TARGET_H / im.height))
        im = im.resize((w, TARGET_H), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=88, method=6)
        blob = buf.getvalue()
        data_url = "data:image/webp;base64," + base64.b64encode(blob).decode("ascii")
        src, replaced = put_sprite(src, name, data_url)
        print("  %-22s %dx%d  %dKB  (%s)" % (name, w, TARGET_H, len(blob) // 1024,
                                             "교체" if replaced else "신규"))
    INDEX.write_text(src, encoding="utf-8")
    print("이제:  node tools/check.js")


if __name__ == "__main__":
    main()
