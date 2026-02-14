#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


def score_text(text: str, positive: list[str], negative: list[str]) -> dict:
    pos_hits = [w for w in positive if w in text]
    neg_hits = [w for w in negative if w in text]
    score = len(pos_hits) - len(neg_hits)
    return {"score": score, "positive_hits": pos_hits, "negative_hits": neg_hits}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--lexicon", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    lexicon = json.loads(Path(args.lexicon).read_text(encoding="utf-8"))
    rows = list(csv.DictReader(Path(args.input).read_text(encoding="utf-8").splitlines()))

    by_book: dict[str, dict] = {}
    for row in rows:
        book_id = row["book_id"]
        result = score_text(row.get("review_text", ""), lexicon["positive"], lexicon["negative"])
        bucket = by_book.setdefault(book_id, {"count": 0, "score_sum": 0, "negative_keywords": {}})
        bucket["count"] += 1
        bucket["score_sum"] += result["score"]
        for kw in result["negative_hits"]:
            bucket["negative_keywords"][kw] = bucket["negative_keywords"].get(kw, 0) + 1

    summary = {
        "books": [],
        "global_negative_top": {}
    }

    for book_id, item in by_book.items():
        avg = item["score_sum"] / item["count"] if item["count"] else 0
        summary["books"].append({
            "book_id": book_id,
            "review_count": item["count"],
            "avg_sentiment": round(avg, 3),
            "negative_keywords": item["negative_keywords"]
        })
        for k, v in item["negative_keywords"].items():
            summary["global_negative_top"][k] = summary["global_negative_top"].get(k, 0) + v

    summary["books"].sort(key=lambda x: x["book_id"])
    summary["global_negative_top"] = dict(sorted(summary["global_negative_top"].items(), key=lambda kv: kv[1], reverse=True))

    Path(args.output).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
