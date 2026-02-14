#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description="基于本轮负向高频词，自动补充情绪词典。")
    p.add_argument("--review", required=True)
    p.add_argument("--lexicon", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--top-k", type=int, default=3)
    args = p.parse_args()

    review = json.loads(Path(args.review).read_text(encoding="utf-8"))
    lexicon = json.loads(Path(args.lexicon).read_text(encoding="utf-8"))

    existing = set(lexicon.get("negative", []))
    candidates = list(review.get("global_negative_top", {}).items())[: args.top_k]

    added = []
    for kw, _ in candidates:
        if kw not in existing:
            lexicon.setdefault("negative", []).append(kw)
            added.append(kw)

    Path(args.output).write_text(json.dumps(lexicon, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"added": added, "output": args.output}, ensure_ascii=False))


if __name__ == "__main__":
    main()
