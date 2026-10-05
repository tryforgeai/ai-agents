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

"""A sophisticated glossary builder module implementing the Co-Star pattern.

This module provides an advanced implementation of a glossary builder that uses the Co-Star pattern
to generate high-quality glossaries. It uses an OpenAI-hosted model in a two-phase process:
1. Initial draft generation
2. Self-criticism and refinement

The module requires an OpenAI API key to be set in the environment variables.
"""

from pathlib import Path
from openai import OpenAI
from prompts.model import Glossary, GlossaryTerm, ImportantTerms
from svlearn.common.utils import check_valid_file
from loguru import logger
import os

import instructor
import markdown

from prompts import config
from dotenv import load_dotenv

# Needed for loading env variables (including the OPEN API KEY from .env)
load_dotenv(override=True)

# LLM endpoint options:
#  (a) OpenAI hosted (default): LLM_MODEL=gpt-5-mini, OPENAI_API_KEY required
#  (b) self-hosted OpenAI-compatible server (vLLM / Ollama): set OPENAI_BASE_URL
#      (read natively by the OpenAI client, e.g. http://localhost:11434/v1) and a
#      served model, e.g. LLM_MODEL="llama3.1"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5-mini")

class GlossaryBuilder:
    """A sophisticated glossary builder implementing the Co-Star pattern.
    
    This class provides an advanced implementation for generating glossaries using a two-phase
    approach with the configured model. It first generates a draft version of each term's
    definition, then uses a self-criticism phase to refine and improve the definitions.
    
    Attributes:
        __DRAFT_VERSION_PROMPT_FILE_NAME (str): Path to the prompt file for initial draft generation.
        __REFINEMENT_PROMPT_FILE_NAME (str): Path to the prompt file for term refinement.
        __terms (List[str]): List of terms to be included in the glossary.
        __refined_glossary_items (List[GlossaryTerm]): List of refined glossary terms.
        openai (OpenAI): OpenAI API client instance.
        api: Instructor-wrapped OpenAI client for structured outputs.
    """

    __DRAFT_VERSION_PROMPT_FILE_NAME = "prompts/01_costar_glossary_prompt.md"
    __REFINEMENT_PROMPT_FILE_NAME = "prompts/02_costar_term_refinement_prompt.md"
  
    # -------------------------------------------------------------------------------------------  
    def __init__(self):
        """Initialize the GlossaryBuilder with empty term lists and OpenAI clients."""
        self.__terms = []
        self.openai = OpenAI()
        # Instructor mode: hosted OpenAI models work best with the default tool-calling
        # mode, but most self-hosted OpenAI-compatible servers (vLLM / Ollama) are far
        # more reliable in plain-JSON mode. We switch on OPENAI_BASE_URL: when it is
        # set, the client is talking to a self-hosted server, so use Mode.JSON.
        mode = instructor.Mode.JSON if os.getenv("OPENAI_BASE_URL") else instructor.Mode.TOOLS
        self.api = instructor.from_openai(self.openai, mode=mode)
        
    # ------------------------------------------------------------------------------------------- 
    def fetch_glossary_terms(self) -> ImportantTerms:
        """Fetch a list of important terms for the glossary.
        
        Makes an API call to GPT-4 to identify the most important terms in the field
        of prompt engineering that should be included in the glossary.
        
        Returns:
            ImportantTerms: A model containing a list of important terms.
        """
        
        # Number of glossary terms to build, from config.yaml (glossary.num_terms).
        # Each term costs two further LLM calls (draft + refinement).
        num_terms = int(config.get("glossary", {}).get("num_terms", 3))
        shortlist =  self.api.chat.completions.create(
            model=LLM_MODEL,
            response_model=ImportantTerms,
            messages=[{"role": "system", 
                       "content": "You are an AI expert in Prompt Engineering."},
                      
                      {"role": "user", 
                       "content": ("In the field of prompt engineering, identify the most important terms "
                                   "that should be included in a glossary. Avoid the obvious terms, and focus "
                                   "on the terms that are specific to the field, and whose definitions a casual "
                                   "engineer may not know. Return the rest as a list of terms only, without "
                                   f"definitions. RETURN EXACTLY {num_terms} TERMS.")}],
        )
        
        logger.info(f"Received the list of important terms: {shortlist.important_terms}")
        # LLM count compliance is best-effort, so enforce the budget deterministically:
        # every extra term would cost two more LLM calls (draft + refinement).
        if len(shortlist.important_terms) > num_terms:
            logger.warning(
                f"Model returned {len(shortlist.important_terms)} terms; truncating to {num_terms} per config.yaml"
            )
        self.__terms = shortlist.important_terms[:num_terms]
        return ImportantTerms(important_terms=self.__terms)

    # -------------------------------------------------------------------------------------------
    def build(self) -> Glossary:
        """Build a complete glossary using the Co-Star pattern.
        
        This method orchestrates the entire glossary building process:
        1. Loads the necessary prompts
        2. Fetches the list of important terms
        3. Generates and refines definitions for each term
        4. Compiles the final glossary
        
        Returns:
            Glossary: A complete glossary object containing all terms and their definitions.
        """

        
        self.draft_version_prompt = self.load_draft_version_prompt()
        self.refinement_prompt = self.load_refinement_prompt()
        
        # first, let us fetch the list of glossary terms
        
        self.fetch_glossary_terms()

        logger.info(f"Fetching glossary terms: {self.__terms}")
        
        # Now, make a call to the OpenAI API to generate the glossary-entry for each term,
        # one by one.
        self.__refined_glossary_items = []
        for index, term in enumerate(self.__terms):
            logger.info(f"Building glossary item: {index} for term: {term}")
            self.build_for_term(term)
            
        glossary = self.build_glossary_from_terms()

        return glossary

    # -------------------------------------------------------------------------------------------
    def load_draft_version_prompt(self) -> str:
        """Load the prompt for generating initial draft definitions.
        
        Returns:
            str: The contents of the draft version prompt file.
        """
        file = Path.cwd() / self.__DRAFT_VERSION_PROMPT_FILE_NAME
        logger.info(f"Reading draft version prompt from file: {file}")
        
        check_valid_file(file)

        prompt = file.read_text(encoding="utf-8")
        return prompt
    
    # -------------------------------------------------------------------------------------------
    def load_refinement_prompt(self) -> str:
        """Load the prompt for refining term definitions.
        
        Returns:
            str: The contents of the refinement prompt file.
        """
        file = Path.cwd() / self.__REFINEMENT_PROMPT_FILE_NAME
        logger.info(f"Reading term refinement prompt from file: {file}")
        
        check_valid_file(file)

        prompt = file.read_text(encoding="utf-8")
        return prompt

    # -------------------------------------------------------------------------------------------
    def build_for_term(self, term: str) -> None:
        """Generate and refine a definition for a single term.
        
        This method implements the two-phase Co-Star pattern for a single term:
        1. Generates an initial draft definition
        2. Uses self-criticism to refine and improve the definition
        
        Args:
            term (str): The term to generate a definition for.
        """
        logger.info(f"Creating glossary term for: {term}")
            # Call the OpenAI API to generate the glossary-term definition
        glossary_term = self.api.chat.completions.create(model=LLM_MODEL, 
                                                   messages=[{"role": "system", 
                                                              "content": self.draft_version_prompt}, 
                                                             {"role": "user", "content": f"Create a glossary-entry for {term}."}
                                                             ],
                                                   response_model=GlossaryTerm,
                                                   )
        logger.info(f"Received draft version of the glossary term: {glossary_term}")
        
        # Self-criticism phase and improvement.
        logger.info (f"Now entering the self-criticism and improvement phase for the glossary term: {term}") 
        user_prompt = f"Glossary term: {term}\n\nDefinition: {glossary_term.definition}"
        
        glossary_term_refined = self.api.chat.completions.create(model=LLM_MODEL, 
                                                   messages=[{"role": "system", "content": self.refinement_prompt}, 
                                                             {"role": "user", "content": user_prompt}
                                                             ],
                                                   response_model=GlossaryTerm,
                                                   )
        
        self.__refined_glossary_items.append(glossary_term_refined)
    
    # -------------------------------------------------------------------------------------------
    def build_glossary_from_terms(self) -> Glossary:
        """Compile all refined terms into a final glossary.
        
        Takes all the refined glossary terms and compiles them into a final
        glossary object, including HTML formatting for display.
        
        Returns:
            Glossary: The complete glossary containing all terms and their definitions.
        """
        glossary = Glossary(subject="Prompt Engineering", terms={})
        sorted_terms = sorted(self.__refined_glossary_items, key=lambda term: term.term)
        
        html = []
        for term in sorted_terms:
            glossary.terms[term.term] = term
            html.append(f"<h2>{term.term}</h2>")
            
            html.append(markdown.markdown(term.definition))
            html.append("<hr/>")
           
        self.html = '\n'.join(html)
        
        return glossary

# -------------------------------------------------------------------------------------------
if __name__ == "__main__":
    
    results_dir = config["paths"]["results_dir"]
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    output_file = Path(f"{results_dir}/co_star_glossary.json")
    html_file = Path(f"{results_dir}/co_star_glossary.html")
    
    glossary_builder = GlossaryBuilder()
    glossary = glossary_builder.build()
    
    output_file.write_text(glossary.model_dump_json(), encoding="utf-8")
    html_file.write_text(glossary_builder.html, encoding="utf-8")
    print(glossary)
    