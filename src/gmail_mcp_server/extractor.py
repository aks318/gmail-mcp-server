from datetime import date
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama


class LoanNotice(BaseModel):
    loan_id: str
    borrower: str
    servicer: str

    principal_amount: float
    interest_rate: float
    payment_amount: float

    payment_due_date: date
    currency: str = Field(description="ISO currency code, e.g. USD")


llm = ChatOllama(
    model="gpt-oss:20b",
    temperature=0,
)

structured_llm = llm.with_structured_output(LoanNotice)


def extract_loan_details(document_text: str, config: dict) -> dict:

    prompt_template = config["prompts"][
        "loan_servicing_notice_extraction"
    ]

    prompt = prompt_template.format(
        document_text=document_text
    )

    result = structured_llm.invoke(prompt)

    return result.model_dump(mode="json")