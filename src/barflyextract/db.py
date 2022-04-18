import googleapiclient.discovery  # type: ignore[import]
import os
from google.auth.transport.requests import Request  # type: ignore[import]
from google.oauth2.credentials import Credentials  # type: ignore[import]
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]

SCOPES = ["https://www.googleapis.com/auth/documents"]
TARGET_DOCUMENT_ID = "1FyWaqxkr7JADUOpzQInIIkr9xOG4rjbXmWqpvgR7bag"


def save_to_db(creds: Credentials, doc_id: str) -> None:
    service = googleapiclient.discovery.build("docs", "v1", credentials=creds)
    # pylint: disable-next=no-member
    document = service.documents().get(documentId=doc_id).execute()
    print("The title of the document is: {}".format(document.get("title")))


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
