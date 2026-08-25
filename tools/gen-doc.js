/* BACKGROUNDS.md 를 index.html 의 배경 라이브러리에서 다시 만든다.
 *   실행:  node tools/gen-doc.js
 * 문서를 손으로 고치지 말 것 — 코드가 기준이고 문서는 결과물이다.
 */
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const src = fs.readFileSync(path.join(root, "index.html"), "utf8");
const blocks = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const assetsJs = blocks.find(b => b.includes("window.BGS="));
const libJs = blocks.find(b => b.includes("const BG_LIB="));

const w = {};
new Function("window", assetsJs + "\n" + libJs +
  "\nwindow.__lib={BG_REGIONS,BG_SHOTS,BG_PLACES,BG_LIB,BG_TONES,bgPrompt,bgTodo};")(w);
const { BG_REGIONS, BG_SHOTS, BG_PLACES, BG_LIB, BG_TONES, bgPrompt, bgTodo } = w.__lib;
const BGS = w.BGS;

const byRegion = {};
for (const k of Object.keys(BG_LIB)) (byRegion[k.split(".")[0]] ||= []).push(k);

const L = [];
L.push("# 에테리아 · 배경 라이브러리");
L.push("");
L.push("`node tools/gen-doc.js` 로 생성됨. 직접 고치지 말고 `index.html` 의 `BG_LIB` 를 고칠 것.");
L.push("");
L.push("배경은 **지역 → 장소 → 시점** 으로 관리한다. 키 예: `asra.rampart.rain`");
L.push("");
L.push("- 새 배경은 `bgPrompt(\"키\")` 로 프롬프트를 만들어 뽑는다. 지역 아트 디렉션이 앞에 붙어서 톤이 어긋나지 않는다.");
L.push("- 씬에서는 `bg:\"키\"`. 없는 시점을 불러도 **같은 장소의 다른 시점 → 지역 기본** 순으로 대체되어 화면이 비지 않는다.");
L.push("- **파일 이름을 믿지 말 것.** `forest_beast` 에는 마수가 없고 `asra_castle` 은 성 외관이 아니라 알현실이었다. 매핑 전에 이미지를 직접 열어볼 것.");
L.push("- 고치고 나면 `node tools/check.js` 로 정합성 검사.");
L.push("");
L.push("## 시점 어휘");
L.push("");
L.push("| 구분 | 코드 |");
L.push("|---|---|");
L.push("| 카메라 | `wide` 원경 · `mid` 기본 · `close` 근경 · `pov` 1인칭 · `vista` 조망 |");
L.push("| 시간·날씨 | `day` · `night` · `dawn` 새벽 · `dusk` 해질녘 · `rain` 비 · `dim` 어둑 |");
L.push("| 연출 | `ground` 지면 · `bush` 수풀너머 · `blur` 흐린시야 · `panic` 급박 · `shout` 외침 · `wake` 각성 · `beast` 조우 · `dissolve` 소멸 |");
L.push("");
L.push("## 화면 톤");
L.push("");
L.push("한 에피소드 안에서 톤이 갈리면 배경이 튄다. `tools/check.js` 가 이걸 잡는다.");
L.push("");
L.push(Object.entries(BG_TONES).map(([k, v]) => "`" + k + "` " + v).join(" · "));
L.push("");

for (const r of Object.keys(byRegion)) {
  const R = BG_REGIONS[r];
  L.push(`## ${r} — ${R.ko}`);
  L.push("");
  L.push("> **아트 디렉션(고정)** — " + R.art);
  L.push("");
  L.push("기본 배경(폴백): `" + R.def + "`");
  L.push("");
  L.push("| 키 | 장소 | 시점 | 톤 | 원본 에셋 | 상태 |");
  L.push("|---|---|---|---|---|---|");
  for (const k of byRegion[r]) {
    const p = k.split("."), e = BG_LIB[k];
    const place = (BG_PLACES[p[0] + "." + p[1]] || "").split(".")[0];
    const shot = BG_SHOTS[p[2]] ? BG_SHOTS[p[2]].ko : "—";
    const state = !e.src || !BGS[e.src] ? "**생성 대기**" : e.retone ? "**재생성 필요**" : "보유";
    L.push(`| \`${k}\` | ${place} | ${shot} | ${BG_TONES[e.tone] || "—"} | ${e.src ? "`" + e.src + "`" : "—"} | ${state} |`);
  }
  L.push("");
}

const retone = Object.entries(BG_LIB).filter(([, v]) => v.retone);
if (retone.length) {
  L.push("## 재생성 필요 (이미 있지만 톤이 안 맞는 것)");
  L.push("");
  for (const [k, v] of retone) {
    L.push(`### \`${k}\` — ${v.retone}`);
    L.push("");
    L.push("```");
    L.push(bgPrompt(k));
    L.push("```");
    L.push("");
  }
}

L.push("## 생성 대기 슬롯 — 프롬프트");
L.push("");
L.push("그대로 넣어서 뽑고, 결과를 webp base64 로 `window.BGS` 에 새 에셋 id 로 넣은 뒤 `BG_LIB` 의 해당 키에 `src` 를 채우면 끝.");
L.push("");
for (const k of bgTodo()) {
  L.push("### `" + k + "`");
  L.push("");
  L.push("```");
  L.push(bgPrompt(k));
  L.push("```");
  L.push("");
}

fs.writeFileSync(path.join(root, "BACKGROUNDS.md"), L.join("\n"), "utf8");
console.log("BACKGROUNDS.md 갱신 · 슬롯 " + Object.keys(BG_LIB).length + "개, 생성 대기 " + bgTodo().length + "개, 재생성 " + retone.length + "개");
