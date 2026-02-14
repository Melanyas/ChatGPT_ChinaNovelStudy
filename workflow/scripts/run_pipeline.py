#!/usr/bin/env python3
import argparse
import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def log_line(log_file: Path | None, message: str, debug: bool = False) -> None:
    line = f"[{datetime.utcnow().isoformat()}Z] {message}"
    if debug:
        print(line)
    if log_file:
        with log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def run(cmd: list[str], log_file: Path | None, debug: bool = False) -> None:
    log_line(log_file, f"run: {' '.join(cmd)}", debug)
    subprocess.run(cmd, check=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--debug", action="store_true")
    p.add_argument("--auto-update", action="store_true", help="根据本轮结果自动更新词典副本")
    p.add_argument("--audit", action="store_true", help="生成本轮审查报告")
    p.add_argument("--generate", action="store_true", help="自动生成网文样稿")
    p.add_argument("--generate-chapters", type=int, default=3, help="自动生成章节数")
    p.add_argument("--colloquial-dialogue", action="store_true", help="生成时启用口语化对白")
    args = p.parse_args()

    artifacts = ROOT / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)

    log_file = artifacts / f"debug_{args.run_id}.log" if args.debug else None
    review_out = artifacts / f"review_signals_{args.run_id}.json"
    radar_out = artifacts / f"radar_scores_{args.run_id}.csv"
    chapter_out = artifacts / f"chapter_audit_{args.run_id}.json"
    summary_out = artifacts / f"summary_{args.run_id}.md"

    generated_out = artifacts / f"generated_novel_{args.run_id}.md"
    generated_meta = artifacts / f"generated_novel_{args.run_id}.json"

    run([
        "python", str(ROOT / "scripts/review_signal_report.py"),
        "--input", str(ROOT / "input/review_snapshot_sample.csv"),
        "--lexicon", str(ROOT / "config/sentiment_lexicon.json"),
        "--output", str(review_out)
    ], log_file, args.debug)
    run([
        "python", str(ROOT / "scripts/radar_batch_score.py"),
        "--input", str(ROOT / "input/project_features_sample.csv"),
        "--weights", str(ROOT / "config/radar_weights.json"),
        "--output", str(radar_out)
    ], log_file, args.debug)
    run([
        "python", str(ROOT / "scripts/chapter_audit.py"),
        "--input", str(ROOT / "input/chapter_sample.txt"),
        "--output", str(chapter_out)
    ], log_file, args.debug)

    if args.audit:
        audit_out = artifacts / f"audit_{args.run_id}.json"
        run([
            "python", str(ROOT / "scripts/audit_report.py"),
            "--review", str(review_out),
            "--radar", str(radar_out),
            "--chapter", str(chapter_out),
            "--thresholds", str(ROOT / "config/audit_thresholds.json"),
            "--output", str(audit_out),
        ], log_file, args.debug)

    if args.auto_update:
        lexicon_updated = artifacts / f"sentiment_lexicon_{args.run_id}.json"
        run([
            "python", str(ROOT / "scripts/self_update.py"),
            "--review", str(review_out),
            "--lexicon", str(ROOT / "config/sentiment_lexicon.json"),
            "--output", str(lexicon_updated),
            "--top-k", "5",
        ], log_file, args.debug)

    review = json.loads(review_out.read_text(encoding="utf-8"))
    chapter = json.loads(chapter_out.read_text(encoding="utf-8"))
    with radar_out.open("r", encoding="utf-8") as f:
        radar_rows = list(csv.DictReader(f))

    top_project = sorted(radar_rows, key=lambda x: float(x["total_score"]), reverse=True)[0]

    if args.generate:
        cmd = [
            "python", str(ROOT / "scripts/novel_generator.py"),
            "--theme", top_project.get("genre", "都市逆袭"),
            "--protagonist", "林砚",
            "--conflict", "在高压竞争中守住底线并完成阶层跃迁",
            "--market-signal", str(review_out),
            "--chapters", str(max(1, args.generate_chapters)),
            "--seed", "42",
            "--scene", "旧工业园",
            "--output", str(generated_out),
            "--meta-output", str(generated_meta),
        ]
        if args.colloquial_dialogue:
            cmd.append("--colloquial")
        run(cmd, log_file, args.debug)
    md = f"""# Run Summary: {args.run_id}

## 评论信号
- 书目数: {len(review['books'])}
- 高频负向词: {review['global_negative_top']}

## 机会雷达
- 最高分项目: {top_project['project_id']} ({top_project['total_score']})
- 决策: {top_project['decision']}

## 章节审阅
- overall: {chapter['scores']['overall']}
- hook: {chapter['chapter_hooks']['hook_type']} / {chapter['chapter_hooks']['strength']}

## 运行模式
- debug: {args.debug}
- audit: {args.audit}
- auto_update: {args.auto_update}
- generate: {args.generate}
- generated_file: {generated_out.name if args.generate else 'N/A'}
"""
    summary_out.write_text(md, encoding="utf-8")
    log_line(log_file, f"Pipeline done. Summary: {summary_out}", args.debug)
    print(f"Pipeline done. Summary: {summary_out}")


if __name__ == "__main__":
    main()
