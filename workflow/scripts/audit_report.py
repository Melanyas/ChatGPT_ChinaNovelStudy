#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    p = argparse.ArgumentParser(description="根据阈值生成审查报告。")
    p.add_argument("--review", required=True)
    p.add_argument("--radar", required=True)
    p.add_argument("--chapter", required=True)
    p.add_argument("--thresholds", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    review = json.loads(Path(args.review).read_text(encoding="utf-8"))
    chapter = json.loads(Path(args.chapter).read_text(encoding="utf-8"))
    radar_rows = load_csv(Path(args.radar))
    th = json.loads(Path(args.thresholds).read_text(encoding="utf-8"))

    top = sorted(radar_rows, key=lambda x: float(x["total_score"]), reverse=True)[0]
    top_score = float(top["total_score"])

    neg_total = sum(review["global_negative_top"].values()) if review["global_negative_top"] else 0
    review_total = sum(x["review_count"] for x in review["books"])
    neg_ratio = (neg_total / review_total) if review_total else 0.0

    checks = [
        {
            "name": "chapter_overall",
            "value": chapter["scores"]["overall"],
            "threshold": th["chapter_overall_min"],
            "pass": chapter["scores"]["overall"] >= th["chapter_overall_min"],
        },
        {
            "name": "hook_strength",
            "value": chapter["chapter_hooks"]["strength"],
            "threshold": th["hook_strength_min"],
            "pass": chapter["chapter_hooks"]["strength"] >= th["hook_strength_min"],
        },
        {
            "name": "top_project_score",
            "value": top_score,
            "threshold": th["top_project_score_min"],
            "pass": top_score >= th["top_project_score_min"],
        },
        {
            "name": "negative_keyword_ratio",
            "value": round(neg_ratio, 4),
            "threshold": th["max_global_negative_keyword_ratio"],
            "pass": neg_ratio <= th["max_global_negative_keyword_ratio"],
        },
    ]

    result = {
        "pass": all(c["pass"] for c in checks),
        "checks": checks,
        "top_project": top,
    }
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
