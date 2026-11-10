
from gmail_mcp_server.gmail_client import (
    list_unread_emails,
    get_email,
    list_attachments,
    download_attachment,
)


emails = list_unread_emails(max_results=5)

for email in emails:

    print("\nSubject:", email["subject"])

    full_email = get_email(email["id"])

    print("\nEmail body:")
    print(full_email["body"][:1000])

    attachments = list_attachments(email["id"])

    for attachment in attachments:

        print("\nAttachment:", attachment)

        if attachment["attachment_id"]:
            path = download_attachment(
                email["id"],
                attachment["attachment_id"],
                attachment["filename"],
            )

            print("Downloaded:", path)
