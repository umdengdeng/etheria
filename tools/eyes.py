"""
eyes.py - 화면 캡쳐/분석 (GameForge/agent/eyes.py 에서 가져옴)
capture_full(), capture_region(), crop(), diff(), wait_for_change(), find_on_screen(), read_text()
"""

import os
import time
from datetime import datetime

import pyautogui
from PIL import Image, ImageChops

CAPTURE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".shots")


def _stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def capture_full(name="screen"):
    """전체 화면 캡쳐. 경로를 돌려준다."""
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    path = os.path.join(CAPTURE_DIR, f"{name}_{_stamp()}.png")
    pyautogui.screenshot().save(path)
    print(f"[EYES] 전체 캡쳐: {path}")
    return path


def capture_region(x, y, width, height, name="region"):
    """일부 영역만 캡쳐."""
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    path = os.path.join(CAPTURE_DIR, f"{name}_{_stamp()}.png")
    pyautogui.screenshot(region=(x, y, width, height)).save(path)
    print(f"[EYES] 영역 캡쳐 ({x},{y},{width},{height}): {path}")
    return path


def shrink(image_path, width=1280, name="small"):
    """분석용 축소본. 큰 스샷을 그대로 보면 느리다."""
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    img = Image.open(str(image_path))
    if img.width <= width:
        return str(image_path)
    h = int(img.height * width / img.width)
    out = os.path.join(CAPTURE_DIR, f"{name}_{_stamp()}.png")
    img.resize((width, h), Image.LANCZOS).save(out)
    print(f"[EYES] 축소본: {out} ({width}x{h}, 배율 {img.width/width:.3f})")
    return out


def crop(image_path, x, y, w, h, save_name=None):
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    img = Image.open(str(image_path))
    out = os.path.join(CAPTURE_DIR, f"{save_name or 'crop'}_{_stamp()}.png")
    img.crop((x, y, x + w, y + h)).save(out)
    print(f"[EYES] 잘라냄: {out} ({w}x{h})")
    return out


def diff(image_path_a, image_path_b):
    """두 캡쳐의 변화율(%)."""
    a = Image.open(str(image_path_a)).convert("RGB")
    b = Image.open(str(image_path_b)).convert("RGB")
    if a.size != b.size:
        b = b.resize(a.size)
    d = ImageChops.difference(a, b)
    pixels = list(d.getdata())
    changed = sum(1 for p in pixels if sum(p) > 30)
    pct = changed / len(pixels) * 100
    print(f"[EYES] 변화율 {pct:.2f}%")
    return pct


def wait_for_change(region=None, timeout=60, interval=1.0, threshold=2.0):
    """화면이 바뀔 때까지 기다린다. 이미지 생성 완료 감지용."""
    before = capture_full() if region is None else capture_region(*region)
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(interval)
        after = capture_full() if region is None else capture_region(*region)
        if diff(before, after) >= threshold:
            print(f"[EYES] 변화 감지 ({time.time()-start:.1f}초)")
            return True
    print(f"[EYES] {timeout}초 동안 변화 없음")
    return False


def find_on_screen(image_template, confidence=0.8):
    """템플릿 이미지를 화면에서 찾는다. (x,y,w,h) 또는 None."""
    try:
        loc = pyautogui.locateOnScreen(str(image_template), confidence=confidence)
        if loc:
            print(f"[EYES] 찾음: {loc}")
            return loc
    except Exception as e:
        print(f"[EYES] 템플릿 탐색 오류: {e}")
    return None


def read_text(image_path, lang="kor+eng"):
    """OCR. pytesseract 가 있어야 한다."""
    try:
        import pytesseract
        text = pytesseract.image_to_string(Image.open(str(image_path)), lang=lang)
        print(f"[EYES] OCR {len(text)}자")
        return text.strip()
    except Exception as e:
        print(f"[EYES] OCR 오류: {e}")
        return ""


if __name__ == "__main__":
    p = capture_full()
    print(shrink(p))
