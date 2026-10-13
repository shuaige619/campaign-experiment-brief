---
name: campaign-experiment-brief
description: Use when 自媒体或电商活动在两种内容、导购入口或推广方案之间取舍，需要依据访客行为、客服反馈、成本估计与资源约束整理实验简报，尤其尚无 A/B 结果时。
---

# 活动实验与决策简报

读取全部资料、决策问题、指标定义、资源约束与指定输出目录；缺目录先取得目录，其他缺口写待确认。沿用段落 ID，无 ID 用“文件名:行号”。分开观测、成本估计、非随机反馈、假设和约束，保留来源。不同入口名称或行为指标不能擅自视为同义，冲突术语列问题。

“约束”“背景”“建议”等文字标签不是来源 ID；未带原始 ID 的段落必须引用实际文件名和行号，不能把新取的标签填进 source_ids。写后运行 [来源检查器](scripts/check_sources.py)，为每个实际读取的文本文件重复 `--input`，并给 `--result <result.json>`。来源不存在或行号越界时修正真实引用，再重跑；检查器不证明结论蕴含，仍需核对原句。

按原指标的分子/分母核算比率；找到详情入口不等于购买、转化或完成入门。计划人数不当实际样本，预计提升不当已实现收益，百分比提升与百分点不同。比较方案是否落在资源约束内时注明成本仍是估计；可逆小实验与正式上线决定分开，不补造负责人承诺。

给出可执行的验证草案：保留来源已有的计划样本和观察窗口，标“来源计划、尚未执行”，可以沿用于草案。每项参数区分来源计划、建议与待确认；缺参数提出具体建议假设，不能将整个方案留空。写唯一主指标和分母，并给记录方法，例如按日期、版本、去重访客与目标动作留记录，期末按相同窗口计算两组比例。默认方向性草案为：同口径指标上升且资源未超约束，建议负责人审阅是否进入下一轮；指标下降、口径未统一、采集不完整或超预算，暂停比较/推进并修正。来源已有规则优先，新增条件标建议待确认。未启动不能选统计赢家；缺效应/随机分配等信息时不凭人数或天数判断功效；轶事不证明因果，不能保证提升。

“每组预计若干人”只说明每组计划人数，不说明有几组、对照是什么或如何分配。材料未明确的组数、对照、变体和随机分配一律作为建议或待确认，不写“来源计划已含两组”。source_plan 参数的 value 要直接保留所引原句里的数值/短语；需要改写成新的指标或对照定义时标 suggested。检查器核对来源计划值是否实际出现在所引原句，并检查报告里的分组来源归属；运行时同时给 `--report <report.md>`。

在指定目录真实写入 UTF-8 `report.md`、`result.json`。报告先给条件式建议，再列证据、约束、方案比较、实验草案和待确认。JSON 顶层含 `skill`（本技能名）、`source_ids`、`evidence`、`metrics`、`options`、`experiments`、`recommendations`、`questions`，后六项为数组。evidence 含 claim/type/source_ids；metric 含 name/numerator/denominator/value/source_ids；option 含 name/effort/unit/feasible/source_ids；experiment 含 hypothesis/variants/metric/denominator/duration/measurement/decision_rule/pending/source_ids，并以 parameters 数组记录 name/value/kind/source_ids（kind 为 source_plan、suggested 或 pending）；建议与问题各含 text/source_ids。未知用 null 或空数组。

机器字段采用固定类型：metric 的 numerator、denominator、value 为实际数字或 null，option 的 effort 为数字或 null；单位、估计状态与指标定义放 unit、note 或 definition，不拼进数值字段。已观测比例填写来源里的实际分子、分母，并用 value=分子/分母核算；未来实验的指标定义放 experiments，不能替代已观测 metrics 的计数。检查器同时检查这些类型与可复算比例。报告只用真实可定位的 ID/行号，不在已正确的记录 ID 前拼接未经核对的行号。

写后回读 JSON，核对计算、原始指标标签、所有判断来源与设计参数的建议标识，报告与 JSON 一致。最终返回真实路径和缺口；不启动投放、修改活动或替负责人拍板。
