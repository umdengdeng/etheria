# -*- coding: utf-8 -*-
"""이미지를 뽑을 때마다 기록한다. 게임에 넣지 않은 테스트도 포함.

    python tools/log_gen.py --tool "Grok Imagine" --model v2.0 --ratio 16:9 \
        --key sylvarn.deep.ground --file .shots/L_anime.png --result 채택 --note "애니풍 테스트"

왜: 채택 안 된 시도도 남아야 "그건 이미 해봤고 이래서 안 됐다"를 알 수 있다.
"""
import argparse, json, sys
from pathlib import Path

HIST = Path(__file__).parent / "asset-history.json"

def add(**kw):
    try:
        d = json.loads(HIST.read_text(encoding="utf-8"))
    except Exception:
        d = {"entries": []}
    d.setdefault("entries", []).append({k: v for k, v in kw.items() if v is not None})
    HIST.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(d["entries"])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--ratio", default=None)
    ap.add_argument("--key", default=None, help="어떤 배경 키를 노린 것인가")
    ap.add_argument("--file", default=None, help="결과 파일 경로")
    ap.add_argument("--result", default="테스트", help="채택 / 반려 / 테스트")
    ap.add_argument("--note", default=None)
    ap.add_argument("--prompt", default=None)
    a = ap.parse_args()
    n = add(kind="생성시도", tool=a.tool, model=a.model, ratio=a.ratio, key=a.key,
            file=a.file, result=a.result, note=a.note, prompt=(a.prompt or "")[:400] or None)
    print("기록 %d건째: %s / %s → %s" % (n, a.tool, a.model, a.result))
