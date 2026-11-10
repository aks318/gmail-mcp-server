from pprint import pprint

from langgraph.types import Command

from gmail_mcp_server.workflow import loan_workflow


config = {
    "configurable": {
        "thread_id": "loan-LN-10025"
    }
}

# Start workflow
result = loan_workflow.invoke(
    {
        "file_path": "downloads/dummy_loan_servicing_notice.pdf"
    },
    config=config,
)

# Workflow pauses for human approval
if result.get("__interrupt__"):
    approval_request = result["__interrupt__"][0].value

    print("\nApproval required!")
    pprint(approval_request)

    decision = input(
        "\nEnter decision (approve/reject): "
    ).strip().lower()

    if decision not in ["approve", "reject"]:
        raise ValueError("Invalid approval decision")

    # Resume workflow
    result = loan_workflow.invoke(
        Command(resume=decision),
        config=config,
    )

print("\nFinal workflow status:")
print(result["status"])