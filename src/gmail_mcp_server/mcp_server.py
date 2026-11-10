
from typing import Literal
from uuid import uuid4

from fastmcp import FastMCP
from langgraph.types import Command

from gmail_mcp_server.workflow import loan_workflow

mcp = FastMCP("Loan Operations Server")


@mcp.tool()
def process_loan_document(file_path: str) -> dict:
    """Process a loan servicing notice PDF."""

    thread_id = str(uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = loan_workflow.invoke(
        {"file_path": file_path},
        config=config,
    )

    if result.get("__interrupt__"):
        approval_request = result["__interrupt__"][0].value

        return {
            "status": "approval_required",
            "thread_id": thread_id,
            "approval_request": approval_request,
        }

    return {
        "status": result.get("status"),
        "thread_id": thread_id,
        "classification": result.get("classification"),
        "extracted_data": result.get("extracted_data"),
        "validation": result.get("validation"),
        "posting_result": result.get("posting_result"),
    }


@mcp.tool()
def approve_loan_transaction(
    thread_id: str,
    decision: Literal["approve", "reject"],
) -> dict:
    """
    Approve or reject a loan transaction.

    Resumes the paused LangGraph workflow using its thread ID.
    """

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = loan_workflow.invoke(
        Command(resume=decision),
        config=config,
    )

    return {
        "status": result.get("status"),
        "approval_decision": result.get("approval_decision"),
        "posting_result": result.get("posting_result"),
    }


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
