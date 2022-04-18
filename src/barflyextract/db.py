"""Replaces an entire, known, shared Google Docs document with updated HTML
(generated elsewhere in this project)."""

import googleapiclient.discovery  # type: ignore[import]
import os
from google.auth.transport.requests import Request  # type: ignore[import]
from google.oauth2.credentials import Credentials  # type: ignore[import]
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]

SCOPES = ["https://www.googleapis.com/auth/documents"]
TARGET_DOCUMENT_ID = "1FyWaqxkr7JADUOpzQInIIkr9xOG4rjbXmWqpvgR7bag"


def update_doc_with_html(creds: Credentials, doc_id: str, content: str) -> None:
    service = googleapiclient.discovery.build("docs", "v1", credentials=creds)
    documents = service.documents()  # pylint: disable=no-member
    doc = documents.get(documentId=doc_id).execute()

    # There doesn't seem to be a replace "all" operation, only find/replace a
    # fixed string. So this function performs a virtually unbound delete,
    # followed by an insert.

    # Work around HTTP 400 "Cannot operate on the first section break in the
    # document."
    not_sections = (
        item for item in doc["body"]["content"] if "sectionBreak" not in item
    )
    start_index = next(item["startIndex"] for item in not_sections)

    # Work around HTTP 400 "The range cannot include the newline character at
    # the end of the segment."
    not_end_newlines = (
        item for item in doc["body"]["content"][::-1] if not _is_newline(item)
    )
    # breakpoint()
    end_index = next(item["endIndex"] for item in not_end_newlines)

    requests = [
        {
            "deleteContentRange": {
                "range": {
                    "startIndex": start_index,
                    "endIndex": end_index,
                }
            }
        },
        {
            "insertText": {
                "location": {
                    "index": start_index,
                },
                "text": content,
            }
        },
    ]

    documents.batchUpdate(documentId=doc_id, body={"requests": requests}).execute()


def _is_newline(google_docs_item: dict) -> bool:
    elements = (google_docs_item.get("paragraph") or {}).get("elements") or []
    if not elements:
        return False

    content = (elements[0].get("textRun") or {}).get("content")
    return content == "\n"


def get_or_prompt_creds() -> Credentials:
    """Per Google's Python quickstart.
    https://developers.google.com/docs/api/quickstart/python"""

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def main() -> None:
    # TODO: update the shared Google Doc with the latest recipe HTML. Only
    #       modify this function.
    pass


if __name__ == "__main__":
    main()
