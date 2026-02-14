#!/usr/bin/env python3
import argparse
import json
import random
from pathlib import Path


OPENING_SCENES = [
    "凌晨的风裹着潮气，{protagonist}站在{scene}前，手机里那条催债消息还亮着。",
    "{scene}的灯一盏接一盏熄灭，只有{protagonist}还盯着屏幕上那串刺眼的数字。",
    "雨点砸在{scene}的铁皮顶上，{protagonist}握紧口袋里最后一张车票。",
]

TWISTS = [
    "他以为只是一次普通试炼，却在后台日志里看到了自己的旧档案。",
    "所有人都认定他会让步时，系统弹出一条从未公开的隐藏协议。",
    "门后的不是敌人，而是失踪多年的同伴，带着足以改写规则的证据。",
]

HOOKS = [
    "他刚要开口，走廊尽头忽然传来第二道脚步声。",
    "就在协议即将签下的一刻，屏幕跳出一条只给他看的警告。",
    "她报出了一个不可能知道的代号，现场瞬间安静。",
]

COLLOQUIAL_FILLERS = ["说白了", "你要真问", "讲真", "这事儿", "不对劲"]
REACTIONS = [
    "他先是愣了一秒，随即下意识后退半步，手指在桌沿轻轻敲了两下。",
    "她眯起眼，呼吸明显变浅，语速却故意放慢，像在给自己争取判断时间。",
    "他没立刻回答，只把视线从门口移到对方手腕，先确认危险源再开口。",
]


def pick_unmet_desire(market_signal: dict) -> str:
    top_negative = market_signal.get("global_negative_top", {})
    if not top_negative:
        return "高压现实下的安全感与被尊重"
    top_word = next(iter(top_negative.keys()))
    mapping = {
        "注水": "高密度有效剧情，不拖沓的爽感",
        "降智": "高智商博弈与角色可信决策",
        "慢": "快节奏推进与短周期兑现",
        "套路": "熟悉框架里的反套路惊喜",
    }
    return mapping.get(top_word, f"围绕“{top_word}”的反向满足")


def build_outline(theme: str, unmet_desire: str, conflict: str, chapters: int) -> list[dict]:
    outline = []
    for i in range(1, chapters + 1):
        if i <= max(1, chapters // 3):
            stage = "欲望建模"
        elif i < chapters:
            stage = "冲突升级"
        else:
            stage = "兑现与反转"
        outline.append(
            {
                "chapter": i,
                "stage": stage,
                "goal": f"围绕未被满足欲望“{unmet_desire}”推进阶段目标{i}",
                "conflict": f"{conflict}（第{i}章强化）",
            }
        )
    return outline


def dialogue_pair(protagonist: str, colloquial: bool) -> str:
    filler = random.choice(COLLOQUIAL_FILLERS) + "，" if colloquial else ""
    return (
        f"“{filler}你是想让我现在就认输？”{protagonist}抬眼。\n"
        "“我只是在提醒你，规则从来不是写给弱者的。”对方笑了笑。"
    )


def generate_text(
    theme: str,
    protagonist: str,
    conflict: str,
    chapters: int,
    seed: int,
    scene: str,
    unmet_desire: str,
    colloquial: bool,
) -> str:
    random.seed(seed)
    outline = build_outline(theme, unmet_desire, conflict, chapters)

    lines = [
        f"# 自动生成网文样稿：{theme}",
        "",
        "## 商品化定位",
        f"- 类型/赛道：{theme}",
        f"- 目标读者未满足欲望：{unmet_desire}",
        f"- 主角：{protagonist}",
        f"- 核心冲突：{conflict}",
        f"- 章节数：{chapters}",
        "",
        "## 章节大纲",
    ]
    for item in outline:
        lines.append(
            f"- 第{item['chapter']}章（{item['stage']}）：{item['goal']}；冲突：{item['conflict']}"
        )

    lines.append("\n## 正文草稿\n")
    for item in outline:
        opening = random.choice(OPENING_SCENES).format(protagonist=protagonist, scene=scene)
        twist = random.choice(TWISTS)
        hook = random.choice(HOOKS)
        reaction = random.choice(REACTIONS)
        body = (
            f"### 第{item['chapter']}章\n"
            f"{opening}\n\n"
            f"{protagonist}此刻的目标很简单：{item['goal']}。"
            f"但现实把问题推向更危险的方向——{item['conflict']}。\n"
            f"{dialogue_pair(protagonist, colloquial)}\n\n"
            f"【场景反应】{reaction}\n"
            f"{twist}"
            f"他必须在信任与生存之间做出选择。\n\n"
            f"【章末钩子】{hook}\n"
        )
        lines.append(body)

    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="自动生成网文样稿（市场洞察+写作手法模板版）")
    p.add_argument("--theme", default="都市逆袭")
    p.add_argument("--protagonist", default="林砚")
    p.add_argument("--conflict", default="在高压竞争中守住底线并完成阶层跃迁")
    p.add_argument("--unmet-desire", default="高压现实下的安全感与被尊重")
    p.add_argument("--market-signal", help="可选：review_signals JSON，用于自动推断未满足欲望")
    p.add_argument("--chapters", type=int, default=3)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--scene", default="旧工业园")
    p.add_argument("--colloquial", action="store_true", help="对白增加口语化表达")
    p.add_argument("--output", required=True)
    p.add_argument("--meta-output", help="可选：输出生成参数元数据 JSON")
    args = p.parse_args()

    unmet_desire = args.unmet_desire
    if args.market_signal:
        signal = json.loads(Path(args.market_signal).read_text(encoding="utf-8"))
        unmet_desire = pick_unmet_desire(signal)

    text = generate_text(
        theme=args.theme,
        protagonist=args.protagonist,
        conflict=args.conflict,
        chapters=max(1, args.chapters),
        seed=args.seed,
        scene=args.scene,
        unmet_desire=unmet_desire,
        colloquial=args.colloquial,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")

    if args.meta_output:
        meta = {
            "theme": args.theme,
            "protagonist": args.protagonist,
            "conflict": args.conflict,
            "unmet_desire": unmet_desire,
            "chapters": max(1, args.chapters),
            "seed": args.seed,
            "scene": args.scene,
            "colloquial": args.colloquial,
            "output": str(out_path),
        }
        Path(args.meta_output).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Generated novel draft: {out_path}")


if __name__ == "__main__":
    main()
