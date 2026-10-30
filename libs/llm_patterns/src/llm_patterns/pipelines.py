"""Bounded multi-call patterns; caller supplies model/backend functions."""
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Step:
    name: str
    run: Callable[[dict[str, Any]], Any]


def run_chain(value, steps):
    """Each step sees original input AND every prior named result."""
    steps = list(steps)
    names = [step.name for step in steps]
    if any(not n or n == "input" for n in names) or len(set(names)) != len(names):
        raise ValueError("step names must be unique, nonempty, and not 'input'")
    state = {"input": value}
    for step in steps:
        state[step.name] = step.run(deepcopy(state))
    return state


def sample_vote(sample, *, samples=3, key=lambda value: value):
    """Separate calls followed by an actual strict-majority vote; ties return None."""
    if samples < 1:
        raise ValueError("samples must be positive")
    values = [sample() for _ in range(samples)]
    counts = Counter(key(value) for value in values)
    winner, count = counts.most_common(1)[0]
    return {"winner": winner if count > samples / 2 else None,
            "counts": dict(counts), "samples": values,
            "has_majority": count > samples / 2}


def refine(initial, review, revise, *, max_revisions=2):
    """review returns (accepted: bool, feedback); exhaustion is explicit."""
    if max_revisions < 0:
        raise ValueError("max_revisions must be nonnegative")
    value, history = initial, []
    for attempt in range(max_revisions + 1):
        accepted, feedback = review(value)
        if not isinstance(accepted, bool):
            raise TypeError("review acceptance must be a boolean")
        history.append({"value": deepcopy(value), "accepted": accepted, "feedback": feedback})
        if accepted:
            return {"result": value, "status": "accepted", "history": history}
        if attempt < max_revisions:
            value = revise(value, feedback)
    return {"result": value, "status": "exhausted", "history": history}
