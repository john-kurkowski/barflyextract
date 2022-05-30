"""Replaces an entire, known, shared Google Docs document with updated HTML
(generated elsewhere in this project)."""

import googleapiclient.discovery  # type: ignore[import]
import os
from google.auth.transport.requests import Request  # type: ignore[import]
from google.oauth2.credentials import Credentials  # type: ignore[import]
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]
from googleapiclient.http import MediaFileUpload  # type: ignore[import]

SCOPES = ["https://www.googleapis.com/auth/drive"]
TARGET_DOCUMENT_ID = "1FyWaqxkr7JADUOpzQInIIkr9xOG4rjbXmWqpvgR7bag"


def update_doc(creds: Credentials, doc_id: str, media: MediaFileUpload) -> None:
    service = googleapiclient.discovery.build("drive", "v3", credentials=creds)
    files = service.files()  # pylint: disable=no-member
    files.update(fileId=doc_id, media_body=media).execute()


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
