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
In-process tools package (NewsAPI / NewsData).

Serper search and MediaStack live under ``newsletter.mcp.tools``
and are exposed through the FastMCP server.
"""

from dotenv import load_dotenv
from svlearn.config.configuration import ConfigurationMixin

load_dotenv()
config = ConfigurationMixin().load_config()
