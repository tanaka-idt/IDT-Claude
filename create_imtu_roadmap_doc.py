"""
Creates a Google Doc from IMTU_FY_Roadmap.md by importing the Markdown
via the Drive API (Docs supports Markdown import -> preserves headings,
bold, and tables). Reuses the existing OAuth token (token.json).
"""

from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"
MD_FILE = BASE / "IMTU_FY_Roadmap.md"
DOC_TITLE = "Boss Revolution — IMTU Product Roadmap (Next FY)"


def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_FILE.exists():
                raise FileNotFoundError("credentials.json missing")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def main():
    creds = get_credentials()
    drive = build("drive", "v3", credentials=creds)

    media = MediaFileUpload(str(MD_FILE), mimetype="text/markdown", resumable=False)
    file_metadata = {
        "name": DOC_TITLE,
        "mimeType": "application/vnd.google-apps.document",
    }
    created = drive.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,webViewLink",
        supportsAllDrives=True,
    ).execute()

    doc_id = created["id"]
    link = created.get("webViewLink", f"https://docs.google.com/document/d/{doc_id}/edit")
    print("DOC_ID:", doc_id)
    print("DOC_URL:", link)


if __name__ == "__main__":
    main()
