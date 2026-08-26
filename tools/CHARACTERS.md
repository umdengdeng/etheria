# 캐릭터 · 표정 자산 장부 (2026-08-26)

> 대사마다 얼굴을 바꿔 쓰려면 **누가 어떤 표정을 갖고 있는지**를 알아야 한다.
> 이 문서 + `tools/sprite-registry.json` 이 그 장부다.
> 재생성: `node tools/check.js` 가 부족한 표정을 알려준다.

---

## 표준 표정 6종

대사에서 부르는 이름이 곧 파일 이름이다.

| 이름 | 언제 쓰나 |
|---|---|
| `neutral` | 기본. 설명하거나 담담할 때 |
| `smile` | 호감·안도·농담 |
| `sad` | 미안함·상실. **울지는 않는다** |
| `blush` | 부끄러움·호감 상승 순간 |
| `surprise` | 예상 못 한 정보·기습 |
| `worried` | 불안·망설임 |

*(추가로 `angry` `smug` `shy` 는 엘리아나만 갖고 있다. 필요해지면 그때 뽑는다.)*

## 보유 현황

| 캐릭터 | 갖고 있는 표정 | 없는 것 |
|---|---|---|
| **serenia** | neutral · smile · sad · blush · surprise · worried | — **완비** |
| **eliana** | neutral · smile · blush · surprise · angry · smug · shy | `sad` `worried` |
| soyeon | (실루엣 전용 1장) | 표정 세트 없음. **얼굴을 안 보여주는 게 설정**이라 필요 없다 |

---

## 대사에서 쓰는 법

```js
{sp:"serenia_sad", name:"세레니아", text:"…미안해요."}
{sp:"neutral",      name:"엘리아나", text:"이름."}      // 엘리아나는 접두어 생략 가능
```

`setSp()` 가 `SPR["eliana_"+k] || SPR[k]` 순으로 찾는다.
→ **엘리아나만 짧은 이름이 되고, 나머지는 `캐릭터_표정` 전체 이름을 준다.**

**실루엣으로 세울 때** — `silh:1` 을 같이 준다. 검은 실루엣이 되고,
암전(`fx.void`) 위에서는 자동으로 빛나는 역광 실루엣이 된다.
```js
{sp:"soyeon", silh:1, narr:1, text:"― 흐릿한 잔상 하나가 명멸한다."}
```

---

## 새로 뽑는 법

```powershell
D:\ComfyUI_windows_portable\run_nvidia_gpu.bat            # 먼저 띄운다

# 표정 세트 한 번에 (기본 6종)
python D:\ComfyUI_windows_portable\gen_char_expr.py serenia
python D:\ComfyUI_windows_portable\gen_char_expr.py serenia sad worried   # 일부만
python D:\ComfyUI_windows_portable\gen_char_expr.py serenia --outfit bold # 의상 교체
```
```bash
# 흰 배경을 지워 스프라이트로 등록
python tools/import_sprite.py .shots/expr/serenia_sad.png
node tools/check.js
```

### ★전신으로 뽑아서 상반신으로 자른다

```bash
python tools/import_sprite.py .shots/expr/serenia_sad.png --upper
```

상반신으로 **직접** 뽑으면 이 모델은 인물로 프레임을 꽉 채워서 **머리카락이 잘린다.**
전신으로 뽑아야 여백이 생기고, 자르는 건 `--upper` 가 계산으로 한다.

같이 걸어야 하는 네거티브 — `figurine, pedestal, display stand, statue, floor, ground`
「전신이 다 들어오게」라고 쓰면 모델이 **진열대 위 피규어**를 그린다. 실제로 그랬다.

### 표정마다 얼굴이 달라질 때

**FaceDetailer 의 `denoise` 를 낮춘다.** 0.45 는 얼굴을 **다시 그려서** 눈매까지 바뀐다.
**0.30** 이면 다듬기만 하고 원래 얼굴을 유지한다.
표정 문장도 **짧게, 프롬프트 맨 뒤에** 붙인다 — 앞에 길게 넣으면 구도까지 흔든다.

### 규칙

- ★**seed 와 facebody 는 절대 안 건드린다.** 이게 캐릭터의 정체성이다.
  표정과 의상만 파라미터다. (세레니아 seed = **515150**, 소연과 같다)
- 의상은 `OUTFITS` 에서 고른다 — `modest`(정숙한 로열 가운) / `bold`(노출 있는 드레스, 2026-08-26 확정)
- 뽑고 나면 **눈으로 볼 것.** 노출 금지 네거티브가 뚫리거나 옷 무늬가 표정마다 달라지는 일이 있다

### ★배경은 **초록(크로마키)** 으로 뽑는다 — 네 번 틀리고 정착한 결론

`gen_char_expr.py` 의 `BG` 가 초록인 이유다. 흰 배경으로 뽑으면 안 된다.

| 시도 | 방법 | 왜 실패했나 |
|---|---|---|
| ① | 「밝으면 배경」(임계 232) | **흰 드레스가 통째로 뚫렸다** |
| ② | 테두리에서 flood fill | 머리카락 사이 **갇힌 흰 구멍이 남고**, 치마 밑단은 아래 테두리와 이어져 **거꾸로 파먹혔다** |
| ③ | 순백과의 거리 | 갇힌 구멍은 지워졌는데 **비치는 흰 소매가 배경과 색이 똑같아서** 같이 지워졌다 |
| ④ | **초록 배경 + 크로마키** | ✅ 인물 팔레트가 흰·검정·붉은 눈뿐이라 초록과 절대 안 겹친다 |

★**흰 배경 + 흰 옷은 색으로 나누는 게 원리적으로 불가능하다.** 그래서 배경을 바꾼 것이다.

**despill(초록물 빼기) 주의** — 초록이 `R·B 평균`을 넘을 때 깎으면 **피부가 보랏빛이 된다.**
피부는 R > G > B 라 평균보다 늘 높기 때문이다. `R·B 중 큰 값`을 넘을 때만 깎아야 한다.
