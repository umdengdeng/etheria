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

from PIL import Image, ImageFilter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
TARGET_H = 820
BRIGHT = 232        # 이보다 밝으면 배경으로 본다


def cut_bg(im):
    """배경만 알파로 바꾼다.

    ★밝기만 보면 **흰 드레스가 통째로 뚫린다.** (2026-08-26에 실제로 그랬다)
      그래서 「밝다」가 아니라 **「테두리에서 이어져 있는 밝은 영역」**만 배경으로 본다.
      화면 가장자리에서 flood fill 로 번져 들어가고, 인물 안쪽의 흰색은 살아남는다.
    """
    im = im.convert("RGBA")
    W, H = im.size
    px = im.load()

    bright = bytearray(W * H)
    for y in range(H):
        base = y * W
        for x in range(W):
            r, g, b, _ = px[x, y]
            if r >= BRIGHT and g >= BRIGHT and b >= BRIGHT:
                bright[base + x] = 1

    # 테두리의 밝은 점에서 시작해 번져 나간다
    from collections import deque
    seen = bytearray(W * H)
    q = deque()
    for x in range(W):
        for y in (0, H - 1):
            i = y * W + x
            if bright[i] and not seen[i]:
                seen[i] = 1; q.append(i)
    for y in range(H):
        for x in (0, W - 1):
            i = y * W + x
            if bright[i] and not seen[i]:
                seen[i] = 1; q.append(i)
    while q:
        i = q.popleft()
        x, y = i % W, i // W
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < W and 0 <= ny < H:
                j = ny * W + nx
                if bright[j] and not seen[j]:
                    seen[j] = 1; q.append(j)

    mask = Image.frombytes("L", (W, H), bytes(0 if seen[i] else 255 for i in range(W * H)))
    mask = mask.filter(ImageFilter.GaussianBlur(0.8))   # 톱니 줄이기
    im.putalpha(mask)
    return im


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
        im = trim(cut_bg(Image.open(p)))
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
