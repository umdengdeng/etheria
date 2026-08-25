/* 에테리아 에셋·연출 정합성 검사
 *   실행:  node tools/check.js
 *
 * 사람 눈으로 잡기 어려운 것들만 본다.
 *   1) 씬이 부르는 배경/스프라이트 키가 실제로 그려지는가
 *   2) 뽑아놓고 어디서도 안 쓰이는 에셋이 있는가  ← 늑대 마수가 이렇게 묻혀 있었다
 *   3) 한 에피소드 안에서 배경 톤/지역이 튀는가    ← "배경 일관성 없어 보인다"의 정체
 *   4) 배경끼리 화면 비율이 제각각인가
 * 나가는 값: 문제 있으면 exit 1
 */
const fs = require("fs");
const path = require("path");

const FILE = path.join(__dirname, "..", "index.html");
const src = fs.readFileSync(FILE, "utf8");
const blocks = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (blocks.length < 3) fail("index.html 에서 script 블록 3개를 찾지 못했다");

const assetsJs = blocks.find(b => b.includes("window.BGS="));
const libJs = blocks.find(b => b.includes("const BG_LIB="));
const gameJs = blocks.find(b => b.includes("const EPS="));
if (!assetsJs || !libJs || !gameJs) fail("에셋 / 라이브러리 / 게임 블록을 구분하지 못했다");

// 라이브러리를 실제로 실행해서 가져온다 (문서가 아니라 코드가 기준)
const sandbox = { window: {} };
new Function("window", assetsJs + "\n" + libJs +
  "\nwindow.__lib={BG_REGIONS,BG_SHOTS,BG_PLACES,BG_LIB,BG_TONES,bgResolve,bgTodo};")(sandbox.window);
const { BG_REGIONS, BG_LIB, BG_TONES, bgResolve } = sandbox.window.__lib;
const BGS = sandbox.window.BGS || {};
const SPRITES = sandbox.window.SPRITES || {};

const problems = [];
const notes = [];
function bad(tag, msg) { problems.push(`[${tag}] ${msg}`); }
function note(tag, msg) { notes.push(`[${tag}] ${msg}`); }
function fail(m) { console.error("치명: " + m); process.exit(2); }

/* ---------- 1. 씬이 부르는 키가 실제로 그려지는가 ---------- */
const bgKeys = [...gameJs.matchAll(/bg:"([^"]+)"/g)].map(m => m[1]);
const bgKeysDirect = [...gameJs.matchAll(/BG\["([^"]+)"\]/g)].map(m => m[1]);
const locKeys = [...gameJs.matchAll(/(?:card|pov)\s*:\s*"([^"]+)"/g)].map(m => m[1]);
const usedBg = new Set([...bgKeys, ...bgKeysDirect, ...locKeys]);

for (const k of usedBg) {
  if (!bgResolve(k)) bad("배경없음", `키 "${k}" 가 아무 이미지로도 풀리지 않는다`);
  else if (!BG_LIB[k] && !BGS[k]) bad("미등록키", `키 "${k}" 가 라이브러리에 없다 (폴백으로만 표시 중)`);
}

const spKeys = new Set([...gameJs.matchAll(/\bsp:"([^"]+)"/g)].map(m => m[1]));
for (const k of spKeys) {
  if (!SPRITES["eliana_" + k] && !SPRITES[k]) bad("스프라이트없음", `sp:"${k}" 에 해당하는 이미지가 없다`);
}

/* ---------- 2. 뽑아놓고 안 쓰이는 에셋 ---------- */
const libSrc = new Set(Object.values(BG_LIB).map(v => v.src).filter(Boolean));
for (const id of Object.keys(BGS)) {
  if (!libSrc.has(id)) bad("방치에셋", `에셋 "${id}" 가 배경 라이브러리에 등록돼 있지 않다 → 게임에 절대 안 나온다`);
}
for (const [k, v] of Object.entries(BG_LIB)) {
  if (v.src && !BGS[v.src]) bad("깨진참조", `"${k}" 가 없는 에셋 "${v.src}" 를 가리킨다`);
}
const reachable = new Set();
for (const k of usedBg) {
  const url = bgResolve(k);
  const id = Object.keys(BGS).find(a => BGS[a] === url);
  if (id) reachable.add(id);
}
for (const [k, v] of Object.entries(BG_LIB)) {
  if (v.src && BGS[v.src] && !reachable.has(v.src))
    note("미사용", `"${k}" (${v.src}) 는 등록돼 있지만 어느 씬도 부르지 않는다`);
}
for (const [k, v] of Object.entries(BG_LIB)) {
  if (v.retone) note("재생성", `"${k}" (${v.src}) — ${v.retone}`);
}
const usedSpr = new Set();
for (const k of spKeys) usedSpr.add(SPRITES["eliana_" + k] ? "eliana_" + k : k);
for (const m of gameJs.matchAll(/SPR\.([A-Za-z0-9_]+)/g)) usedSpr.add(m[1]);
for (const id of Object.keys(SPRITES)) {
  if (!usedSpr.has(id)) note("미사용", `스프라이트 "${id}" 를 어디서도 부르지 않는다`);
}

/* ---------- 3. 한 에피소드 안에서 톤·지역이 튀는가 ---------- */
const eps = [];
const epRe = /\{id:"([a-z0-9_]+)",(?:stage:\d+,)?title:"([^"]*)"/g;
let m, marks = [];
while ((m = epRe.exec(gameJs))) marks.push({ id: m[1], title: m[2], at: m.index });
marks.forEach((mk, i) => {
  const body = gameJs.slice(mk.at, i + 1 < marks.length ? marks[i + 1].at : gameJs.length);
  eps.push({ ...mk, keys: [...body.matchAll(/bg:"([^"]+)"/g)].map(x => x[1]) });
});

const toneOf = k => (BG_LIB[k] || {}).tone;
const 연출톤 = new Set(["flat", "white"]);   // 암전·백색은 어디에 끼어도 튀지 않는다
// 밝기 차이(bright↔dim↔indoor)는 연출로 넘어가지만, 계절·시간대가 갈리면 눈에 띈다
const 낮계열 = new Set(["bright", "dim", "indoor"]);
for (const ep of eps) {
  if (!ep.keys.length) continue;
  const tones = [...new Set(ep.keys.map(toneOf).filter(t => t && !연출톤.has(t)))];
  const detail = () => tones.map(t => {
    const ks = [...new Set(ep.keys.filter(k => toneOf(k) === t))];
    const re = ks.filter(k => (BG_LIB[k] || {}).retone).length ? " ※재생성 대기" : "";
    return `${BG_TONES[t] || t}(${ks.join(", ")})${re}`;
  }).join("  ↔  ");
  if (tones.some(t => !낮계열.has(t)) && tones.length > 1)
    bad("톤혼재", `${ep.id} "${ep.title}" 안에서 계절·시간대가 갈린다 → ${detail()}`);
  else if (tones.length > 1)
    note("밝기차", `${ep.id} "${ep.title}" 안에서 밝기가 갈린다 → ${detail()}`);
  const regions = [...new Set(ep.keys.map(k => k.split(".")[0]).filter(r => r !== "fx" && r !== "ui"))];
  if (regions.length > 1)
    note("지역이동", `${ep.id} "${ep.title}" 가 여러 지역을 오간다 → ${regions.join(" → ")} (의도한 이동이면 무시)`);
}

/* ---------- 3.5 대사가 약속한 그림이 실제로 있는가 ----------
   코드 검사로는 절대 못 잡는 종류다. 사람이 눈으로 보고 여기에 기록해야 한다.
   늑대 목줄이 대표 사례 — 대사는 "목에 낡은 쇠 목줄"인데 그림엔 없었다. */
try {
  const vc = JSON.parse(fs.readFileSync(path.join(__dirname, "visual-claims.json"), "utf8"));
  for (const c of vc.claims) {
    const where = c.key + (c.asset ? ` (${c.asset})` : "");
    if (c.state === "fail")
      bad("그림불일치", `${where} — 대사는 "${c.must}"를 약속하는데 그림이 다르다. ${c.note || ""}`);
    else if (c.state === "todo")
      note("미확인", `${where} — "${c.must}" 확인 안 됨. ${c.note || ""}`);
  }
  const done = vc.claims.filter(c => c.state === "ok").length;
  note("대조", `그림↔대사 대조 ${done}/${vc.claims.length} 확인 완료 (tools/visual-claims.json)`);
} catch (e) {
  note("대조", "visual-claims.json 을 읽지 못했다: " + e.message);
}

/* ---------- 4. 배경 화면 비율 ---------- */
function webpSize(dataUrl) {
  const b = Buffer.from(dataUrl.split(",")[1], "base64");
  if (b.slice(0, 4).toString() !== "RIFF") return null;
  const tag = b.slice(12, 16).toString();
  if (tag === "VP8X") return { w: (b.readUIntLE(24, 3) & 0xffffff) + 1, h: (b.readUIntLE(27, 3) & 0xffffff) + 1 };
  if (tag === "VP8L") { const n = b.readUInt32LE(21); return { w: (n & 0x3fff) + 1, h: ((n >> 14) & 0x3fff) + 1 }; }
  if (tag === "VP8 ") { const o = b.indexOf(Buffer.from([0x9d, 0x01, 0x2a])); if (o < 0) return null;
    return { w: b.readUInt16LE(o + 3) & 0x3fff, h: b.readUInt16LE(o + 5) & 0x3fff }; }
  return null;
}
const ratios = {};
for (const [k, v] of Object.entries(BG_LIB)) {
  if (!v.src || !BGS[v.src] || k.startsWith("ui.") || k.startsWith("fx.")) continue;
  const s = webpSize(BGS[v.src]); if (!s) continue;
  const r = (s.w / s.h).toFixed(2);
  (ratios[r] = ratios[r] || []).push(`${v.src} ${s.w}x${s.h}`);
}
const rk = Object.keys(ratios);
if (rk.length > 1) {
  const main = rk.sort((a, b) => ratios[b].length - ratios[a].length)[0];
  for (const r of rk) if (r !== main)
    note("비율", `주 비율 ${main} 과 다른 배경 ${ratios[r].length}장 (${r}) → ${ratios[r].join(", ")}`);
}

/* ---------- 0. 아직 적용 안 된 결정 ----------
   Etheria/DECISIONS.md 의 ⬜대기 줄을 세어 맨 앞에 띄운다.
   정해놓고 잊어버리는 걸 막으려는 것이다. */
let pendingLines = [];
try {
  const dp = path.join(__dirname, "..", "..", "..", "Etheria", "DECISIONS.md");
  const md = fs.readFileSync(dp, "utf8");
  const sec = md.split("## 🔧")[0];
  pendingLines = sec.split(String.fromCharCode(10)).filter(l => l.indexOf("| ⬜ |") >= 0)
    .map(l => l.split("|").map(x => x.trim()).filter(Boolean))
    .map(c => `${c[0]}  ${c[1]}${c[3] ? "  — " + c[3] : ""}`);
} catch (e) { /* 문서가 없으면 조용히 넘어간다 */ }

/* ---------- 결과 ---------- */
const todo = sandbox.window.__lib.bgTodo();
console.log(`배경 에셋 ${Object.keys(BGS).length}장 · 라이브러리 슬롯 ${Object.keys(BG_LIB).length}개 · 생성 대기 ${todo.length}개`);
console.log(`스프라이트 ${Object.keys(SPRITES).length}장 · 에피소드 ${eps.length}개 · 씬이 부르는 배경 키 ${usedBg.size}개`);
console.log("");
if (pendingLines.length) {
  console.log("■ 정해놓고 아직 안 한 것 (DECISIONS.md)");
  pendingLines.forEach(l => console.log("  ⬜ " + l));
  console.log("");
}
if (problems.length) { console.log("■ 고쳐야 함"); problems.forEach(p => console.log("  ✗ " + p)); console.log(""); }
if (notes.length) { console.log("■ 확인 필요"); notes.forEach(p => console.log("  · " + p)); console.log(""); }
if (!problems.length && !notes.length) console.log("문제 없음.");
else if (!problems.length) console.log("치명적인 문제는 없음.");
console.log("");
console.log("비주얼 연출(정면대칭·정중앙·명암)은 따로 본다 →  python tools/vcheck.py");
process.exit(problems.length ? 1 : 0);
