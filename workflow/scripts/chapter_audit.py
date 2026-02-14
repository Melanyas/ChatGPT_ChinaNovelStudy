#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


COLLOQUIAL_WORDS = ["说白了", "讲真", "这事儿", "不对劲", "你要真问"]
REACTION_CUES = ["愣", "后退", "呼吸", "抬眼", "视线", "手指", "停顿"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.strip()]

    issues = []
    for ln in lines:
        if len(ln) > 45 and "，" not in ln and "。" not in ln:
            issues.append({"type": "grammar", "severity": "medium", "evidence": ln, "problem": "句子偏长且缺少停顿", "fix": "增加逗号或拆句"})
        if re.search(r"(很|非常|特别).*(很|非常|特别)", ln):
            issues.append({"type": "style", "severity": "low", "evidence": ln, "problem": "程度副词重复", "fix": "保留一次强调即可"})

    dialogue_lines = [ln for ln in lines if "“" in ln and "”" in ln]
    action_lines = [ln for ln in lines if any(k in ln for k in ["抬", "走", "退", "看", "踏", "停", "握", "敲"])]
    colloquial_hits = sum(1 for ln in lines for w in COLLOQUIAL_WORDS if w in ln)
    reaction_hits = sum(1 for ln in lines for w in REACTION_CUES if w in ln)

    result = {
        "scores": {
            "grammar": max(0, 100 - 8 * len([i for i in issues if i["type"] == "grammar"])),
            "emotion": min(100, 55 + 5 * sum(1 for ln in lines if any(k in ln for k in ["心跳", "发冷", "想起", "沉默"]))),
            "action": min(100, 50 + 6 * len(action_lines)),
            "dialogue": min(100, 45 + 10 * len(dialogue_lines)),
            "script": 70,
            "colloquial": min(100, 55 + 8 * colloquial_hits),
            "reaction": min(100, 50 + 6 * reaction_hits),
            "technique_recreation": min(100, 60 + 5 * sum(1 for ln in lines if "【" in ln and "】" in ln)),
        },
        "issues": issues[:12],
        "chapter_hooks": {
            "hook_type": "crisis" if any("不会再退" in ln or "脚步声" in ln for ln in lines) else "none",
            "strength": 78 if any("不会再退" in ln or "脚步声" in ln for ln in lines) else 40,
            "suggestion": "章末可增加明确对手动作与代价倒计时，增强下一章拉力",
        },
    }
    score_keys = [
        "grammar",
        "emotion",
        "action",
        "dialogue",
        "script",
        "colloquial",
        "reaction",
        "technique_recreation",
    ]
    result["scores"]["overall"] = round(sum(result["scores"][k] for k in score_keys) / len(score_keys), 2)

    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
