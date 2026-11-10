
import asyncio
from fastmcp import Client


async def main():

    async with Client("http://127.0.0.1:8000/mcp") as client:

        # 1. Discover tools
        tools = await client.list_tools()

        print("\nAvailable MCP tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

        # 2. Process document
        result = await client.call_tool(
            "process_loan_document",
            {
                "file_path": "downloads/dummy_loan_servicing_notice.pdf"
            },
        )

        processing_data = result.structured_content

        print("\nProcessing result:")
        print(processing_data)

        # 3. Human approval
        if processing_data["status"] == "approval_required":

            thread_id = processing_data["thread_id"]

            print("\nLoan details:")
            print(processing_data["approval_request"]["loan_details"])

            decision = input(
                "\nEnter decision (approve/reject): "
            ).strip().lower()

            if decision not in ["approve", "reject"]:
                raise ValueError("Invalid decision")

            # 4. Resume workflow using the SAME client connection
            approval_result = await client.call_tool(
                "approve_loan_transaction",
                {
                    "thread_id": thread_id,
                    "decision": decision,
                },
            )

            print("\nFinal result:")
            print(approval_result.structured_content)


if __name__ == "__main__":
    asyncio.run(main())
