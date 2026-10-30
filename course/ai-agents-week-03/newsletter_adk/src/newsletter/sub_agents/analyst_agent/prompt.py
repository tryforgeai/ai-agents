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
Analyst prompt — uses ``{validated_reports}`` from state.
Output shape is enforced by ``AnalysisReport`` (newsletter/schemas.py).
"""

ANALYST_INSTRUCTION = """
You are a news analyst.

Inputs:
- Validated reports: {validated_reports}

Tasks:
1. Use validated_reports for titles, snippets/claims, source metadata, and credibility flags.
2. Identify major topics or themes discussed across the sources.
3. Construct a clear timeline or chronology (if events are dated).
4. Highlight key conflicts, contradictions, or corroborations.
5. Summarize insights clearly and concisely.

Use [] for timeline or conflicts when there is nothing to report.
All findings must come strictly from the provided validated data.
Do not invent facts or open URLs.
"""
