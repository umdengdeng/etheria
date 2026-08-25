"""
hands.py - 마우스/키보드 조작 (GameForge/agent/hands.py 에서 가져옴)
"""

import pyautogui
import pyperclip
import time

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


def click(x, y):
    pyautogui.click(x, y)


def double_click(x, y):
    pyautogui.doubleClick(x, y)


def right_click(x, y):
    pyautogui.rightClick(x, y)


def type_text(text, interval=0.05):
    pyautogui.typewrite(text, interval=interval)


def type_korean(text):
    """한글은 클립보드 경유로 붙여넣는다."""
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')


def press_key(key):
    pyautogui.press(key)


def hotkey(*keys):
    pyautogui.hotkey(*keys)


def move_to(x, y):
    pyautogui.moveTo(x, y)


def scroll(amount):
    pyautogui.scroll(amount)


def drag(start_x, start_y, end_x, end_y, duration=0.5):
    pyautogui.moveTo(start_x, start_y)
    pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)


if __name__ == "__main__":
    print(f"Screen: {pyautogui.size()}")
    print(f"Mouse: {pyautogui.position()}")
    print("hands.py ready.")
