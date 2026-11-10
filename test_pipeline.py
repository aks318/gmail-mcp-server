from pprint import pprint

from gmail_mcp_server.pipeline import process_document


result = process_document(
    "downloads/dummy_loan_servicing_notice.pdf"
)

pprint(result)