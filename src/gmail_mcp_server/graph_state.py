from typing import TypedDict


class LoanProcessingState(TypedDict, total=False):
    file_path: str
    filename: str
    full_text: str

    classification: dict
    extracted_data: dict
    validation: dict

    status: str
    approval_decision: str
    posting_result: dict