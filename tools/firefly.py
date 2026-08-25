# -*- coding: utf-8 -*-
"""파이어플라이 웹을 직접 조작해서 이미지를 뽑는다.

    python tools/firefly.py open                     ← 새 탭으로 파이어플라이 열기
    python tools/firefly.py ratio                    ← 비율을 세로(3:4)로
    python tools/firefly.py gen "프롬프트 내용"        ← 프롬프트 넣고 생성 (완료까지 대기)
    python tools/firefly.py gen --file prompts.txt   ← 파일에서 프롬프트 읽기
    python tools/firefly.py shot                     ← 지금 화면 캡쳐
    python tools/firefly.py zoom 1                   ← 결과 1번 크게 보기 / zoom close 로 닫기

좌표는 tools/ui-map.json 에 있다. UI 바뀌면 거기만 고치면 된다.

⚠ 사용자의 실제 화면을 조작한다. 각 단계마다 캡쳐를 남기니 .shots/ 를 확인할 것.
⚠ 뽑은 이미지를 게임에 넣는 건 import_image.py 가 한다. 화풍이 실사 쪽이라
   콘티 판단용으로 쓰고, 게임 배경 에셋으로 쓸 거면 결과를 먼저 눈으로 확인할 것.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import pyautogui
import pyperclip

sys.path.insert(0, str(Path(__file__).parent))
import eyes  # noqa: E402

pyautogui.PAUSE = 0.4
pyautogui.FAILSAFE = True

MAP = json.loads((Path(__file__).parent / "ui-map.json").read_text(encoding="utf-8"))
FF = MAP["firefly"]


def _click(name, settle=1.0):
    x, y = FF[name]
    pyautogui.click(x, y)
    time.sleep(settle)
    return x, y


def shot(name="ff"):
    """캡쳐하고 축소본 경로를 돌려준다."""
    return eyes.shrink(eyes.capture_full(name), name=name + "_small")


def cmd_open():
    pyautogui.hotkey("ctrl", "t")
    time.sleep(0.8)
    pyautogui.typewrite(FF["url"], interval=0.02)
    pyautogui.press("enter")
    print("파이어플라이 여는 중...")
    time.sleep(9)
    print(shot("ff_open"))


def cmd_ratio(scrolled=False):
    """비율을 세로(3:4)로. 프롬프트를 이미 넣었으면 scrolled=True."""
    _click("비율드롭다운_스크롤후" if scrolled else "비율드롭다운_초기", settle=1.2)
    _click("비율옵션_세로3to4_아래로열릴때" if scrolled else "비율옵션_세로3to4_위로열릴때", settle=1.2)
    print("비율 세로(3:4)")
    print(shot("ff_ratio"))


def cmd_gen(prompt, wait=28, first=False):
    """프롬프트를 넣고 생성. first=True 면 아직 결과가 없는 첫 생성."""
    _click("프롬프트입력창_초기" if first else "프롬프트입력창_결과표시후", settle=0.6)
    pyautogui.hotkey("ctrl", "a")
    pyperclip.copy(prompt)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.2)
    _click("생성버튼", settle=0.5)
    print("생성 클릭 — %d초 대기" % wait)
    time.sleep(wait)
    print(shot("ff_result"))


def cmd_zoom(which):
    if str(which) == "close":
        _click("확대_닫기", settle=1.5)
    else:
        _click("결과이미지_%s번" % which, settle=2.5)
    print(shot("ff_zoom"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["open", "ratio", "gen", "shot", "zoom"])
    ap.add_argument("arg", nargs="?", default=None)
    ap.add_argument("--file", default=None, help="프롬프트를 파일에서 읽는다")
    ap.add_argument("--scrolled", action="store_true", help="패널이 스크롤된 상태")
    ap.add_argument("--first", action="store_true", help="첫 생성 (결과가 아직 없음)")
    ap.add_argument("--wait", type=int, default=28)
    a = ap.parse_args()

    if a.cmd == "open":
        cmd_open()
    elif a.cmd == "ratio":
        cmd_ratio(scrolled=a.scrolled)
    elif a.cmd == "gen":
        text = Path(a.file).read_text(encoding="utf-8").strip() if a.file else a.arg
        if not text:
            sys.exit('프롬프트가 없다. gen "내용" 또는 --file 로 줘라.')
        cmd_gen(text, wait=a.wait, first=a.first)
    elif a.cmd == "shot":
        print(shot())
    elif a.cmd == "zoom":
        cmd_zoom(a.arg or 1)


if __name__ == "__main__":
    main()
