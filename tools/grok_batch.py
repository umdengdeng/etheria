# -*- coding: utf-8 -*-
"""Grok Imagine 에서 배경을 연달아 뽑고 키 이름으로 받아둔다.
   python tools/grok_batch.py <시작index> <개수>
좌표는 최대화된 창(1936x1048) 기준. 창 크기가 다르면 안 맞는다."""
import json, os, shutil, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pyautogui, pyperclip

pyautogui.PAUSE = 0.5
DL = Path.home() / "Downloads"
OUT = Path(__file__).parent.parent / ".shots" / "bg20"
OUT.mkdir(parents=True, exist_ok=True)

PROMPT_BOX = (1050, 955)
RESULT_1   = (565, 320)     # 최신 결과 줄의 1번 (Grok 은 최신을 맨 위에 놓는다)
DOWNLOAD   = (1863, 1007)
BACK       = (230, 146)

EXT = ("*.jpg", "*.jpeg", "*.png", "*.webp")

def snapshot():
    """다운로드 폴더 상태. 파일명 패턴이 매번 달라서(grok-image-*.jpg / UUID.jpg)
       이름으로 거르지 않고 '새로 생긴 파일'로 찾는다."""
    out = set()
    for e in EXT:
        out |= {p.name for p in DL.glob(e)}
    return out

def newest_dl(before):
    for _ in range(25):
        new = snapshot() - before
        new = {n for n in new if not n.endswith(".crdownload")}
        if new:
            cands = [DL / n for n in new]
            return max(cands, key=lambda p: p.stat().st_mtime)
        time.sleep(1)
    return None

def run(items):
    done, failed = [], []
    for it in items:
        key = it["key"]
        before = snapshot()
        pyautogui.click(*PROMPT_BOX); time.sleep(0.8)
        pyautogui.hotkey("ctrl", "a")
        pyperclip.copy(it["prompt"])
        pyautogui.hotkey("ctrl", "v"); time.sleep(1.5)
        pyautogui.press("enter")
        print(key, "생성...", flush=True)
        time.sleep(40)
        pyautogui.click(*RESULT_1); time.sleep(3.5)
        pyautogui.click(*DOWNLOAD); time.sleep(4)
        f = newest_dl(before)
        if f:
            dst = OUT / (key.replace(".", "_") + ".jpg")
            shutil.move(str(f), str(dst))
            print("   받음:", dst.name, flush=True)
            done.append(key)
        else:
            print("   다운로드 실패", flush=True)
            failed.append(key)
        pyautogui.click(*BACK); time.sleep(3)
    return done, failed

if __name__ == "__main__":
    items = json.load(open(Path(__file__).parent.parent / ".shots" / "batch_bg.json", encoding="utf-8"))
    s = int(sys.argv[1]); n = int(sys.argv[2])
    d, f = run(items[s:s+n])
    print("완료 %d · 실패 %d" % (len(d), len(f)))
    if f: print("실패:", ", ".join(f))
