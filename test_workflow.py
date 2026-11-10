from pprint import pprint

from gmail_mcp_server.workflow import loan_workflow


result = loan_workflow.invoke({
    "file_path": "downloads/dummy_loan_servicing_notice.pdf"
})

print("\nFinal workflow result:")
pprint(result)

print("\nFinal status:", result["status"])