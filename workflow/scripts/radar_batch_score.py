#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


def decision(total: float, focus: int, trial: int) -> str:
    if total >= focus:
        return "重点开发"
    if total >= trial:
        return "试投放打磨"
    return "暂缓立项"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--weights", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    cfg = json.loads(Path(args.weights).read_text(encoding="utf-8"))
    rows = list(csv.DictReader(Path(args.input).read_text(encoding="utf-8").splitlines()))

    fields = [
        "project_id", "genre", "topic_opportunity", "persona_distinctiveness",
        "conflict_engine", "pace_hook", "commercial_potential", "total_score", "decision"
    ]

    out_lines = [fields]
    for r in rows:
        total = (
            float(r["topic_opportunity"]) * cfg["topic_opportunity"] +
            float(r["persona_distinctiveness"]) * cfg["persona_distinctiveness"] +
            float(r["conflict_engine"]) * cfg["conflict_engine"] +
            float(r["pace_hook"]) * cfg["pace_hook"] +
            float(r["commercial_potential"]) * cfg["commercial_potential"]
        )
        out_lines.append([
            r["project_id"], r["genre"], r["topic_opportunity"], r["persona_distinctiveness"],
            r["conflict_engine"], r["pace_hook"], r["commercial_potential"],
            f"{total:.2f}",
            decision(total, cfg["decision_threshold"]["focus"], cfg["decision_threshold"]["trial"])
        ])

    with Path(args.output).open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(out_lines)


if __name__ == "__main__":
    main()
