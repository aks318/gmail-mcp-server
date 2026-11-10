from gmail_mcp_server.document_reader import extract_pdf_text
from gmail_mcp_server.document_config import load_document_config
from gmail_mcp_server.classifier import classify_document
from gmail_mcp_server.extractor import extract_loan_details
from gmail_mcp_server.validator import validate_loan_details


def process_document(file_path: str) -> dict:

    config = load_document_config()

    pdf = extract_pdf_text(file_path)

    classification = classify_document(
        pdf["full_text"],
        config,
    )

    document_type = classification["document_type"]

    if document_type != "loan_servicing_notice":
        return {
            "status": "unsupported_document",
            "filename": pdf["filename"],
            "classification": classification,
            "extracted_data": None,
            "validation": None,
        }

    loan_details = extract_loan_details(
        pdf["full_text"],
        config,
    )

    validation = validate_loan_details(loan_details)

    return {
        "status": (
            "ready_for_approval"
            if validation["is_valid"]
            else "exception"
        ),
        "filename": pdf["filename"],
        "classification": classification,
        "extracted_data": loan_details,
        "validation": validation,
    }