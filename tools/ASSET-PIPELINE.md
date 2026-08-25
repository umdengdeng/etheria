# 무엇으로 뽑는가 — 에셋 생성 경로 (2026-08-25 정리)

> ★**캐릭터와 배경은 다른 도구로 뽑는다.** 이걸 헷갈리면 얼굴이 매번 달라진다.
> 2026-08-25에 세레니아를 Grok 으로 뽑았다가 지적받고 정리한 문서다.

| 대상 | 도구 | 왜 |
|---|---|---|
| ★**캐릭터 · 인물** | **ComfyUI (로컬)** | **seed 고정**으로 같은 얼굴이 계속 나온다. 웹 도구는 이게 안 된다 |
| 배경 · 풍경 | Grok Imagine (웹) | 인물이 없으면 seed 고정이 필요 없다. 빠르고 16:9 가 편하다 |
| 콘티·검토용 | Firefly (웹) | 실사 화풍이라 게임 에셋으로는 안 쓴다. 판단용으로만 |

---

## 캐릭터 = ComfyUI

**설치 위치:** `D:\ComfyUI_windows_portable`
**띄우기:** `run_nvidia_gpu.bat` (API 는 `http://127.0.0.1:8188/prompt`)

**★본체 스크립트: `D:\ComfyUI_windows_portable\heroine_gen.py`**
「히로인 캐릭터 일관성 생성기 (v3): 얼굴+몸매+seed 고정, 의상/표정만 변경」

### 고정값

| 항목 | 값 |
|---|---|
| 체크포인트 | **`prefectIllustriousXL_v70.safetensors`** |
| 해상도 | 832 x 1216 (세로) |
| 샘플러 | `euler_ancestral` / `normal` |
| steps / cfg | 30 / 5.0 (FaceDetailer 2차 24 / 5.0) |
| 얼굴 보정 | **FaceDetailer** (Impact Pack) |

### 구조 — 캐릭터마다 락(lock)이 걸려 있다

```
CHARS[캐릭터] = { seed, facebody, signature, neg }
OUTFIT[캐릭터] = 의상 문장
EXPR[표정]     = 표정 문장   (neutral/smile/blush/sad/surprised/worried/angry/cold/smirk)
```
**seed 와 facebody 는 절대 안 건드린다. 바꾸는 건 의상과 표정뿐이다.**

### ★세레니아 · 소연 — **같은 seed 를 쓴다**

```
soyeon  : seed 515150
serenia : seed 515150      ← 같다
```
스크립트 주석 그대로:
> 소연 — 세레니아와 **'얼굴 완전 동일', 눈색만 다름(갈색).** 현대·성인 여성.

| | 세레니아 | 소연 |
|---|---|---|
| seed | **515150** | **515150** |
| 머리 | 검고 긴 생머리 | 검고 긴 생머리 |
| **눈** | **crimson red** | **warm dark brown** |
| 공통 | 왼쪽 볼에 옅은 보조개 · 갸름하고 단정한 이목구비 · 「눈이 반달로 접히는」 미소 |
| 의상 | 목까지 여민 흰·연금 로열 가운, 은실 자수, 얇은 은관 | 현대 캐주얼 |

★**「소연 = 세레니아 닮은꼴」은 설정만이 아니라 실제 생성 방식이다.**
같은 seed 로 뽑고 눈색만 바꾼다. 이걸 모르면 얼굴이 안 맞는다.

★세레니아 전용 네거티브에 **노출 금지가 박혀 있다** —
`cleavage, exposed chest, revealing clothes, plunging neckline, bare shoulders, seductive pose`
공주는 노출시키지 않는다는 게 못박힌 규칙이다.

### 쓰는 법

```powershell
# 1) ComfyUI 를 먼저 띄운다
D:\ComfyUI_windows_portable\run_nvidia_gpu.bat

# 2) 스크립트 맨 아래 분기에서 원하는 작업을 고른다
python D:\ComfyUI_windows_portable\heroine_gen.py <모드>
#   gen(파일명, 캐릭터id, OUTFIT[..], expr="neutral", view=.., bg=..)
#   gen_set(접두어, 캐릭터id, OUTFIT[..])   ← 표정 6종 일괄

# 3) 결과: D:\ComfyUI_windows_portable\ComfyUI\output\
```

---

## 배경 = Grok Imagine (웹)

- 크롬 탭이 늘 열려 있다. `tools/ui-map.json` 에 좌표.
- 비율은 **16:9** 로 맞춰둘 것.
- 결과 목록 화면의 **하단 입력창**을 쓴다. 상세 화면의 입력창은 「이미지 편집」이라 새로 안 뽑힌다.
- 사이드바 「새로운 생성」은 결과 화면에서 안 먹는다. 초기화하려면 주소창에 `grok.com/imagine`.
- 프롬프트: **장면을 먼저, 화풍은 뒤에.** 스타일을 앞에 길게 쓰면 소재가 묻힌다.
- 한글 프롬프트가 잘 먹지만 **반드시 클립보드로 붙여넣는다** (`typewrite` 는 한글이 깨진다).

---

## 넣고 나서

```bash
python tools/import_image.py <파일> <배경키> --tool "..." --model "..." --ratio "16:9"
node tools/check.js        # 키·방치에셋·대사↔그림 대조
python tools/vcheck.py     # 연출(대칭·구도·명암)
```
`--tool/--model` 을 안 주면 나중에 톤을 못 맞춘다. `tools/asset-history.json` 에 쌓인다.

> 2026-08-25 교훈: 히스토리를 만들기 **전에** 뽑은 원본은 프롬프트가 안 남아 있어서,
> 나중에 자세를 맞추려고 원본 이미지를 보고 역산해야 했다. 기록은 반드시 남긴다.
