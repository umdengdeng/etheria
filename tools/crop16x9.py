# -*- coding: utf-8 -*-
"""세로로 뽑은 인물 컷을 **손을 안 자르고** 가로 16:9 로 만든다.

    python tools/crop16x9.py .shots/comfy/s1.png
    python tools/crop16x9.py .shots/comfy/*.png --out .shots/comfy16

왜 필요한가
    ComfyUI(Illustrious)는 좁은 프레임을 주면 뻗은 손을 반드시 화면 가장자리에
    붙여버린다. 프롬프트로 「여백을 둬라」는 세 번 시도해서 세 번 다 실패했다.
    (2026-08-26. holdA 388px · holdB 215px · fitB 790px 씩 테두리에 살갗이 남았다)

    그래서 순서를 뒤집는다 —
      ① **전신으로 뽑아 여백을 확보하고**
      ② 손이 전부 들어오는 범위로 **여기서 잘라낸다.**
    자르는 건 계산이라 실패할 수가 없다.

하는 일
    - 밝은 배경을 기준으로 인물 경계와 **살갗(손·얼굴) 위치**를 찾는다
    - 머리 위 여백부터 **손끝 아래**까지가 반드시 들어가도록 세로 범위를 잡는다
    - 16:9 가 되도록 좌우를 정하고, 모자라면 **원본 배경색으로** 채운다
      (흰색으로 채우면 이음매가 보인다 — 배경이 순백이 아닌 경우가 많다)
    - 마지막에 테두리에 살갗이 남아 있는지 다시 재서 알려준다
"""
import sys
from pathlib import Path

from PIL import Image

# 윈도우 콘솔이 cp949 라 「—」 같은 글자에서 죽는다
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

W_OUT, H_OUT = 1280, 720
BRIGHT = 238          # 이보다 밝으면 배경으로 본다


def is_skin(c):
    r, g, b = c[:3]
    return r > 150 and g > 100 and b > 80 and r > g > b and (r - b) > 25 and (r - g) < 70


def edge_skin(im):
    """테두리에 살갗이 몇 픽셀이나 있나. 0 이 아니면 손·팔이 잘린 것이다."""
    px = im.load(); W, H = im.size
    out = {}
    for k, pts in (("위", [(x, y) for x in range(W) for y in (0, 1)]),
                   ("왼", [(x, y) for y in range(H) for x in (0, 1)]),
                   ("오른", [(x, y) for y in range(H) for x in (W - 2, W - 1)])):
        out[k] = sum(1 for x, y in pts if is_skin(px[x, y]))
    return out


def convert(path, outdir):
    src = Image.open(path).convert("RGB")
    W, H = src.size
    px = src.load()
    g = src.convert("L").load()
    bg = src.getpixel((3, 3))

    ys = [y for y in range(H) if any(g[x, y] < BRIGHT for x in range(0, W, 3))]
    xs = [x for x in range(W) if any(g[x, y] < BRIGHT for y in range(0, H, 3))]
    sy = [y for y in range(0, H, 2) for x in range(0, W, 2) if is_skin(px[x, y])]
    if not ys or not sy:
        print("  %s — 인물을 못 찾았다" % Path(path).name)
        return None

    top = max(0, ys[0] - 45)                 # 머리 위 여백
    bot = min(H, max(sy) + 150)              # ★손끝 아래로 넉넉히. 여기가 핵심이다
    need_w = int((bot - top) * W_OUT / H_OUT)
    cx = (xs[0] + xs[-1]) // 2
    left = 0 if need_w >= W else max(0, min(W - need_w, cx - need_w // 2))
    crop = src.crop((left, top, min(W, left + need_w), bot))

    out = Image.new("RGB", (W_OUT, H_OUT), bg)
    s = crop.resize((int(crop.width * H_OUT / crop.height), H_OUT), Image.LANCZOS)
    if s.width > W_OUT:
        s = s.crop(((s.width - W_OUT) // 2, 0, (s.width - W_OUT) // 2 + W_OUT, H_OUT))
    out.paste(s, ((W_OUT - s.width) // 2, 0))

    dst = Path(outdir) / (Path(path).stem + "_16x9.png")
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst)
    e = edge_skin(out); tot = sum(e.values())
    print("  %-14s → %s   테두리 살갗 %dpx %s"
          % (Path(path).name, dst.name, tot, "✅" if tot == 0 else "❌ 아직 잘린다"))
    return dst


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    outdir = "."
    if "--out" in sys.argv:
        outdir = sys.argv[sys.argv.index("--out") + 1]
        args = [a for a in args if a != outdir]
    if not args:
        sys.exit(__doc__)
    print("가로 16:9 변환 — 손이 잘리지 않는 범위로 자른다")
    for a in args:
        convert(a, outdir)


if __name__ == "__main__":
    main()
