from pprint import pprint

from gmail_mcp_server.document_reader import extract_pdf_text
from gmail_mcp_server.extractor import extract_loan_details


pdf = extract_pdf_text(
    "downloads/dummy_loan_servicing_notice.pdf"
)

loan_details = extract_loan_details(pdf["full_text"])

pprint(loan_details)