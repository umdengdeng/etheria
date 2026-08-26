# -*- coding: utf-8 -*-
"""세레니아 「부름」 컷 — 1화 오프닝 전용 (2026-08-25)

    python gen_serenia_call.py            # 4컷 전부
    python gen_serenia_call.py close      # 하나만

왜 따로 만들었나
    heroine_gen.py 의 gen() 은 832x1216 세로 고정에 배경도 회색 스튜디오다.
    오프닝은 **가로 16:9 · 새하얀 빈 공간 · 이쪽으로 손을 내미는 자세**가 필요하다.
    그래서 캐릭터 락(seed/facebody/neg/의상)은 heroine_gen.py 것을 그대로 가져오고
    해상도와 view/bg 만 이 장면에 맞춰 바꿨다.

★건드리면 안 되는 것
    seed 515150 · facebody · 세레니아 네거티브(노출 금지).
    이게 소연과 같은 얼굴을 만드는 장치다. 바꾸면 닮은꼴이 깨진다.
"""
import json, urllib.request, time, os, glob, shutil, sys

API = "http://127.0.0.1:8188/prompt"
OUT = r"D:\ComfyUI_windows_portable\ComfyUI\output"
DEST = r"C:\Users\umdeng\Desktop\게임제작\dating-sim\.shots\comfy"

CKPT = {"class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": "prefectIllustriousXL_v70.safetensors"}}

# ── heroine_gen.py 의 serenia 락을 그대로 옮겨온 것 ──────────────────
SEED = 515150            # ★소연과 같은 seed. 이게 「같은 얼굴」의 정체다
FACEBODY = ("1girl, solo, beautiful young princess age 22, very long straight glossy black hair, black hair, "
            "fair skin with a soft warm healthy tone, crimson red eyes, small delicate nose, "
            "a faint dimple on the left cheek, refined elegant symmetrical features, "
            "graceful figure, medium breasts, serene noble gentle demeanor")
# ★이 모델(Illustrious)은 **부루 태그**로 알아듣는다. 긴 영어 문장은 거의 무시되고
#   대신 엉뚱한 단어만 문자 그대로 그린다 — 「camera」라고 썼더니 REC 뷰파인더를 그렸다.
#   그래서 전부 짧은 태그로 쓴다.
OUTFIT = ("flowing white robe, sheer gauzy layered fabric, high collar, long wide sleeves, "
          "covered shoulders, tiara, plain, elegant")
CHAR_NEG = ("cleavage, exposed chest, revealing clothes, plunging neckline, bare shoulders, off-shoulder, "
            "strapless, sleeveless, bare arms, collarbone, bare chest, seductive pose")
BASE_NEG = ("red clothes, red sash, red ribbon, gold ornament, colored accessory, necklace, pendant, brooch, ball gown, wedding dress, long train, trailing skirt, wide skirt, poofy dress, full body, feet, shoes, multicolored hair, gradient hair, streaked hair, red hair, colored hair tips, two-tone hair, viewfinder, rec, recording indicator, frame border, letterbox, ui, hud, battery icon, "
            "closed eyes, eyes closed, twintails, earrings, jewelry, "
            "giant hand, oversized hand, smug, smirk, grin, angry, glaring, "
            "multiple views, reference sheet, character sheet, turnaround, front and back view, multiple girls, 2girls, extra person, deformed, bad anatomy, bad hands, extra digits, "
            "watermark, signature, text, cropped head, out of frame, muscular, old, child, lowres, blurry")

# 백색 공간
VOID = "white background, simple background, empty background, no shadow, soft lighting, pale"

# ★부르는 자세 — 태그로
CALL = "reaching towards viewer, outstretched arm, open palm, looking at viewer, one hand raised"
NO_TPOSE = "spread arms, t-pose, symmetrical pose, both arms outstretched, "

CUTS = {
  "grabA": dict(
    expr="sad, desperate, open eyes, looking at viewer, parted lips",
    view="cowboy shot, outstretched hand, reaching towards viewer, grabbing motion, fingers curled, clawed hand, leaning forward, off balance, shoulder pulled forward, other arm trailing behind, hair flowing backwards, clothes flowing backwards, dynamic pose, foreshortening, looking at viewer, desperate, straining",
    extra_neg=NO_TPOSE + "full body, feet, close-up, open palm, relaxed, standing still, calm pose",
    detail=True, hands=True, portrait=True),

  "grabB": dict(
    expr="sad, desperate, open eyes, looking at viewer, parted lips",
    view="cowboy shot, outstretched hand, reaching towards viewer, grabbing motion, fingers curled, clawed hand, leaning forward, off balance, shoulder pulled forward, other arm trailing behind, hair flowing backwards, clothes flowing backwards, dynamic pose, foreshortening, looking at viewer, desperate, straining, lunging forward, one foot lifted, falling towards viewer, motion blur",
    extra_neg=NO_TPOSE + "full body, feet, close-up, open palm, relaxed, standing still, calm pose",
    detail=True, hands=True, portrait=True),

  "grabC": dict(
    expr="sad, desperate, open eyes, looking at viewer, parted lips",
    view="cowboy shot, outstretched hand, reaching towards viewer, grabbing motion, fingers curled, clawed hand, leaning forward, off balance, shoulder pulled forward, other arm trailing behind, hair flowing backwards, clothes flowing backwards, dynamic pose, foreshortening, looking at viewer, desperate, straining, hand in front of face, extreme foreshortening, hand reaching out of frame",
    extra_neg=NO_TPOSE + "full body, feet, close-up, open palm, relaxed, standing still, calm pose",
    detail=True, hands=True, portrait=True),

  "poseA": dict(
    expr="sad, apologetic, open eyes, looking at viewer, closed mouth",
    view="cowboy shot, leaning forward, reaching towards viewer, outstretched arm, open palm, head tilt, head down, looking up, upturned eyes, from below",
    extra_neg=NO_TPOSE + "full body, feet, legs, close-up",
    detail=True, hands=True, portrait=True),

  "poseB": dict(
    expr="sad, apologetic, open eyes, looking at viewer, closed mouth",
    view="cowboy shot, floating, weightless, hair floating upwards, clothes floating, wide sleeves billowing, reaching towards viewer, outstretched arm, open palm, looking at viewer, from below",
    extra_neg=NO_TPOSE + "full body, feet, legs, close-up",
    detail=True, hands=True, portrait=True),

  "poseC": dict(
    expr="sad, apologetic, open eyes, looking at viewer, closed mouth",
    view="cowboy shot, dutch angle, reaching towards viewer, outstretched arm across the frame, open palm, foreshortening, upper body turned away, looking back at viewer, over the shoulder",
    extra_neg=NO_TPOSE + "full body, feet, legs, close-up",
    detail=True, hands=True, portrait=True),

  # ★전신이 아니라 카우보이샷(허벅지 위). 전신은 얼굴에 갈 픽셀이 없어서 눈·코가 뭉갠다.
  #   그리고 세로(832x1216)로 뽑는다 — 이 모델이 학습한 비율이라 인물이 크게 잡힌다.
  #   배경이 순백이라 뒤에서 16:9 흰 캔버스에 얹으면 이음매가 안 보인다.
  "wide": dict(
    expr="sad, apologetic, open eyes, looking at viewer, closed mouth",
    view="cowboy shot, " + CALL,
    extra_neg=NO_TPOSE + "full body, feet, legs, close-up",
    detail=True, hands=True, portrait=True),

  "close": dict(
    expr="sad, apologetic, half-closed eyes, closed mouth",
    view="upper body, from below, " + CALL,
    extra_neg=NO_TPOSE + "full body, wide shot",
    detail=True, hands=True),

  "mid": dict(
    expr="face obscured by light",
    view="full body, silhouette, backlighting, overexposed, glowing, blurry, " + CALL,
    extra_neg=NO_TPOSE + "detailed face, sharp focus",
    detail=False),

  "dissolve": dict(
    expr="dissolving, disintegrating",
    view="full body, dissolving into light particles, glowing motes, backlighting, overexposed, ethereal",
    extra_neg=NO_TPOSE + "detailed face, sharp focus, intact body",
    detail=False),
}


def build(name, cut):
    P = (f"masterpiece, best quality, amazing quality, {FACEBODY}, {cut['expr']}, "
         f"{OUTFIT}, {cut['view']}, {VOID}")
    N = BASE_NEG + ", " + CHAR_NEG + ", " + cut["extra_neg"]
    wf = {
     "c": CKPT,
     "pos": {"class_type": "CLIPTextEncode", "inputs": {"text": P, "clip": ["c", 1]}},
     "neg": {"class_type": "CLIPTextEncode", "inputs": {"text": N, "clip": ["c", 1]}},
     # ★가로 16:9. SDXL 계열이라 1344x768 이 안전하다 (832x1216 의 가로판)
     # 세로 컷은 832x1216 — heroine_gen.py 가 쓰는 비율이고 얼굴에 픽셀이 제일 많이 간다.
     # 가로가 필요하면 뽑은 뒤 흰 캔버스에 얹는다 (배경이 순백이라 이음매가 없다).
     "lat": {"class_type": "EmptyLatentImage", "inputs": {
        "width": 832 if cut.get("portrait") else 1344,
        "height": 1216 if cut.get("portrait") else 768, "batch_size": 1}},
     "ks": {"class_type": "KSampler", "inputs": {
        "model": ["c", 0], "positive": ["pos", 0], "negative": ["neg", 0], "latent_image": ["lat", 0],
        "seed": SEED, "steps": 30, "cfg": 5.0,
        "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0}},
     "dec": {"class_type": "VAEDecode", "inputs": {"samples": ["ks", 0], "vae": ["c", 2]}},
    }
    img = ["dec", 0]
    if cut["detail"]:
        wf["ult"] = {"class_type": "UltralyticsDetectorProvider",
                     "inputs": {"model_name": "bbox/face_yolov8m.pt"}}
        wf["sam"] = {"class_type": "SAMLoader",
                     "inputs": {"model_name": "sam_vit_b_01ec64.pth", "device_mode": "AUTO"}}
        wf["fd"] = {"class_type": "FaceDetailer", "inputs": {
            "image": ["dec", 0], "model": ["c", 0], "clip": ["c", 1], "vae": ["c", 2],
            "positive": ["pos", 0], "negative": ["neg", 0],
            "bbox_detector": ["ult", 0], "sam_model_opt": ["sam", 0],
            "guide_size": 512.0, "guide_size_for": True, "max_size": 1024.0,
            "seed": SEED + 1, "steps": 24, "cfg": 5.0,
            "sampler_name": "euler_ancestral", "scheduler": "normal",
            "denoise": 0.45, "feather": 5, "noise_mask": True, "force_inpaint": True,
            "bbox_threshold": 0.5, "bbox_dilation": 10, "bbox_crop_factor": 3.0,
            "sam_detection_hint": "center-1", "sam_dilation": 0, "sam_threshold": 0.93,
            "sam_bbox_expansion": 0, "sam_mask_hint_threshold": 0.7,
            "sam_mask_hint_use_negative": "False", "drop_size": 10, "wildcard": "", "cycle": 1}}
        img = ["fd", 0]
    if cut.get("hands"):
        # ★손은 FaceDetailer(얼굴 디텍터)로 안 잡힌다. hand_yolov8s 로 한 번 더 태운다.
        #   전신샷에서 손가락이 뭉개지던 걸 이걸로 잡는다.
        wf["ulth"] = {"class_type": "UltralyticsDetectorProvider",
                      "inputs": {"model_name": "bbox/hand_yolov8s.pt"}}
        wf["hd"] = {"class_type": "FaceDetailer", "inputs": {
            "image": img, "model": ["c", 0], "clip": ["c", 1], "vae": ["c", 2],
            "positive": ["pos", 0], "negative": ["neg", 0],
            "bbox_detector": ["ulth", 0],
            "guide_size": 384.0, "guide_size_for": True, "max_size": 1024.0,
            "seed": SEED + 2, "steps": 24, "cfg": 5.0,
            "sampler_name": "euler_ancestral", "scheduler": "normal",
            "denoise": 0.5, "feather": 5, "noise_mask": True, "force_inpaint": True,
            "bbox_threshold": 0.5, "bbox_dilation": 10, "bbox_crop_factor": 3.0,
            "sam_detection_hint": "center-1", "sam_dilation": 0, "sam_threshold": 0.93,
            "sam_bbox_expansion": 0, "sam_mask_hint_threshold": 0.7,
            "sam_mask_hint_use_negative": "False", "drop_size": 10, "wildcard": "", "cycle": 1}}
        img = ["hd", 0]
    wf["save"] = {"class_type": "SaveImage",
                  "inputs": {"images": img, "filename_prefix": "sercall_" + name}}
    return wf


def run(name):
    cut = CUTS[name]
    pat = os.path.join(OUT, "sercall_" + name + "*.png")
    before = set(glob.glob(pat))
    data = json.dumps({"prompt": build(name, cut)}).encode()
    req = urllib.request.Request(API, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req).read()
    except Exception as e:
        print("[%s] 요청 실패: %s" % (name, e), flush=True)
        return None
    for _ in range(180):
        time.sleep(2)
        new = set(glob.glob(pat)) - before
        if new:
            f = sorted(new)[-1]
            if os.path.getsize(f) > 0:
                time.sleep(1)
                os.makedirs(DEST, exist_ok=True)
                dst = os.path.join(DEST, name + ".png")
                shutil.copy(f, dst)
                print("[%s] 완료 -> %s" % (name, dst), flush=True)
                return dst
    print("[%s] 시간 초과" % name, flush=True)
    return None


if __name__ == "__main__":
    names = sys.argv[1:] or ["wide", "close", "mid", "dissolve"]
    for n in names:
        run(n)
    print("끝", flush=True)
