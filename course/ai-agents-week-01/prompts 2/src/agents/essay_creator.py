# -------------------------------------------------------------------------------------------
#  Copyright (c) 2024.  SupportVectors AI Lab
#
#  This code is part of the AI Lab Book companion repository.
#  It is released under the MIT License - see the LICENSE file at the repository root.
#
#  Copyright (c) 2016-2026 SupportVectors AI Lab.
#
#  Author: SupportVectors AI Training
# -------------------------------------------------------------------------------------------

import openai
import os

import instructor
from pydantic import BaseModel, Field
from rich import print as rprint
from dotenv import load_dotenv
from typing import Optional
load_dotenv()

class SearchResult(BaseModel):
    title: str = Field(description="The title of the search result")
    url: str = Field(description="The url of the search result")
    summary: str = Field(description="The summarized version of the content in 5000 words or less")

class WebSearchResults(BaseModel):
    search_query: str = Field(description="The search query used to find the most relevant 5 facts on the topic of '{topic}'")
    search_results: list[SearchResult] = Field(description="The most relevant 5 facts on the topic of '{topic}'")

class Glossary(BaseModel):
    glossary: dict[str, str] = Field(description="A dictionary of at least 10 important keywords and their definitions that are relevant to the essay")

class Essay(BaseModel):
    title: str = Field(description="A creative title for the essay")
    reference_urls: list[str] = Field(description="The reference urls used to write the essay")
    glossary: Optional[dict[str, str]] = Field(None, description="A dictionary of at least 10 important keywords and their definitions that are relevant to the essay")
    essay: str = Field(description='''The essay on the topic of '{topic}' in not less than 5000 words 
    structured as a markdown document with at least 5 sections.  The sections should be:
    1. Introduction
    2. Body
    3. Conclusion
    4. References
    5. Glossary''')

# The essay agent defaults to the larger gpt-5 tier: it drives a web_search tool
# call and a 5000-word structured essay, where the small tier noticeably cuts
# corners. Set ESSAY_MODEL=gpt-5-mini for a cheaper (weaker) run.
ESSAY_MODEL = os.getenv("ESSAY_MODEL", "gpt-5")

_mode = instructor.Mode.TOOLS
client = instructor.from_openai(openai.OpenAI(base_url="https://api.openai.com/v1"), mode=_mode)

topic = "Vector Database"

# Stage 1a: run the ACTUAL web search with a plain client via the Responses API.
# This cannot go through instructor: instructor injects its own extraction tool
# and forces the model to call it (tool_choice), which displaces the hosted
# web_search tool - the model then just fills the schema from memory and
# returns an empty search_results list.
raw_search = openai.OpenAI(base_url="https://api.openai.com/v1").responses.create(
    model=ESSAY_MODEL,
    tools=[{"type": "web_search"}],
    input=(f"Search the web and return the most relevant 5 facts on the topic of "
           f"'{topic}'. For each fact, include the source URL."),
)
search_text = raw_search.output_text
rprint(search_text)

# Stage 1b: structure the findings with instructor (no tools needed here).
search_results = client.chat.completions.create(
        model=ESSAY_MODEL,
        response_model=WebSearchResults,
        messages=[
            {"role": "system", "content": "You extract structured data from text. Use ONLY the facts and URLs present in the text."},
            {"role": "user", "content": f"Extract the search query and the facts (with their source URLs) from this web-search summary about '{topic}':\n\n{search_text}"}],
    )
rprint(search_results)

essay = client.chat.completions.create(
    model=ESSAY_MODEL,
    response_model=Essay,

    messages=[
        {"role": "system", "content": "You are a helpful assistant that will write an essay on a specified topic using the search results retrieved from the web"},
        {"role": "user", "content": f'''Write an essay on the topic of 
        \n 
        '{topic}' 
        \n 
        using the following search results: 
        \n 
        {search_results.model_dump_json(indent=2)}
        \n 
        The essay should be structured as a JSON object with the following fields:
        - title: a creative title for the essay
        - reference_urls: a list of reference urls
        - essay: the essay on the topic of '{topic}' in not less than 5000 words structured as a markdown document with at least 4 sections.  The sections should be:
        1. Introduction
        2. Body
        3. Conclusion
        4. References
        \n 
        Include a creative title for the essay, and the list of reference urls
        '''}],
)

glossary = client.chat.completions.create(
    model=ESSAY_MODEL,
    response_model=Glossary,

    messages=[
        {"role": "system", "content": "You are a helpful assistant that will complete the glossary of the essay passed in"},
        {"role": "user", "content": f'''Write a glossary of the essay passed in
        \n 
        {essay.model_dump_json(indent=2)}
        \n 
        The glossary should be a dictionary of at least 10 important keywords and their definitions that are relevant to the essay
        \n 
        The glossary should be structured as a JSON object with the following fields:
        - glossary: a dictionary of at least 10 important keywords and their definitions that are relevant to the essay
        '''}]
)

essay.glossary = glossary.glossary

with open("essay.json", "w") as f:
    f.write(essay.model_dump_json(indent=2))

rprint(essay)

with open("essay.md", "w") as f:
    f.write(essay.essay)


