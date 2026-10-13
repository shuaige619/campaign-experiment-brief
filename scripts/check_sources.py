#!/usr/bin/env python3
"""Read-only source-ID and file:line checks for decision briefs from text inputs."""
import argparse
import json
from pathlib import Path
import re
import math
import sys


def references(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "source_ids" and isinstance(item, list):
                yield from item
            elif isinstance(item, (dict, list)):
                yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)


def check(inputs, result, report_text=""):
    source_ids = set()
    lines = {}
    source_text={}
    all_text=[]
    for path in inputs:
        if path.name in lines:
            raise ValueError("同名输入文件无法唯一定位，请先明确引用名称")
        text = path.read_text(encoding="utf-8-sig")
        all_text.append(text)
        for number,line in enumerate(text.splitlines(),1):
            source_text[f"{path.name}:{number}"]=line
            for sid in re.findall(r"\[([A-Za-z0-9][A-Za-z0-9_-]*)\]",line): source_text[sid]=line
        source_ids.update(re.findall(r"\[([A-Za-z0-9][A-Za-z0-9_-]*)\]", text))
        lines[path.name] = len(text.splitlines())
    invalid = []
    refs = list(references(result))
    for ref in refs:
        if isinstance(ref, str) and ref in source_ids:
            continue
        match = re.fullmatch(r"(?:.*/)?([^/:]+):(\d+)", ref) if isinstance(ref, str) else None
        if not match or not 1 <= int(match[2]) <= lines.get(match[1], 0):
            invalid.append(ref)
    type_errors=[]
    numeric=lambda x: x is None or (type(x) in (int,float) and math.isfinite(x))
    for index,metric in enumerate(result.get("metrics",[])):
        for key in ["numerator","denominator","value"]:
            if key not in metric or not numeric(metric[key]): type_errors.append(f"metrics[{index}].{key}: expected number/null")
        numerator,denominator,value=(metric.get(k) for k in ["numerator","denominator","value"])
        if all(type(x) in (int,float) for x in [numerator,denominator]):
            if denominator==0 and value is not None: type_errors.append(f"metrics[{index}]: zero denominator requires null")
            elif denominator!=0 and (type(value) not in (int,float) or not math.isclose(value,numerator/denominator,rel_tol=1e-8,abs_tol=1e-8)): type_errors.append(f"metrics[{index}]: ratio does not match counts")
    for index,option in enumerate(result.get("options",[])):
        if "effort" not in option or not numeric(option["effort"]): type_errors.append(f"options[{index}].effort: expected number/null")
    attribution_errors=[]
    for index,experiment in enumerate(result.get("experiments",[])):
        for parameter in experiment.get("parameters",[]):
            if parameter.get("kind")!="source_plan": continue
            value=parameter.get("value")
            evidence="\n".join(source_text.get(str(ref),source_text.get(Path(str(ref)).name,"")) for ref in parameter.get("source_ids",[]))
            compact=lambda text: re.sub(r"\s","",str(text))
            if value is None or not compact(value) or compact(value) not in compact(evidence):
                attribution_errors.append(f"experiments[{index}].{parameter.get('name')}: source_plan value is not in cited source; preserve source wording or mark suggestion")
    if not re.search(r"两组|2组|两臂|2臂|对照组", "\n".join(all_text)) and re.search(r"来源计划(?:含|有|包括|明确).{0,6}两组",report_text):
        attribution_errors.append("report: source does not specify two groups")
    return {"passed":bool(refs) and not invalid and not type_errors and not attribution_errors,"invalid_references":invalid,"type_errors":type_errors,"attribution_errors":attribution_errors,"references_checked":len(refs),
            "allowed_record_ids":sorted(source_ids),"input_line_counts":lines,"manual_required":True,
            "scope":"Reference existence only; evidence entailment must be independently reviewed."}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,action="append",required=True)
    parser.add_argument("--result",type=Path,required=True)
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    try:
        report_path=args.report or args.result.with_name("report.md")
        report=check(args.input,json.loads(args.result.read_text(encoding="utf-8")),report_path.read_text(encoding="utf-8"))
    except (OSError,ValueError,TypeError) as error:
        report={"passed":False,"error":str(error),"manual_required":True}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    sys.exit(0 if report["passed"] else 1)
