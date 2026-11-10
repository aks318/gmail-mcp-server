from math import isclose

from gmail_mcp_server.mock_data import LOAN_RECORDS


def validate_loan_details(loan: dict) -> dict:
    errors = []

    loan_id = loan.get("loan_id")

    # 1. Check whether loan exists
    master_record = LOAN_RECORDS.get(loan_id)

    if not master_record:
        errors.append(f"Unknown loan ID: {loan_id}")

        return {
            "is_valid": False,
            "errors": errors,
        }

    # 2. Validate borrower
    if loan["borrower"] != master_record["borrower"]:
        errors.append("Borrower does not match loan master record")

    # 3. Validate currency
    if loan["currency"] != master_record["currency"]:
        errors.append("Currency mismatch")

    # 4. Validate principal amount
    if not isclose(
        loan["principal_amount"],
        master_record["principal_amount"],
        abs_tol=0.01,
    ):
        errors.append("Principal amount mismatch")

    # 5. Validate interest rate
    if not isclose(
        loan["interest_rate"],
        master_record["interest_rate"],
        abs_tol=0.001,
    ):
        errors.append("Interest rate mismatch")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }