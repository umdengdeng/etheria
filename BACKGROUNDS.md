# 에테리아 · 배경 라이브러리

`node tools/gen-doc.js` 로 생성됨. 직접 고치지 말고 `index.html` 의 `BG_LIB` 를 고칠 것.

배경은 **지역 → 장소 → 시점** 으로 관리한다. 키 예: `asra.rampart.rain`

- 새 배경은 `bgPrompt("키")` 로 프롬프트를 만들어 뽑는다. 지역 아트 디렉션이 앞에 붙어서 톤이 어긋나지 않는다.
- 씬에서는 `bg:"키"`. 없는 시점을 불러도 **같은 장소의 다른 시점 → 지역 기본** 순으로 대체되어 화면이 비지 않는다.
- **파일 이름을 믿지 말 것.** `forest_beast` 에는 마수가 없고 `asra_castle` 은 성 외관이 아니라 알현실이었다. 매핑 전에 이미지를 직접 열어볼 것.
- 고치고 나면 `node tools/check.js` 로 정합성 검사.

## 시점 어휘

| 구분 | 코드 |
|---|---|
| 카메라 | `wide` 원경 · `mid` 기본 · `close` 근경 · `pov` 1인칭 · `vista` 조망 |
| 시간·날씨 | `day` · `night` · `dawn` 새벽 · `dusk` 해질녘 · `rain` 비 · `dim` 어둑 |
| 연출 | `ground` 지면 · `bush` 수풀너머 · `blur` 흐린시야 · `panic` 급박 · `shout` 외침 · `wake` 각성 · `beast` 조우 · `dissolve` 소멸 |

## 화면 톤

한 에피소드 안에서 톤이 갈리면 배경이 튄다. `tools/check.js` 가 이걸 잡는다.

`bright` 밝은 대낮 · `dim` 어둑·안개 · `night` 밤 · `autumn` 가을(갈색) · `indoor` 실내 · `white` 백색 · `flat` 무배경

## serenia — 세레니아 · 부름의 백색

> **아트 디렉션(고정)** — 경계 없는 백색 공간. 바닥도 천장도 지평선도 없다. 확산광만 존재해 그림자가 거의 생기지 않는다. 색은 흰빛·은빛·아주 옅은 하늘빛 세 가지로만 제한. 채도 극단적으로 낮게, 윤곽은 부드럽게 번지게. 원근을 알 수 있는 단서를 절대 넣지 말 것. 미세한 필름 그레인.

기본 배경(폴백): `bg_serenia_call`

| 키 | 장소 | 시점 | 톤 | 원본 에셋 | 상태 |
|---|---|---|---|---|---|
| `serenia.call.wide` | 부름이 일어나는 백색의 한가운데 | 원경 | 백색 | `serenia_call_wide` | 보유 |
| `serenia.call.mid` | 부름이 일어나는 백색의 한가운데 | 기본 | 백색 | `serenia_call_mid` | 보유 |
| `serenia.call.close` | 부름이 일어나는 백색의 한가운데 | 근경 | 백색 | `serenia_call_close` | 보유 |
| `serenia.call.dissolve` | 부름이 일어나는 백색의 한가운데 | 소멸 | 백색 | `serenia_call_dissolve` | 보유 |
| `serenia.call.pov` | 부름이 일어나는 백색의 한가운데 | 1인칭 | 백색 | — | **생성 대기** |
| `serenia.gate.wide` | 봉인된 문 | 원경 | 백색 | — | **생성 대기** |

## asra — 아스라 왕국

> **아트 디렉션(고정)** — 중세 북유럽풍 석조 왕국. 회청색 화강암과 짙은 남색 지붕, 포인트로만 금빛 문장. 하늘은 늘 옅은 구름이 낀 한랭한 톤. 광원은 낮게 깔린 태양 또는 횃불. 직선적이고 육중한 건축에 장식은 절제. 중간 채도, 명암 대비는 강하게.

기본 배경(폴백): `asra_rampart`

| 키 | 장소 | 시점 | 톤 | 원본 에셋 | 상태 |
|---|---|---|---|---|---|
| `asra.castle.wide` | 아스라 왕성 외관 | 원경 | 밝은 대낮 | `asra_castle_wide` | 보유 |
| `asra.castle.night` | 아스라 왕성 외관 | 밤 | 밤 | `asra_castle_night` | 보유 |
| `asra.castle.dawn` | 아스라 왕성 외관 | 새벽 | 밝은 대낮 | — | **생성 대기** |
| `asra.hall.mid` | 알현실 | 기본 | 실내 | `asra_castle` | 보유 |
| `asra.gate.mid` | 성 안쪽 아치 통로 | 기본 | 실내 | `asra_gate` | 보유 |
| `asra.gate.night` | 성 안쪽 아치 통로 | 밤 | 밤 | — | **생성 대기** |
| `asra.rampart.mid` | 성벽 순찰로 | 기본 | 밝은 대낮 | `asra_rampart_mid` | 보유 |
| `asra.rampart.night` | 성벽 순찰로 | 밤 | 밤 | `asra_rampart_night` | 보유 |
| `asra.rampart.rain` | 성벽 순찰로 | 비 | 어둑·안개 | `asra_rampart_rain` | 보유 |
| `asra.training.mid` | 기사단 훈련장 | 기본 | 실내 | `asra_training_mid` | 보유 |
| `asra.training.dusk` | 기사단 훈련장 | 해질녘 | 어둑·안개 | — | **생성 대기** |
| `asra.market.mid` | 성 아랫마을 장터 | 기본 | 밝은 대낮 | — | **생성 대기** |
| `asra.mine.mid` | 버려진 광산 | 기본 | 밤 | `asra_mine_mid` | 보유 |
| `asra.mine.close` | 버려진 광산 | 근경 | 밤 | `asra_mine_close` | 보유 |
| `asra.orchard.mid` | 왕립 과수원 | 기본 | 밝은 대낮 | `asra_orchard_mid` | 보유 |
| `asra.orchard.dusk` | 왕립 과수원 | 해질녘 | 어둑·안개 | `asra_orchard_dusk` | 보유 |

## sylvarn — 실바른 숲 일대

> **아트 디렉션(고정)** — 습한 온대 활엽수림. 계절은 한여름이라 잎이 무성하고 바닥까지 초록 이끼가 덮여 있다. 낙엽이 쌓인 가을 풍경이 아니다. 짙은 녹청과 이끼빛이 지배색, 흙은 적갈색. 나뭇잎 사이로 떨어지는 산광과 공기 중 부유물, 늘 옅게 깔린 안개.

기본 배경(폴백): `forest_edge`

| 키 | 장소 | 시점 | 톤 | 원본 에셋 | 상태 |
|---|---|---|---|---|---|
| `sylvarn.edge.wide` | 실바른 숲 가장자리 | 원경 | 밝은 대낮 | `sylvarn_edge_wide` | 보유 |
| `sylvarn.edge.mid` | 실바른 숲 가장자리 | 기본 | 밝은 대낮 | `sylvarn_edge_mid` | 보유 |
| `sylvarn.edge.night` | 실바른 숲 가장자리 | 밤 | 밤 | — | **생성 대기** |
| `sylvarn.deep.wide` | 숲 속 깊은 곳 | 원경 | 밝은 대낮 | `forest2` | 보유 |
| `sylvarn.deep.mid` | 숲 속 깊은 곳 | 기본 | 밝은 대낮 | `forest_in` | 보유 |
| `sylvarn.deep.bush` | 숲 속 깊은 곳 | 수풀 너머 | 밝은 대낮 | `sylvarn_deep_bush` | 보유 |
| `sylvarn.deep.blur` | 숲 속 깊은 곳 | 흐린 시야 | 밝은 대낮 | `sylvarn_deep_blur` | 보유 |
| `sylvarn.deep.panic` | 숲 속 깊은 곳 | 급박 | 밝은 대낮 | `sylvarn_deep_panic` | 보유 |
| `sylvarn.deep.wake` | 숲 속 깊은 곳 | 각성 | 밝은 대낮 | `sylvarn_deep_wake` | 보유 |
| `sylvarn.deep.beast` | 숲 속 깊은 곳 | 조우 | 밝은 대낮 | `giantrat` | 보유 |
| `sylvarn.deep.tracks` | 숲 속 깊은 곳 | 흔적 | 밝은 대낮 | `sylvarn_deep_tracks` | 보유 |
| `sylvarn.deep.goblin` | 숲 속 깊은 곳 | 무리 | 밝은 대낮 | `sylvarn_deep_goblin` | 보유 |
| `sylvarn.deep.ground` | 숲 속 깊은 곳 | 지면 시점 | 가을(갈색) | `sylvarn_deep_ground` | 보유 |
| `sylvarn.deep.vista` | 숲 속 깊은 곳 | 조망 | 어둑·안개 | `sylvarn_deep_vista` | 보유 |
| `sylvarn.deep.dusk` | 숲 속 깊은 곳 | 해질녘 | 어둑·안개 | `forest_beast` | 보유 |
| `sylvarn.deep.shout` | 숲 속 깊은 곳 | 외침 | 어둑·안개 | `forest_shout` | 보유 |
| `sylvarn.deep.night` | 숲 속 깊은 곳 | 밤 | 밤 | — | **생성 대기** |
| `sylvarn.pond.mid` | 숲속 연못 | 기본 | 밝은 대낮 | `pond_face` | 보유 |
| `sylvarn.pond.close` | 숲속 연못 | 근경 | 밝은 대낮 | `sylvarn_pond_close` | 보유 |
| `sylvarn.pond.dawn` | 숲속 연못 | 새벽 | 어둑·안개 | — | **생성 대기** |
| `sylvarn.rift.wide` | 마수 사냥터의 균열 | 원경 | 밤 | `sylvarn_rift_wide` | 보유 |
| `sylvarn.rift.close` | 마수 사냥터의 균열 | 근경 | 밤 | `sylvarn_rift_close` | 보유 |

## modern — 현실 · 한국

> **아트 디렉션(고정)** — 현대 한국 도시. 형광등·모니터·가로등 같은 인공광만 쓰고 자연광은 넣지 않는다. 색온도는 차갑게(청록 기미), 대비는 나트륨등 주황으로만 준다. 좁고 답답한 프레이밍에 수직선 강조. 채도 낮게, 노이즈 약간.

기본 배경(폴백): `bg_home`

| 키 | 장소 | 시점 | 톤 | 원본 에셋 | 상태 |
|---|---|---|---|---|---|
| `modern.office.mid` | 야근 중인 사무실 | 기본 | 밤 | `bg_office` | 보유 |
| `modern.home.mid` | 혼자 사는 원룸 | 기본 | 밤 | `bg_home` | 보유 |
| `modern.home.dim` | 혼자 사는 원룸 | 어둑 | 밤 | `bg_floor` | 보유 |
| `modern.street.night` | 밤거리 | 밤 | 밤 | `bg_night_street` | 보유 |
| `modern.phone.close` | 손에 든 휴대폰 화면 | 근경 | 밤 | `bg_phone` | 보유 |

## fx — 연출용 · 무배경

> **아트 디렉션(고정)** — 실제 장소가 아님. 단색 또는 무형. 인물 실루엣·암전 연출 전용.

기본 배경(폴백): `bg_void`

| 키 | 장소 | 시점 | 톤 | 원본 에셋 | 상태 |
|---|---|---|---|---|---|
| `fx.void` | 암전 | — | 무배경 | `bg_void` | 보유 |
| `fx.blank` | 역광 실루엣용 무배경 | — | 무배경 | `bg_blank` | 보유 |

## ui — UI 자산

> **아트 디렉션(고정)** — 게임 UI에 얹는 도해. 배경 연출용이 아님.

기본 배경(폴백): `map_asra`

| 키 | 장소 | 시점 | 톤 | 원본 에셋 | 상태 |
|---|---|---|---|---|---|
| `ui.map.asra` | 아스라 영지 지도 | — | 무배경 | `map_asra` | 보유 |

## 생성 대기 슬롯 — 프롬프트

그대로 넣어서 뽑고, 결과를 webp base64 로 `window.BGS` 에 새 에셋 id 로 넣은 뒤 `BG_LIB` 의 해당 키에 `src` 를 채우면 끝.

### `serenia.call.pov`

```
[지역 · 세레니아 · 부름의 백색] 경계 없는 백색 공간. 바닥도 천장도 지평선도 없다. 확산광만 존재해 그림자가 거의 생기지 않는다. 색은 흰빛·은빛·아주 옅은 하늘빛 세 가지로만 제한. 채도 극단적으로 낮게, 윤곽은 부드럽게 번지게. 원근을 알 수 있는 단서를 절대 넣지 말 것. 미세한 필름 그레인.
[장소] 부름이 일어나는 백색의 한가운데. 은빛 관을 쓴 존재가 두 팔을 벌린 자리
[시점 · 1인칭] 주인공 시선 높이, 강한 원근, 화면 가장자리 왜곡
[공통] 가로 16:9 (1456x816). ★2D anime background art, cel shaded, flat vivid saturated colors, clean crisp edges, Japanese animation studio background painting, bright and clear. NOT photorealistic, NOT a 3D render, no photographic texture, no realistic lighting. 인물 없음. 텍스트·워터마크 없음. ★화면 정중앙은 인물이 설 자리이므로 비워둘 것 — 중앙에 큰 나무나 구조물을 두지 말 것
```

### `serenia.gate.wide`

```
[지역 · 세레니아 · 부름의 백색] 경계 없는 백색 공간. 바닥도 천장도 지평선도 없다. 확산광만 존재해 그림자가 거의 생기지 않는다. 색은 흰빛·은빛·아주 옅은 하늘빛 세 가지로만 제한. 채도 극단적으로 낮게, 윤곽은 부드럽게 번지게. 원근을 알 수 있는 단서를 절대 넣지 말 것. 미세한 필름 그레인.
[장소] 봉인된 문. 백색 공간 끝에 홀로 서 있는 거대한 석문
[시점 · 원경] 광각 24mm, 장소 전체가 들어오는 전경, 지평선 낮게, 인물 없음
[공통] 가로 16:9 (1456x816). ★2D anime background art, cel shaded, flat vivid saturated colors, clean crisp edges, Japanese animation studio background painting, bright and clear. NOT photorealistic, NOT a 3D render, no photographic texture, no realistic lighting. 인물 없음. 텍스트·워터마크 없음. ★화면 정중앙은 인물이 설 자리이므로 비워둘 것 — 중앙에 큰 나무나 구조물을 두지 말 것
```

### `asra.castle.dawn`

```
[지역 · 아스라 왕국] 중세 북유럽풍 석조 왕국. 회청색 화강암과 짙은 남색 지붕, 포인트로만 금빛 문장. 하늘은 늘 옅은 구름이 낀 한랭한 톤. 광원은 낮게 깔린 태양 또는 횃불. 직선적이고 육중한 건축에 장식은 절제. 중간 채도, 명암 대비는 강하게.
[장소] 아스라 왕성 외관. 절벽을 등진 육중한 석조 성채
[시점 · 새벽] 박명, 낮은 대비, 푸른 기운에 옅은 주황 한 줄
[공통] 가로 16:9 (1456x816). ★2D anime background art, cel shaded, flat vivid saturated colors, clean crisp edges, Japanese animation studio background painting, bright and clear. NOT photorealistic, NOT a 3D render, no photographic texture, no realistic lighting. 인물 없음. 텍스트·워터마크 없음. ★화면 정중앙은 인물이 설 자리이므로 비워둘 것 — 중앙에 큰 나무나 구조물을 두지 말 것
```

### `asra.gate.night`

```
[지역 · 아스라 왕국] 중세 북유럽풍 석조 왕국. 회청색 화강암과 짙은 남색 지붕, 포인트로만 금빛 문장. 하늘은 늘 옅은 구름이 낀 한랭한 톤. 광원은 낮게 깔린 태양 또는 횃불. 직선적이고 육중한 건축에 장식은 절제. 중간 채도, 명암 대비는 강하게.
[장소] 성 안쪽 아치 통로. 좌우로 늘어선 석주와 끝에서 새어드는 빛
[시점 · 밤] 달빛 또는 횃불 단일 광원, 청색 암부
[공통] 가로 16:9 (1456x816). ★2D anime background art, cel shaded, flat vivid saturated colors, clean crisp edges, Japanese animation studio background painting, bright and clear. NOT photorealistic, NOT a 3D render, no photographic texture, no realistic lighting. 인물 없음. 텍스트·워터마크 없음. ★화면 정중앙은 인물이 설 자리이므로 비워둘 것 — 중앙에 큰 나무나 구조물을 두지 말 것
```

### `asra.training.dusk`

```
[지역 · 아스라 왕국] 중세 북유럽풍 석조 왕국. 회청색 화강암과 짙은 남색 지붕, 포인트로만 금빛 문장. 하늘은 늘 옅은 구름이 낀 한랭한 톤. 광원은 낮게 깔린 태양 또는 횃불. 직선적이고 육중한 건축에 장식은 절제. 중간 채도, 명암 대비는 강하게.
[장소] 기사단 훈련장. 흙바닥과 목검 거치대, 둘러싼 목책
[시점 · 해질녘] 황혼 역광, 긴 그림자, 실루엣 강조
[공통] 가로 16:9 (1456x816). ★2D anime background art, cel shaded, flat vivid saturated colors, clean crisp edges, Japanese animation studio background painting, bright and clear. NOT photorealistic, NOT a 3D render, no photographic texture, no realistic lighting. 인물 없음. 텍스트·워터마크 없음. ★화면 정중앙은 인물이 설 자리이므로 비워둘 것 — 중앙에 큰 나무나 구조물을 두지 말 것
```

### `asra.market.mid`

```
[지역 · 아스라 왕국] 중세 북유럽풍 석조 왕국. 회청색 화강암과 짙은 남색 지붕, 포인트로만 금빛 문장. 하늘은 늘 옅은 구름이 낀 한랭한 톤. 광원은 낮게 깔린 태양 또는 횃불. 직선적이고 육중한 건축에 장식은 절제. 중간 채도, 명암 대비는 강하게.
[장소] 성 아랫마을 장터. 천막과 좌판이 늘어선 좁은 골목
[시점 · 기본] 35mm, 아이레벨, 장소를 한 화면에 담되 공간감 유지
[공통] 가로 16:9 (1456x816). ★2D anime background art, cel shaded, flat vivid saturated colors, clean crisp edges, Japanese animation studio background painting, bright and clear. NOT photorealistic, NOT a 3D render, no photographic texture, no realistic lighting. 인물 없음. 텍스트·워터마크 없음. ★화면 정중앙은 인물이 설 자리이므로 비워둘 것 — 중앙에 큰 나무나 구조물을 두지 말 것
```

### `sylvarn.edge.night`

```
[지역 · 실바른 숲 일대] 습한 온대 활엽수림. 계절은 한여름이라 잎이 무성하고 바닥까지 초록 이끼가 덮여 있다. 낙엽이 쌓인 가을 풍경이 아니다. 짙은 녹청과 이끼빛이 지배색, 흙은 적갈색. 나뭇잎 사이로 떨어지는 산광과 공기 중 부유물, 늘 옅게 깔린 안개.
[장소] 실바른 숲 가장자리. 초지가 끝나고 나무가 시작되는 경계
[시점 · 밤] 달빛 또는 횃불 단일 광원, 청색 암부
[공통] 가로 16:9 (1456x816). ★2D anime background art, cel shaded, flat vivid saturated colors, clean crisp edges, Japanese animation studio background painting, bright and clear. NOT photorealistic, NOT a 3D render, no photographic texture, no realistic lighting. 인물 없음. 텍스트·워터마크 없음. ★화면 정중앙은 인물이 설 자리이므로 비워둘 것 — 중앙에 큰 나무나 구조물을 두지 말 것
```

### `sylvarn.deep.night`

```
[지역 · 실바른 숲 일대] 습한 온대 활엽수림. 계절은 한여름이라 잎이 무성하고 바닥까지 초록 이끼가 덮여 있다. 낙엽이 쌓인 가을 풍경이 아니다. 짙은 녹청과 이끼빛이 지배색, 흙은 적갈색. 나뭇잎 사이로 떨어지는 산광과 공기 중 부유물, 늘 옅게 깔린 안개.
[장소] 숲 속 깊은 곳. 하늘이 거의 보이지 않는 우거진 수관
[시점 · 밤] 달빛 또는 횃불 단일 광원, 청색 암부
[공통] 가로 16:9 (1456x816). ★2D anime background art, cel shaded, flat vivid saturated colors, clean crisp edges, Japanese animation studio background painting, bright and clear. NOT photorealistic, NOT a 3D render, no photographic texture, no realistic lighting. 인물 없음. 텍스트·워터마크 없음. ★화면 정중앙은 인물이 설 자리이므로 비워둘 것 — 중앙에 큰 나무나 구조물을 두지 말 것
```

### `sylvarn.pond.dawn`

```
[지역 · 실바른 숲 일대] 습한 온대 활엽수림. 계절은 한여름이라 잎이 무성하고 바닥까지 초록 이끼가 덮여 있다. 낙엽이 쌓인 가을 풍경이 아니다. 짙은 녹청과 이끼빛이 지배색, 흙은 적갈색. 나뭇잎 사이로 떨어지는 산광과 공기 중 부유물, 늘 옅게 깔린 안개.
[장소] 숲속 연못. 수면이 거울처럼 잔잔한 작은 웅덩이
[시점 · 새벽] 박명, 낮은 대비, 푸른 기운에 옅은 주황 한 줄
[공통] 가로 16:9 (1456x816). ★2D anime background art, cel shaded, flat vivid saturated colors, clean crisp edges, Japanese animation studio background painting, bright and clear. NOT photorealistic, NOT a 3D render, no photographic texture, no realistic lighting. 인물 없음. 텍스트·워터마크 없음. ★화면 정중앙은 인물이 설 자리이므로 비워둘 것 — 중앙에 큰 나무나 구조물을 두지 말 것
```
