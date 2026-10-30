#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the training material and, therefore, part of the intellectual property.
#   It may not be reused or shared without the explicit, written permission of SupportVectors.
#
#   Use is limited to the duration and purpose of the training at SupportVectors.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""
Package init — loads .env + training config, starts Phoenix tracing,
then imports ``agent`` so ``adk run newsletter`` / ``adk web`` can find
``root_agent`` / ``app``.
"""

from dotenv import load_dotenv
from svlearn.config.configuration import ConfigurationMixin

# Load .env before importing agents so settings/API keys are visible at import time.
load_dotenv()
config = ConfigurationMixin().load_config()

# Phoenix must register BEFORE agents are imported (auto_instrument patches ADK).
from .tracing import setup_tracing  # noqa: E402

setup_tracing()

from . import agent  # noqa: E402, F401 — registers root_agent / app for ADK
