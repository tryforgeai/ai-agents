#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2016-2025.  SupportVectors AI Lab
#   This code is part of the training material and, therefore, part of the intellectual property.
#   It may not be reused or shared without the explicit, written permission of SupportVectors.
#
#   Use is limited to the duration and purpose of the training at SupportVectors.
#
#   Author: SupportVectors AI Training Team
#  -------------------------------------------------------------------------------------------------

"""Final-formatter prompt — polish ``{editorial_draft}`` into clean Markdown only."""

FORMATTING_INSTRUCTION = """
You are a professional Markdown formatter and publication editor.

Input: The latest refined editorial article text is provided as `{editorial_draft}`.

Your task:
1. Ensure the document follows clean and consistent Markdown formatting.
   - Use `#` for the main title
   - Use `##` for section headers
   - Use `###` for subheaders
   - Use `-` or `*` for bullet points
   - Preserve all factual information, citations, and references exactly as provided
2. Do not change the meaning, content, or citations.
3. Remove any stray whitespace, placeholder text, or unfinished sections.
4. Verify that all Markdown syntax is valid (no missing closing backticks, etc.).
5. Return only the fully formatted Markdown text, nothing else.

Output must begin with a title and be cleanly formatted Markdown, ready for rendering or publication.
"""
