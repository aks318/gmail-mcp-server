import json

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

class DocumentClassification(BaseModel):
    document_type: str = Field(
        description="Type of document"
    )
    confidence: float = Field(
        description="Confidence score between 0 and 1"
    )
    reason: str = Field(
        description="Why this document was classified this way"
    ) 

llm = ChatOllama(
    model="gpt-oss:20b",
    temperature=0,
)

structured_llm = llm.with_structured_output(DocumentClassification)

import json

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field


class DocumentClassification(BaseModel):
    document_type: str = Field(
        description="Type of document"
    )
    confidence: float = Field(
        description="Confidence score between 0 and 1"
    )
    reason: str = Field(
        description="Why this document was classified this way"
    )


llm = ChatOllama(
    model="gpt-oss:20b",
    temperature=0,
)

structured_llm = llm.with_structured_output(
    DocumentClassification
)


def classify_document(document_text: str, config: dict) -> dict:
    document_types = config["document_types"]

    prompt_template = config["prompts"]["classification"]

    prompt = prompt_template.format(
        document_types=", ".join(document_types),
        document_text=document_text,
    )

    result = structured_llm.invoke(prompt)

    return result.model_dump()