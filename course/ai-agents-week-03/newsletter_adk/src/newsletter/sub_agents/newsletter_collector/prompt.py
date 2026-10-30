#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the training material and, therefore, part of the intellectual property.
#   It may not be reused or shared without the explicit, written permission of SupportVectors.
#
#   Use is limited to the duration and purpose of the training at SupportVectors.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""Collector prompts — tell each source agent which tool to call and which key to fill."""

# Note: output_key on the LlmAgent also stores the reply; these strings reinforce that.

# {user_query} is the original request, e.g. "Generate a newsletter about small language models".
_TOPIC = (
    "User request: {user_query}\n"
    "Search for the TOPIC only (e.g. 'small language models'), not the whole sentence — "
    "drop words like 'generate', 'newsletter', 'about'. "
)

SERPER_INSTRUCTION = (
    _TOPIC
    + "Use the Serper tool to gather recent articles about the topic. "
    "Return the raw response from the tool under key `serper_articles`."
)

MEDIASTACK_INSTRUCTION = (
    _TOPIC
    + "Use the MediaStack tool to gather recent articles about the topic. "
    "Return the raw response from the tool under key `mediastack_articles`."
)

NEWSAPI_INSTRUCTION = (
    _TOPIC
    + "Use the NewsAPI tool to gather recent articles about the topic. "
    "Return the raw response from the tool under key `newsapi_articles`."
)

NEWSDATA_INSTRUCTION = (
    _TOPIC
    + "Use the NewsData.io tool to gather recent articles about the topic. "
    "Return the raw response from the tool under key `newsdata_articles`."
)
