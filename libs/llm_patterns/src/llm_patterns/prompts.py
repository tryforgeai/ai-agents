"""Structured prompts express requirements; they do not prove factual correctness."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PromptSpec:
    context: str
    objective: str
    style: str = "清晰、具体"
    tone: str = "中立"
    audience: str = "初学者"
    response: str = "简洁回答"

    def render(self):
        return "\n\n".join(f"## {label}\n{value}" for label, value in (
            ("Context", self.context), ("Objective", self.objective),
            ("Style", self.style), ("Tone", self.tone),
            ("Audience", self.audience), ("Response", self.response)))


def few_shot_messages(instruction, examples, query):
    messages = [{"role": "system", "content": instruction}]
    for user, assistant in examples:
        messages.extend([{"role": "user", "content": user},
                         {"role": "assistant", "content": assistant}])
    return [*messages, {"role": "user", "content": query}]
