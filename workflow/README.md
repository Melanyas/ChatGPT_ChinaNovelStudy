# 网文商品化自动工作流（MVP v2）

本工作流的目标不是“随便写文”，而是：

1. 通过市场反馈识别读者未被满足的欲望点；
2. 结合类型/赛道做可商品化选题；
3. 用可复用写作技法（对白口语化、场景反应、钩子）生成文本；
4. 通过自动审阅与阈值审查持续迭代，稳定输出更有市场适配度的网文商品。

## 功能板块

- **市场洞察层**：评论信号提取（情绪、负向关键词）+ 项目雷达评分。
- **生成层**：根据赛道与未满足欲望自动生成网文样稿。
- **写法增强层**：对白口语化、角色反应、章末钩子与模板再创造。
- **审阅层**：语法/情绪/动作/对白/口语化/反应/技法再创造打分。
- **治理层**：阈值审查（pass/fail）、debug 日志、词典弱自更新。
- **迭代层**：循环运行（时间上限、轮次上限、错误续跑）。

## 目录结构

- `config/`：情绪词典、雷达权重、审查阈值
- `input/`：评论快照、项目特征、章节样例
- `scripts/`：执行脚本
- `artifacts/`：每轮输出结果

## 一键运行（标准流程）

```bash
python workflow/scripts/run_pipeline.py --run-id demo --generate --generate-chapters 3 --colloquial-dialogue
```

典型输出：

- `review_signals_<run_id>.json`：评论洞察
- `radar_scores_<run_id>.csv`：赛道评分与决策
- `chapter_audit_<run_id>.json`：写法审阅
- `generated_novel_<run_id>.md`：自动生成样稿
- `generated_novel_<run_id>.json`：生成参数元数据
- `summary_<run_id>.md`：本轮摘要

## 自动生成网文文本（独立运行）

```bash
python workflow/scripts/novel_generator.py \
  --output workflow/artifacts/generated_novel_demo.md \
  --meta-output workflow/artifacts/generated_novel_demo.json \
  --theme 都市逆袭 \
  --market-signal workflow/artifacts/review_signals_demo.json \
  --chapters 3 \
  --colloquial
```

说明：
- `--market-signal` 会从评论负向词推断“未满足欲望点”；
- `--colloquial` 会增强对白口语化表达。

## 自动审阅与阈值闸门

```bash
python workflow/scripts/run_pipeline.py --run-id audit_demo --generate --audit --auto-update --colloquial-dialogue
```

新增输出：
- `audit_<run_id>.json`：阈值审查结果（pass/fail）
- `sentiment_lexicon_<run_id>.json`：词典更新副本
- `debug_<run_id>.log`（仅 `--debug` 时）：调试日志

## 循环迭代（时间上限）

```bash
python workflow/scripts/run_loop.py \
  --max-seconds 600 \
  --interval-seconds 10 \
  --run-id-prefix loop \
  --max-runs 0 \
  --continue-on-error \
  --generate \
  --generate-chapters 2 \
  --colloquial-dialogue \
  --audit
```

## Makefile 快捷命令

```bash
make run-workflow RUN_ID=demo GENERATE=1 GENERATE_CHAPTERS=3 COLLOQUIAL_DIALOGUE=1
make run-workflow-loop MAX_SECONDS=120 INTERVAL_SECONDS=10 GENERATE=1 COLLOQUIAL_DIALOGUE=1
make run-generate-novel RUN_ID=demo GENERATE_CHAPTERS=2 COLLOQUIAL_DIALOGUE=1
```

## 方法论要点（简版）

- 市场不是“猜”，而是通过评论信号和评分维度量化；
- 生成不是“堆词”，而是围绕未满足欲望构建冲突与兑现；
- 写法不是“玄学”，而是对白、反应、钩子等可审阅指标；
- 迭代不是“重写”，而是跑一轮→审一轮→改配置→再生成。
