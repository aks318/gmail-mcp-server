from pprint import pprint

from gmail_mcp_server.classifier import classify_document
from gmail_mcp_server.document_reader import extract_pdf_text


pdf = extract_pdf_text(
    "downloads/dummy_loan_servicing_notice.pdf"
)

loan_details = classify_document(pdf["full_text"])

pprint(loan_details)