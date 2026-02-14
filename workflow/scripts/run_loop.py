#!/usr/bin/env python3
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_once(run_id: str, debug: bool = False, audit: bool = False, auto_update: bool = False, generate: bool = False, generate_chapters: int = 3, colloquial_dialogue: bool = False) -> None:
    cmd = [
        "python",
        str(ROOT / "scripts" / "run_pipeline.py"),
        "--run-id",
        run_id,
    ]
    if debug:
        cmd.append("--debug")
    if audit:
        cmd.append("--audit")
    if auto_update:
        cmd.append("--auto-update")
    if generate:
        cmd.extend(["--generate", "--generate-chapters", str(max(1, generate_chapters))])
    if colloquial_dialogue:
        cmd.append("--colloquial-dialogue")
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="循环运行网文分析流水线，并限制总运行时长。"
    )
    parser.add_argument("--max-seconds", type=int, required=True, help="最大运行时长（秒）。到时后停止新一轮启动。")
    parser.add_argument("--interval-seconds", type=int, default=5, help="每轮之间等待秒数，默认 5。")
    parser.add_argument("--run-id-prefix", default="loop", help="每轮 run-id 前缀，默认 loop。")
    parser.add_argument("--max-runs", type=int, default=0, help="可选：最大轮数上限，0 表示不限制。")
    parser.add_argument("--continue-on-error", action="store_true", help="单轮失败后继续下一轮。")
    parser.add_argument("--debug", action="store_true", help="透传到 pipeline，写 debug 日志。")
    parser.add_argument("--audit", action="store_true", help="透传到 pipeline，生成审查报告。")
    parser.add_argument("--auto-update", action="store_true", help="透传到 pipeline，生成自动更新词典副本。")
    parser.add_argument("--generate", action="store_true", help="透传到 pipeline，生成网文样稿。")
    parser.add_argument("--generate-chapters", type=int, default=3, help="透传到 pipeline 的生成章节数。")
    parser.add_argument("--colloquial-dialogue", action="store_true", help="透传到 pipeline，启用口语化对白。")
    args = parser.parse_args()

    if args.max_seconds <= 0:
        raise ValueError("--max-seconds 必须大于 0")
    if args.interval_seconds < 0:
        raise ValueError("--interval-seconds 不能小于 0")

    start = time.time()
    deadline = start + args.max_seconds
    run_count = 0

    while True:
        now = time.time()
        if now >= deadline:
            print(f"Reached time limit: {args.max_seconds}s. Stop scheduling new runs.")
            break
        if args.max_runs > 0 and run_count >= args.max_runs:
            print(f"Reached run limit: {args.max_runs}. Stop scheduling new runs.")
            break

        run_count += 1
        stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        run_id = f"{args.run_id_prefix}_{run_count}_{stamp}"
        remaining = int(deadline - time.time())
        print(f"[{run_count}] start run_id={run_id}, remaining≈{remaining}s")
        try:
            run_once(run_id, args.debug, args.audit, args.auto_update, args.generate, args.generate_chapters, args.colloquial_dialogue)
        except subprocess.CalledProcessError as err:
            print(f"run failed: run_id={run_id}, return_code={err.returncode}")
            if not args.continue_on_error:
                raise

        now = time.time()
        if now >= deadline:
            print("Time limit reached right after run completion.")
            break

        sleep_for = min(args.interval_seconds, max(0, int(deadline - now)))
        if sleep_for > 0:
            print(f"sleep {sleep_for}s before next run")
            time.sleep(sleep_for)

    total = int(time.time() - start)
    print(f"loop finished: runs={run_count}, elapsed={total}s")


if __name__ == "__main__":
    main()
