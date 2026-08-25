# -*- coding: utf-8 -*-
"""AI 웹에서 뽑은 이미지를 게임에 집어넣는다.

    python tools/import_image.py <이미지파일> <배경키> [--id 에셋id] [--quality 88]
    python tools/import_image.py ~/Downloads/firefly_01.png sylvarn.deep.goblin

하는 일
    1) 가로 16:9 (1456x816) 로 중앙 크롭 + 리사이즈  ← 게임이 가로로 바뀌었다
    2) webp 로 변환
    3) index.html 의 window.BGS 에 base64 로 넣는다 (같은 id 있으면 교체)
    4) BG_LIB 의 해당 키에 src 를 채운다 (retone 표시가 있었으면 지운다)

에셋 id 는 키에서 자동으로 만든다 — sylvarn.deep.goblin -> sylvarn_deep_goblin.
예전 에셋(forest_beast 같은 이름)은 그대로 두되, 새로 넣는 건 전부 키와 같은 이름을 쓴다.

넣고 나면 반드시:  node tools/check.js
"""
import argparse
import base64
import json
import io
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
TARGET_W, TARGET_H = 1280, 720   # 정확한 가로 16:9. 배경은 전부 이 크기다 (2026-08-25 통일)


def fit_cover(im, w, h):
    """비율이 다르면 중앙을 기준으로 잘라낸 뒤 정확히 w x h 로 맞춘다."""
    src_r, dst_r = im.width / im.height, w / h
    if abs(src_r - dst_r) > 0.001:
        if src_r > dst_r:                      # 원본이 더 넓다 → 좌우를 자른다
            new_w = round(im.height * dst_r)
            left = (im.width - new_w) // 2
            im = im.crop((left, 0, left + new_w, im.height))
        else:                                   # 원본이 더 길다 → 위아래를 자른다
            new_h = round(im.width / dst_r)
            top = (im.height - new_h) // 2
            im = im.crop((0, top, im.width, top + new_h))
    return im.resize((w, h), Image.LANCZOS)


def load_index():
    return INDEX.read_text(encoding="utf-8")


def put_asset(src, asset_id, data_url):
    """window.BGS 에 에셋을 넣거나 교체한다."""
    existing = re.search(r'"%s"\s*:\s*"data:image/[a-z]+;base64,[^"]*"' % re.escape(asset_id), src)
    if existing:
        return src[:existing.start()] + '"%s": "%s"' % (asset_id, data_url) + src[existing.end():], True
    anchor = "window.BGS={"
    i = src.index(anchor) + len(anchor)
    return src[:i] + '"%s": "%s",\n' % (asset_id, data_url) + src[i:], False


def set_lib_src(src, key, asset_id):
    """BG_LIB 의 키에 src 를 채운다. 없는 키면 알려준다."""
    m = re.search(r'("%s"\s*:\s*\{)([^}]*)(\})' % re.escape(key), src)
    if not m:
        return None
    body = m.group(2)
    if re.search(r'src\s*:\s*(null|"[^"]*")', body):
        body = re.sub(r'src\s*:\s*(null|"[^"]*")', 'src:"%s"' % asset_id, body, count=1)
    else:
        body = 'src:"%s",' % asset_id + body
    # 재생성 대기 표시가 있었다면 이제 해결됐으므로 지운다
    body = re.sub(r',?\s*retone\s*:\s*"[^"]*"', "", body)
    return src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():]


def _log_history(a, asset_id, w, h, nbytes):
    """무엇으로 뽑았는지 남긴다. 이게 없으면 나중에 톤을 못 맞춘다."""
    hp = Path(__file__).parent / "asset-history.json"
    try:
        data = json.loads(hp.read_text(encoding="utf-8"))
    except Exception:
        data = {"entries": []}
    data.setdefault("entries", []).append({
        "key": a.key, "asset": asset_id,
        "tool": a.tool or "미기록", "model": a.model or "미기록", "ratio": a.ratio or "미기록",
        "size": "%dx%d" % (w, h), "kb": nbytes // 1024,
        "src_file": Path(a.image).name,
        "prompt": (a.prompt or "")[:400],
    })
    # 셸을 거치며 깨진 문자(서러게이트)가 섞이면 기록이 통째로 죽는다. 그건 막는다
    txt = json.dumps(data, ensure_ascii=False, indent=2)
    hp.write_text(txt.encode("utf-8", "replace").decode("utf-8"), encoding="utf-8")
    if not a.tool:
        print("  ⚠ --tool 을 안 줬다. 나중에 톤 맞출 때 곤란해진다.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("key", help='배경 라이브러리 키. 예: sylvarn.deep.goblin')
    ap.add_argument("--id", default=None, help="에셋 id (기본: 키에서 자동 생성)")
    ap.add_argument("--quality", type=int, default=74)   # 74 로도 배경은 충분하다. 단일 파일이라 용량이 곧 로딩이다
    ap.add_argument("--tool", default=None, help="어디서 뽑았나. 예: Grok Imagine / Firefly")
    ap.add_argument("--model", default=None, help="모델명. 예: v2.0 / GPT Image 2 / Firefly Image 5")
    ap.add_argument("--ratio", default=None, help="생성 비율. 예: 16:9")
    ap.add_argument("--prompt", default=None, help="쓴 프롬프트 (앞부분만이라도)")
    a = ap.parse_args()

    path = Path(a.image).expanduser()
    if not path.exists():
        sys.exit("파일이 없다: %s" % path)

    asset_id = a.id or a.key.replace(".", "_")

    im = Image.open(path).convert("RGB")
    before = "%dx%d" % (im.width, im.height)
    im = fit_cover(im, TARGET_W, TARGET_H)

    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=a.quality, method=6)
    blob = buf.getvalue()
    data_url = "data:image/webp;base64," + base64.b64encode(blob).decode("ascii")

    src = load_index()
    src, replaced = put_asset(src, asset_id, data_url)
    out = set_lib_src(src, a.key, asset_id)
    if out is None:
        sys.exit('BG_LIB 에 "%s" 키가 없다. index.html 의 BG_LIB 에 슬롯을 먼저 만들어라.' % a.key)

    INDEX.write_text(out, encoding="utf-8")
    _log_history(a, asset_id, im.width, im.height, len(blob))
    print("%s  ->  %s" % (path.name, a.key))
    print("  원본 %s → %dx%d webp %dKB" % (before, TARGET_W, TARGET_H, len(blob) // 1024))
    print("  에셋 id: %s (%s)" % (asset_id, "교체" if replaced else "신규"))
    print("  이제:  node tools/check.js")


if __name__ == "__main__":
    main()
