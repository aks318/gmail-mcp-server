
from gmail_mcp_server.document_reader import extract_pdf_text

pdf_path = "downloads/dummy_loan_servicing_notice.pdf"

result = extract_pdf_text(pdf_path)

print("Filename:", result["filename"])
print("Total pages:", result["total_pages"])

print("\nExtracted content:")
print(result["full_text"])
