#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#  -------------------------------------------------------------------------------------------------
"""Agent skills demo — Google ADK agent with a filesystem skill library.

Import ``root_agent`` for ADK CLI/web (defaults to preload agent).

Run both loading strategies in ADK web::

    adk web src/skills/agents

Learning path: read ``docs/LEARNING_GUIDE.md`` before this package. Skills live in
``skills/`` at repo root; this package only loads them into ADK.
"""

from dotenv import load_dotenv
from svlearn.config.configuration import ConfigurationMixin

from skills.paths import project_root

load_dotenv()

config = ConfigurationMixin().load_config(config_file=project_root() / "config.yaml")

__all__ = ["config", "root_agent"]


def __getattr__(name: str):
    # Lazy import: unit tests can import skill_loader without LiteLLM extensions.
    if name == "root_agent":
        from skills.agents.preload.agent import root_agent as agent

        return agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
