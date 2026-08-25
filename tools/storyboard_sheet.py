# -*- coding: utf-8 -*-
"""키프레임 이미지들을 컷 번호·지문과 함께 한 장짜리 스토리보드 시트로 합친다.

    python tools/storyboard_sheet.py .shots/sheet_1hwa.json

입력 JSON:
{
  "title": "제1장 1화 「뜯겨온 자」",
  "subtitle": "26컷 중 키프레임 9",
  "out": ".shots/STORYBOARD_1화.png",
  "cols": 3,
  "frames": [
    {"prefix": "F1_", "cut": "컷 2", "caption": "부름 — ...", "note": "신규"},
    ...
  ]
}
prefix 는 .shots/ 안에서 그 이름으로 시작하는 가장 최근 파일을 찾는다.
"""
import glob
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / ".shots"

BG = (18, 20, 26)
CARD = (28, 31, 40)
INK = (238, 242, 248)
MUTED = (150, 163, 182)
ACCENT = (107, 168, 255)
NEW = (255, 122, 168)

FONT_DIR = Path("C:/Windows/Fonts")


def font(size, bold=False):
    f = FONT_DIR / ("malgunbd.ttf" if bold else "malgun.ttf")
    return ImageFont.truetype(str(f), size)


def newest(prefix):
    hits = sorted(glob.glob(str(SHOTS / (prefix + "*.png"))), key=os.path.getmtime)
    if not hits:
        raise SystemExit("이미지를 못 찾음: %s*" % prefix)
    return hits[-1]


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=fnt) <= max_w:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    frames = cfg["frames"]
    cols = cfg.get("cols", 3)
    rows = (len(frames) + cols - 1) // cols

    IW, IH = 400, 514          # 셀 안 이미지 크기
    PAD, GAP = 26, 18
    CAP_H = 108                 # 지문 영역
    CELL_W, CELL_H = IW + PAD, IH + CAP_H + PAD
    HEAD = 118

    W = cols * CELL_W + GAP * (cols + 1)
    H = HEAD + rows * CELL_H + GAP * (rows + 1)

    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)

    d.text((GAP + 12, 30), cfg["title"], fill=INK, font=font(38, bold=True))
    d.text((GAP + 12, 78), cfg.get("subtitle", ""), fill=MUTED, font=font(20))

    f_cut = font(21, bold=True)
    f_cap = font(17)
    f_tag = font(15, bold=True)

    for i, fr in enumerate(frames):
        cx = GAP + (i % cols) * (CELL_W + GAP)
        cy = HEAD + GAP + (i // cols) * (CELL_H + GAP)
        d.rounded_rectangle([cx, cy, cx + CELL_W, cy + CELL_H], 14, fill=CARD)

        im = Image.open(newest(fr["prefix"])).convert("RGB")
        im = im.resize((IW, IH), Image.LANCZOS)
        sheet.paste(im, (cx + PAD // 2, cy + PAD // 2))

        ty = cy + PAD // 2 + IH + 12
        d.text((cx + PAD // 2, ty), fr["cut"], fill=ACCENT, font=f_cut)
        if fr.get("note"):
            w = d.textlength(fr["cut"], font=f_cut)
            d.text((cx + PAD // 2 + w + 12, ty + 3), fr["note"], fill=NEW, font=f_tag)

        for n, line in enumerate(wrap(d, fr["caption"], f_cap, IW - 8)[:3]):
            d.text((cx + PAD // 2, ty + 30 + n * 24), line, fill=INK, font=f_cap)

    out = ROOT / cfg.get("out", ".shots/STORYBOARD.png")
    sheet.save(out)
    print("%s  (%dx%d, %dKB)" % (out, W, H, out.stat().st_size // 1024))


if __name__ == "__main__":
    main()
