# =============================================================================
# Filename: output_tests.py
#
# Short Description: Input → expected-output tests for skill scripts and skill
#                    behaviour (the procedure applied by an LLM).
#
# Creation date: 2026-10-07
# Author: SupportVectors AI Training Team
# =============================================================================
"""Test what a skill *produces*, not just what its SKILL.md *says*.

Learning overview
--------------------
Firing tests check the description (I). Validation tests check the text of
the procedure (π). Neither shows that the skill, applied to a real input,
gives a good output. This module adds two output-level test types:

**Script tests** (``tests/script_cases.yaml``) — run a bundled script with an
input and compare its stdout / exit code. Deterministic and free: no LLM.
Arguments are passed the way ADK's ``run_skill_script`` passes them (a list is
passed as-is; ``positional_args`` are preceded by ``--``), and no stdin is
given, because the agent cannot provide stdin either.

**Behaviour tests** (``tests/behaviour_cases.yaml``) — give an LLM the skill's
SKILL.md body and its L3 files as instructions, send a sample user input, and
check the reply with ``must_contain`` / ``must_not_contain`` / ``must_match``
(regex) / ``min_matches`` (regex + count). Costs one LLM call per case, and
results can vary between runs, so treat a single failure as a signal to rerun
before concluding the procedure is wrong.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import yaml

from skills.paths import skill_dir
from skills.skill_loader import load_skill

BehaviourRunner = Callable[[str, str], str]
"""``runner(skill_name, user_input) -> reply text``."""

_SCRIPT_TIMEOUT_SECONDS = 30
_REPLY_EXCERPT_CHARS = 300
_L3_DIRS = ("references", "assets", "scripts")
_TEXT_SUFFIXES = (".md", ".txt", ".py", ".sh", ".json", ".yaml", ".yml", ".csv")


@dataclass(frozen=True)
class OutputReport:
    """Aggregate results for script or behaviour tests of one skill."""

    skill_name: str
    total: int
    correct: int
    accuracy: float
    failures: tuple[str, ...]


def _load_cases(*, skill_name: str, filename: str) -> list[dict[str, Any]]:
    path = skill_dir(name=skill_name) / "tests" / filename
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return list(data.get("cases", []))


def _case_label(*, case: dict[str, Any], index: int) -> str:
    return str(case.get("name") or f"case {index + 1}")


def _check_text(*, text: str, case: dict[str, Any]) -> list[str]:
    """Apply the shared output checks; return a list of problems."""
    problems: list[str] = []
    for needle in case.get("must_contain", []) or []:
        if needle not in text:
            problems.append(f"missing {needle!r}")
    for needle in case.get("must_not_contain", []) or []:
        if needle in text:
            problems.append(f"contains forbidden {needle!r}")
    for pattern in case.get("must_match", []) or []:
        if re.search(pattern, text, flags=re.MULTILINE) is None:
            problems.append(f"no match for /{pattern}/")
    min_matches = case.get("min_matches")
    if min_matches:
        pattern = str(min_matches["pattern"])
        wanted = int(min_matches["count"])
        found = len(re.findall(pattern, text, flags=re.MULTILINE))
        if found < wanted:
            problems.append(f"/{pattern}/ matched {found} times, need {wanted}")
    return problems


def _report(*, skill_name: str, outcomes: list[tuple[str, list[str]]]) -> OutputReport:
    """Build a report from ``(label, problems)`` outcomes."""
    failures = [
        f"{label}: {'; '.join(problems)}" for label, problems in outcomes if problems
    ]
    total = len(outcomes)
    correct = total - len(failures)
    return OutputReport(
        skill_name=skill_name,
        total=total,
        correct=correct,
        accuracy=correct / total if total else 1.0,
        failures=tuple(failures),
    )


# --------------------------------------------------------------------------
# Script tests (deterministic, no LLM)
# --------------------------------------------------------------------------


def _script_argv(*, case: dict[str, Any]) -> list[str]:
    """Build argv the way ADK's run_skill_script does."""
    argv = [str(arg) for arg in case.get("args", []) or []]
    positional = case.get("positional_args")
    if positional:
        argv += ["--", *(str(arg) for arg in positional)]
    return argv


def run_script_case(*, skill_name: str, case: dict[str, Any]) -> list[str]:
    """Run one script case and return its problems (empty list = pass)."""
    folder = skill_dir(name=skill_name)
    script = folder / str(case["script"])
    if not script.is_file():
        return [f"script not found: {case['script']}"]
    completed = subprocess.run(
        [sys.executable, str(script), *_script_argv(case=case)],
        cwd=folder,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=_SCRIPT_TIMEOUT_SECONDS,
        check=False,
    )
    stdout = completed.stdout.strip()
    problems: list[str] = []
    expected_code = int(case.get("exit_code", 0))
    if completed.returncode != expected_code:
        problems.append(f"exit code {completed.returncode}, expected {expected_code}")
    if "expect_stdout" in case and stdout != str(case["expect_stdout"]).strip():
        problems.append(f"stdout {stdout!r}, expected {str(case['expect_stdout'])!r}")
    problems += _check_text(text=stdout, case=case)
    return problems


def evaluate_scripts(*, skill_name: str) -> OutputReport:
    """Run ``tests/script_cases.yaml`` for one skill."""
    cases = _load_cases(skill_name=skill_name, filename="script_cases.yaml")
    outcomes = [
        (
            _case_label(case=case, index=index),
            run_script_case(skill_name=skill_name, case=case),
        )
        for index, case in enumerate(cases)
    ]
    return _report(skill_name=skill_name, outcomes=outcomes)


# --------------------------------------------------------------------------
# Behaviour tests (the procedure applied by an LLM)
# --------------------------------------------------------------------------


def build_skill_prompt(*, skill_name: str) -> str:
    """System prompt: the SKILL.md body plus every L3 text file, inline.

    The real agent opens L3 files with tools; here they are inlined so one LLM
    call applies the whole skill. Scripts cannot run in this test, so the
    model is asked to apply their effect itself.
    """
    skill = load_skill(name=skill_name)
    folder = skill_dir(name=skill_name)
    parts = [
        f"You are applying the skill '{skill_name}'. Follow its procedure "
        "exactly and reply with the finished result for the user.",
        "Scripts cannot be run here: where the procedure says to run a script, "
        "apply what the script would do yourself.",
        "# SKILL.md",
        skill.instructions,
    ]
    for sub in _L3_DIRS:
        base = folder / sub
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix in _TEXT_SUFFIXES and "__pycache__" not in path.parts:
                rel = path.relative_to(folder).as_posix()
                parts.append(f"# {rel}\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def llm_behaviour_runner(skill_name: str, user_input: str) -> str:
    """Default runner: one chat completion against the configured endpoint."""
    import litellm

    from skills.llm_config import resolve_llm_settings

    litellm.disable_aiohttp_transport = True
    settings = resolve_llm_settings()
    response = litellm.completion(
        model=settings.model,
        api_base=settings.base_url,
        api_key=settings.api_key,
        messages=[
            {"role": "system", "content": build_skill_prompt(skill_name=skill_name)},
            {"role": "user", "content": user_input},
        ],
    )
    return response.choices[0].message.content or ""


def evaluate_behaviour(
    *,
    skill_name: str,
    runner: BehaviourRunner | None = None,
) -> OutputReport:
    """Run ``tests/behaviour_cases.yaml`` for one skill through ``runner``."""
    run = runner or llm_behaviour_runner
    cases = _load_cases(skill_name=skill_name, filename="behaviour_cases.yaml")
    outcomes = []
    for index, case in enumerate(cases):
        label = _case_label(case=case, index=index)
        try:
            reply = run(skill_name, str(case["input"]))
            problems = _check_text(text=reply, case=case)
            if problems:
                excerpt = " ".join(reply.split())[:_REPLY_EXCERPT_CHARS]
                problems.append(f"reply began: {excerpt!r}")
        except Exception as exc:  # LLM/network errors count as failures
            problems = [f"runner error: {exc}"]
        outcomes.append((label, problems))
    return _report(skill_name=skill_name, outcomes=outcomes)


def _manifest_names() -> list[str]:
    from skills.skill_loader import load_manifest

    _, _, entries = load_manifest()
    return [entry.name for entry in entries]


def evaluate_scripts_library(*, names: list[str] | None = None) -> list[OutputReport]:
    """Script tests for every skill that has ``tests/script_cases.yaml``."""
    names = names or _manifest_names()
    return [
        evaluate_scripts(skill_name=name)
        for name in names
        if (skill_dir(name=name) / "tests" / "script_cases.yaml").is_file()
    ]


def evaluate_behaviour_library(
    *,
    names: list[str] | None = None,
    runner: BehaviourRunner | None = None,
) -> list[OutputReport]:
    """Behaviour tests for every skill that has ``tests/behaviour_cases.yaml``."""
    names = names or _manifest_names()
    return [
        evaluate_behaviour(skill_name=name, runner=runner)
        for name in names
        if (skill_dir(name=name) / "tests" / "behaviour_cases.yaml").is_file()
    ]
