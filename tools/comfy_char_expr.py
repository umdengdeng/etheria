# -*- coding: utf-8 -*-
"""캐릭터 표정 세트 생성기 (2026-08-26)

    python gen_char_expr.py serenia
    python gen_char_expr.py serenia sad worried
    python gen_char_expr.py serenia --outfit bold

무엇을 하나
    heroine_gen.py 의 **캐릭터 락(seed / facebody)** 을 그대로 쓰고
    표정만 바꿔서 대사용 스프라이트를 한 번에 뽑는다.
    seed 가 고정이라 표정이 달라져도 같은 사람으로 보인다 — 그게 이 파이프라인의 전부다.

★건드리면 안 되는 것
    SEED · FACEBODY. 이게 캐릭터의 정체성이다.
    소연과 세레니아가 같은 seed(515150)를 쓰는 것도 여기에 걸려 있다.

의상은 장면 파라미터라 바꿔도 얼굴이 안 흔들린다. --outfit 으로 고른다.
"""
import json, urllib.request, time, os, glob, shutil, sys

API = "http://127.0.0.1:8188/prompt"
OUT = r"D:\ComfyUI_windows_portable\ComfyUI\output"
DEST = r"C:\Users\umdeng\Desktop\게임제작\dating-sim\.shots\expr"

CKPT = {"class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": "prefectIllustriousXL_v70.safetensors"}}

# ── 캐릭터 락 (heroine_gen.py 에서 옮겨온 것) ────────────────────────
CHARS = {
 "serenia": dict(
   seed=515150,
   facebody=("1girl, solo, beautiful young princess age 22, very long straight glossy black hair, "
             "black hair, fair skin, crimson red eyes, small delicate nose, "
             "a faint dimple on the left cheek, refined elegant symmetrical features, "
             "graceful figure, medium breasts"),
   neg=""),
 "soyeon": dict(
   seed=515150,          # ★세레니아와 같은 seed. 얼굴 동일, 눈색만 다름
   facebody=("1girl, solo, beautiful elegant young woman age 23, very long straight glossy black hair, "
             "black hair, fair skin, warm dark brown eyes, small delicate nose, "
             "a faint dimple on the left cheek, refined elegant mature features, graceful figure"),
   neg="red eyes, crimson eyes, fantasy, elf ears, armor, medieval, tiara"),
}

# ── 의상 (장면 파라미터. 얼굴에 영향 없음) ──────────────────────────
OUTFITS = {
 # 원래 락에 있던 정숙한 로열 가운
 "modest": ("white royal gown, turtleneck, high collar, long sleeves, covered shoulders, "
            "silver embroidery, tiara, elegant, modest"),
 # ★노출을 올린 버전 (2026-08-26 유저 요청). 락의 정숙 규칙을 이 의상에서만 푼다
 "bold":   ("elegant white dress, off-shoulder, bare shoulders, sleeveless, deep neckline, "
            "cleavage, thin sheer layered fabric, silver embroidery, tiara, "
            "slit skirt, graceful and alluring"),
}
# 의상별로 풀거나 걸어야 하는 네거티브가 다르다
OUTFIT_NEG = {
 "modest": ("cleavage, exposed chest, revealing clothes, plunging neckline, bare shoulders, "
            "off-shoulder, strapless, sleeveless, bare arms"),
 "bold":   ("turtleneck, high collar, fully covered, nude, nipples, topless, bottomless, "
            "explicit, genitals"),
}

# ── 표정 (대사에서 부를 이름 그대로) ────────────────────────────────
EXPR = {
 "neutral":  "calm neutral expression, soft steady gaze, lips gently closed",
 "smile":    "warm gentle smile, eyes curving into soft crescents",
 "sad":      "sad sorrowful expression, tears welling in her eyes, eyebrows lowered, closed mouth",
 "blush":    "shy bashful expression, faint pink blush on cheeks, eyes slightly averted",
 "surprise": "surprised expression, widened eyes, slightly parted lips, raised brows",
 "worried":  "worried anxious expression, furrowed brows, uneasy downcast eyes",
}
DEFAULT_SET = ["neutral", "smile", "sad", "blush", "surprise", "worried"]

VIEW = ("solo, full body, facing viewer, front view, straight-on, arms down at her sides, "
        "looking at viewer, standing on nothing, no ground")
BG = ("flat vivid green background, solid bright green backdrop, chroma key green screen, "
      "simple background, no shadow, soft even lighting")
BASE_NEG = ("multiple views, reference sheet, character sheet, turnaround, multiple girls, 2girls, "
            "extra person, deformed, bad anatomy, bad hands, extra digits, watermark, signature, text, "
            "figurine, figure, pedestal, display stand, display base, statue, doll, showcase, floor, ground, shadow on ground, cropped head, cropped hair, out of frame, close-up, lowres, blurry, windswept hair, green clothes, green tint on skin, green hair, "
            "gold trim, red gem, colored accessory")


def build(cid, expr_key, outfit_key):
    c = CHARS[cid]
    P = ("masterpiece, best quality, amazing quality, %s, %s, %s, %s, %s"
         % (c["facebody"], OUTFITS[outfit_key], VIEW, BG, EXPR[expr_key]))
    N = BASE_NEG + ", " + OUTFIT_NEG[outfit_key] + ((", " + c["neg"]) if c["neg"] else "")
    seed = c["seed"]
    wf = {
     "c": CKPT,
     "pos": {"class_type": "CLIPTextEncode", "inputs": {"text": P, "clip": ["c", 1]}},
     "neg": {"class_type": "CLIPTextEncode", "inputs": {"text": N, "clip": ["c", 1]}},
     # ★가로를 넓혔다. 머리가 옆으로 퍼져서 832 폭에선 항상 잘렸다
     "lat": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1216, "batch_size": 1}},
     "ks": {"class_type": "KSampler", "inputs": {
        "model": ["c", 0], "positive": ["pos", 0], "negative": ["neg", 0], "latent_image": ["lat", 0],
        "seed": seed, "steps": 30, "cfg": 5.0,
        "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0}},
     "dec": {"class_type": "VAEDecode", "inputs": {"samples": ["ks", 0], "vae": ["c", 2]}},
     "ult": {"class_type": "UltralyticsDetectorProvider", "inputs": {"model_name": "bbox/face_yolov8m.pt"}},
     "sam": {"class_type": "SAMLoader", "inputs": {"model_name": "sam_vit_b_01ec64.pth", "device_mode": "AUTO"}},
    }
    wf["fd"] = {"class_type": "FaceDetailer", "inputs": {
        "image": ["dec", 0], "model": ["c", 0], "clip": ["c", 1], "vae": ["c", 2],
        "positive": ["pos", 0], "negative": ["neg", 0],
        "bbox_detector": ["ult", 0], "sam_model_opt": ["sam", 0],
        "guide_size": 512.0, "guide_size_for": True, "max_size": 1024.0,
        "seed": seed + 1, "steps": 24, "cfg": 5.0,
        "sampler_name": "euler_ancestral", "scheduler": "normal",
        "denoise": 0.30, "feather": 5, "noise_mask": True, "force_inpaint": True,
        "bbox_threshold": 0.5, "bbox_dilation": 10, "bbox_crop_factor": 3.0,
        "sam_detection_hint": "center-1", "sam_dilation": 0, "sam_threshold": 0.93,
        "sam_bbox_expansion": 0, "sam_mask_hint_threshold": 0.7,
        "sam_mask_hint_use_negative": "False", "drop_size": 10, "wildcard": "", "cycle": 1}}
    wf["save"] = {"class_type": "SaveImage",
                  "inputs": {"images": ["fd", 0], "filename_prefix": "expr_%s_%s" % (cid, expr_key)}}
    return wf


def run(cid, expr_key, outfit_key):
    pat = os.path.join(OUT, "expr_%s_%s*.png" % (cid, expr_key))
    before = set(glob.glob(pat))
    data = json.dumps({"prompt": build(cid, expr_key, outfit_key)}).encode()
    req = urllib.request.Request(API, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req).read()
    except Exception as e:
        print("[%s] 요청 실패: %s" % (expr_key, e), flush=True); return
    for _ in range(200):
        time.sleep(2)
        new = set(glob.glob(pat)) - before
        if new:
            f = sorted(new)[-1]
            if os.path.getsize(f) > 0:
                time.sleep(1)
                os.makedirs(DEST, exist_ok=True)
                dst = os.path.join(DEST, "%s_%s.png" % (cid, expr_key))
                shutil.copy(f, dst)
                print("[%s] %s" % (expr_key, dst), flush=True); return
    print("[%s] 시간 초과" % expr_key, flush=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    outfit = "modest"
    if "--outfit" in sys.argv:
        outfit = sys.argv[sys.argv.index("--outfit") + 1]
        args = [a for a in args if a != outfit]
    cid = args[0] if args else "serenia"
    exprs = args[1:] or DEFAULT_SET
    print("%s · 의상 %s · 표정 %s" % (cid, outfit, ",".join(exprs)), flush=True)
    for e in exprs:
        run(cid, e, outfit)
    print("끝", flush=True)
