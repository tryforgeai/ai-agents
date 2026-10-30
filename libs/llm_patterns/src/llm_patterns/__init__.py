"""Reusable patterns independent of ADK and any specific model provider."""
from .client import CompletionClient
from .prompts import PromptSpec, few_shot_messages
from .pipelines import Step, run_chain, sample_vote, refine
from .vision import image_data_url, vision_messages
from .tool_loop import Action, Tool, run_tool_loop
from .deterministic import days_between, sum_amounts, routing_report

__all__ = ["CompletionClient", "PromptSpec", "few_shot_messages", "Step",
           "run_chain", "sample_vote", "refine", "image_data_url", "vision_messages",
           "Action", "Tool", "run_tool_loop", "days_between", "sum_amounts", "routing_report"]
