#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the AI Lab Book companion repository.
#   It is released under the MIT License - see the LICENSE file at the repository root.
#
#   Copyright (c) 2016-2026 SupportVectors AI Lab.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------
from pathlib import Path

from dotenv import load_dotenv

# Load before svlearn reads BOOTCAMP_ROOT_DIR at import time. Notebooks run
# with cwd under docs/, so the path is this project's .env, not the cwd.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from svlearn.config.configuration import ConfigurationMixin

config = ConfigurationMixin().load_config()
