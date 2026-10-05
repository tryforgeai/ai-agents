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

"""Data models for the glossary builder system.

This module defines the core data structures used throughout the glossary builder system.
It uses Pydantic models to ensure type safety and data validation for glossary terms,
definitions, and the overall glossary structure.
"""

from typing import List, OrderedDict
from pydantic import BaseModel, Field

class ImportantTerms(BaseModel):
    """A model representing a list of important terms for a glossary.
    
    This model is used to structure the response from the initial term selection phase.
    The number of terms is set by the request (see config.yaml -> glossary.num_terms);
    keep counts OUT of this schema: in instructor's tool-calling mode the field
    description below is embedded in the JSON schema the model fills in, and a count
    written here silently overrides whatever the chat prompt asks for.

    Attributes:
        important_terms (List[str]): Important terms that should be included in the
            glossary. These terms are specific to the field and may not be
            immediately obvious to casual engineers.
    """
    important_terms: List[str] = Field(..., title="Important terms", description="A list of important terms that should be included in a glossary. Avoid the obvious terms, and focus on the terms that are specific to the field, and whose definitions a casual engineer may not know. Return exactly the number of terms the request asks for.",)

# -------------------------------------------------------------------------------------------
class GlossaryTerm(BaseModel):
    """A model representing a single term in the glossary.
    
    This model defines the structure for individual glossary terms, including both the
    term itself and its detailed definition. The definition is expected to be comprehensive
    and technically accurate, with appropriate examples where needed.
    
    Attributes:
        term (str): The term to be defined (e.g., 'Prompt Engineering').
        definition (str): A detailed, technically complete definition of the term,
            at least 300 tokens long. May include itemized components and illustrative
            examples where appropriate.
    """

    term: str = Field(..., title="The term", description="The term to be defined, e.g. 'Prompt Engineering'")
    definition: str = Field(
        ...,
        title="The definition",
        description="""
                            The detailed, technically complete and accurate definition of the term, in the context of Prompt Engineering. This must be at least 300 tokens long. Where necessary, provide itemization of components if that is appropriate. 
                            
                            If illustrative examples are needed, they should be included in the definition.
                            """,
    )


# -------------------------------------------------------------------------------------------


class Glossary(BaseModel):
    """A model representing a complete glossary.
    
    This model serves as the container for all glossary terms, organizing them by
    subject matter and maintaining an ordered dictionary of terms and their definitions.
    
    Attributes:
        subject (str): The subject matter of the glossary (e.g., 'Prompt Engineering').
        terms (OrderedDict[str, GlossaryTerm]): An ordered dictionary mapping terms to
            their GlossaryTerm objects, containing both the term and its definition.
    """

    subject: str = Field(..., title="The subject", description="The subject of the glossary, e.g. 'Prompt Engineering'")
    terms: OrderedDict[str, GlossaryTerm] = Field(
        ...,
        title="The terms",
        description="A collection of GlossaryTerm objects, each representing a term and its definition.",
    )


# -------------------------------------------------------------------------------------------
