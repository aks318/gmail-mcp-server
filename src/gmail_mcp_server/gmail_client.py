
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import base64
from pathlib import Path


# Read-only Gmail access
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

CREDENTIALS_FILE = BASE_DIR / "credentials" / "credentials.json"
TOKEN_FILE = BASE_DIR / "credentials" / "token.json"


def get_gmail_service():
    """Authenticate with Google and return a Gmail API service."""

    creds = None

    # Reuse previously generated OAuth token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES,
        )

    # Refresh expired credentials or start OAuth flow
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"OAuth credentials not found: {CREDENTIALS_FILE}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES,
            )

            creds = flow.run_local_server(port=0)

        # Save token for future authentication
        TOKEN_FILE.write_text(creds.to_json())

    service = build(
        "gmail",
        "v1",
        credentials=creds,
        cache_discovery=False,
    )

    return service


def list_unread_emails(max_results: int = 10):
    """Fetch unread emails from Gmail."""

    service = get_gmail_service()

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            q="is:unread",
            maxResults=max_results,
        )
        .execute()
    )

    messages = response.get("messages", [])

    emails = []

    for message in messages:

        email = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )

        headers = email.get("payload", {}).get("headers", [])

        header_data = {
            header["name"].lower(): header["value"]
            for header in headers
        }

        emails.append({
            "id": email["id"],
            "thread_id": email["threadId"],
            "sender": header_data.get("from"),
            "subject": header_data.get("subject"),
            "date": header_data.get("date"),
            "snippet": email.get("snippet"),
        })

    return emails



def get_email(message_id: str):
    """Fetch complete email content."""

    service = get_gmail_service()

    email = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="full",
        )
        .execute()
    )

    payload = email.get("payload", {})
    headers = payload.get("headers", [])

    header_data = {
        header["name"].lower(): header["value"]
        for header in headers
    }

    def extract_body(part):
        """Recursively extract readable email body."""

        import base64

        mime_type = part.get("mimeType", "")
        body_data = part.get("body", {}).get("data")

        if mime_type == "text/plain" and body_data:
            decoded = base64.urlsafe_b64decode(
                body_data + "=="
            )
            return decoded.decode("utf-8", errors="replace")

        for child in part.get("parts", []):
            result = extract_body(child)
            if result:
                return result

        return ""

    body = extract_body(payload)

    return {
        "id": email["id"],
        "thread_id": email["threadId"],
        "sender": header_data.get("from"),
        "subject": header_data.get("subject"),
        "date": header_data.get("date"),
        "body": body,
        "payload": payload,
    }


def list_attachments(message_id: str):
    """List attachments in an email."""

    email = get_email(message_id)

    attachments = []

    def find_attachments(part):

        filename = part.get("filename")

        if filename:
            attachments.append({
                "filename": filename,
                "mime_type": part.get("mimeType"),
                "attachment_id": (
                    part.get("body", {}).get("attachmentId")
                ),
            })

        for child in part.get("parts", []):
            find_attachments(child)

    find_attachments(email["payload"])

    return attachments


def download_attachment(
    message_id: str,
    attachment_id: str,
    filename: str,
):
    """Download an email attachment."""

    service = get_gmail_service()

    attachment = (
        service.users()
        .messages()
        .attachments()
        .get(
            userId="me",
            messageId=message_id,
            id=attachment_id,
        )
        .execute()
    )

    file_data = base64.urlsafe_b64decode(
        attachment["data"]
    )

    download_dir = BASE_DIR / "downloads"
    download_dir.mkdir(exist_ok=True)

    # Avoid writing outside the downloads directory
    safe_filename = Path(filename).name
    file_path = download_dir / safe_filename

    file_path.write_bytes(file_data)

    return str(file_path)
