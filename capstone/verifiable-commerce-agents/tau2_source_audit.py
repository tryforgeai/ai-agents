"""Read-only, standard-library audit. Usage: python3 tau2_source_audit.py REPO."""
import ast
import collections
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
tree = ast.parse((root / "src/tau2/domains/retail/tools.py").read_text())
writes = []
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if any(isinstance(d, ast.Call) and any(
            isinstance(a, ast.Attribute) and a.attr == "WRITE" for a in d.args
        ) for d in node.decorator_list):
            writes.append(node.name)

def summarize(relative):
    tasks = json.loads((root / relative).read_text())
    no_writes = []
    for task in tasks:
        criteria = task.get("evaluation_criteria") or {}
        if not any(a["name"] in writes for a in criteria.get("actions") or []):
            no_writes.append({"id": task["id"], "reward_basis": criteria.get("reward_basis"),
                              "nl_assertions": criteria.get("nl_assertions"),
                              "communicate_info": criteria.get("communicate_info")})
    return {"file": relative, "tasks": len(tasks),
            "reward_bases": dict(collections.Counter(
                str(t["evaluation_criteria"].get("reward_basis")) for t in tasks)),
            "no_reference_write_tasks": no_writes}

report = {"commit": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
          "method": "Static JSON/AST inspection; no agent run, reward computation or tool execution.",
          "write_tools": writes,
          "collections": [summarize(p) for p in [
              "data/tau2/domains/retail/tasks.json",
              "data/tau2/multilingual/en/retail_tasks_en.json"]]}
print(json.dumps(report, ensure_ascii=False, indent=2))
