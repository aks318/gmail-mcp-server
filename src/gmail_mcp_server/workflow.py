from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

from gmail_mcp_server.graph_state import LoanProcessingState
from gmail_mcp_server.document_reader import extract_pdf_text
from gmail_mcp_server.document_config import load_document_config
from gmail_mcp_server.classifier import classify_document
from gmail_mcp_server.extractor import extract_loan_details
from gmail_mcp_server.validator import validate_loan_details

import httpx

# Node 1: Read PDF
def read_document(state: LoanProcessingState):
    pdf = extract_pdf_text(state["file_path"])

    return {
        "filename": pdf["filename"],
        "full_text": pdf["full_text"],
    }


# Node 2: Classify document
def classify(state: LoanProcessingState):
    config = load_document_config()

    result = classify_document(
        state["full_text"],
        config,
    )

    return {"classification": result}


# Node 3: Extract loan details
def extract_loan_data(state: LoanProcessingState):
    config = load_document_config()

    result = extract_loan_details(
        state["full_text"],
        config,
    )

    return {"extracted_data": result}


# Node 4: Validate loan details
def validate(state: LoanProcessingState):
    result = validate_loan_details(
        state["extracted_data"]
    )

    return {"validation": result}


# Node 5: Handle unsupported documents
def unsupported_document(state: LoanProcessingState):
    return {"status": "unsupported_document"}


# Node 6: Ready for human approval
def request_human_approval(state: LoanProcessingState):
    decision = interrupt({
        "message": "Review the loan details before approval.",
        "loan_details": state["extracted_data"],
        "validation": state["validation"],
        "available_actions": ["approve", "reject"] 
    })

    if decision == "approve":
        return {
            "status": "approved",
            "approval_decision": "approve",
        }
    return {
            "status": "rejected",
            "approval_decision": "reject",
        }


# Node 7: Handle validation failures
def handle_exception(state: LoanProcessingState):
    return {"status": "exception"}

# Conditional routing after classification
def route_after_classification(state: LoanProcessingState):
    if (
        state["classification"]["document_type"]
        == "loan_servicing_notice"
    ):
        return "extract"

    return "unsupported"


# Conditional routing after validation
def route_after_validation(state: LoanProcessingState):
    if state["validation"]["is_valid"]:
        return "approval"

    return "exception"

def post_to_pam(state: LoanProcessingState):

    if state.get("approval_decision") != "approve":
        raise ValueError("Cannot post without human approval")

    payload = {
        **state["extracted_data"],
        "approval_decision": "approve",
    }

    try:
        response = httpx.post(
            "http://localhost:8001/transactions",
            json=payload,
            timeout=15,
        )

        response.raise_for_status()

        return {
            "posting_result": response.json(),
            "status": "posted",
        }

    except httpx.HTTPError as exc:
        return {
            "posting_result": {
                "error": str(exc),
            },
            "status": "posting_failed",
        }

def handle_posting_error(state: LoanProcessingState):
    return {
        "status": "posting_failed",
    }

def route_after_approval(state: LoanProcessingState):
    if state["approval_decision"] == "approve":
        return "post"

    return "end"


def route_after_posting(state: LoanProcessingState):
    if state["status"] == "posted":
        return "success"

    return "failure"




builder = StateGraph(LoanProcessingState)

builder.add_node("read_document", read_document)
builder.add_node("classify", classify)
builder.add_node("extract_loan_data", extract_loan_data)
builder.add_node("validate", validate)

builder.add_node("unsupported_document", unsupported_document)
builder.add_node("handle_exception", handle_exception)
builder.add_node("request_human_approval", request_human_approval)

builder.add_node("post_to_pam", post_to_pam)
builder.add_node("handle_posting_error", handle_posting_error)

builder.add_edge(START, "read_document")
builder.add_edge("read_document", "classify")

builder.add_conditional_edges(
    "classify", 
    route_after_classification,
    {
        "extract" : "extract_loan_data",
        "unsupported" : "unsupported_document"
    }
)

builder.add_edge("extract_loan_data", "validate")

builder.add_conditional_edges(
    "validate", 
    route_after_validation,
    {
        "approval" : "request_human_approval",
        "exception" : "handle_exception"
    }
)
builder.add_conditional_edges(
    "request_human_approval",
    route_after_approval,
    {
        "post": "post_to_pam",
        "end": END,
    },
)

builder.add_conditional_edges(
    "post_to_pam",
    route_after_posting,
    {
        "success": END,
        "failure": "handle_posting_error",
    },
)

builder.add_edge("handle_posting_error", END)
builder.add_edge("unsupported_document", END)
builder.add_edge("handle_exception", END)


checkpointer = InMemorySaver()
# Compile graph
loan_workflow = builder.compile(
    checkpointer=checkpointer
)