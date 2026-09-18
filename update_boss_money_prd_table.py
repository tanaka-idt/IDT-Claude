"""
Updates the existing BOSS Money Recipient App PRD Google Doc:
- Deletes the existing 5-column prioritization table
- Inserts a new 7-column table at the same position
- New columns: # (far left) and Type (after Feature)

Doc ID is hardcoded from the create_boss_money_prd.py run.
"""

import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]
BASE = Path(__file__).parent
CREDS_FILE = BASE / "credentials.json"
TOKEN_FILE = BASE / "token.json"

DOC_ID = "1ioXtnx0SxxXgTODFTcB5ize24BcedxjJ1IEzZIiKi2k"


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


# ── New 7-column table data ───────────────────────────────────────────────────
# Columns: #, Feature, Type, App, UX Impact, Revenue Impact, Priority
TABLE_DATA = [
    ["#", "Feature", "Type", "App", "UX Impact", "Revenue Impact", "Priority"],
    # Recipient — P0
    ["1",  "Start the purchase flow",                              "Purchase flow", "Recipient", "High",   "High",   "P0"],
    ["2",  "Subscription request",                                  "Purchase flow", "Recipient", "High",   "High",   "P0"],
    ["3",  "Subscription editing request",                          "Purchase flow", "Recipient", "Medium", "High",   "P0"],
    ["4",  "Emergency / one-tap request",                           "Purchase flow", "Recipient", "High",   "Medium", "P0"],
    ["5",  "Notifications when top-up arrives",                     "Informative",   "Recipient", "High",   "Medium", "P0"],
    ["6",  "Failed transactions notification",                      "Informative",   "Recipient", "High",   "Medium", "P0"],
    ["7",  "See available carrier promos",                          "Promos",        "Recipient", "Medium", "High",   "P0"],
    ["8",  "Loyalty promos visualization",                          "Promos",        "Recipient", "Medium", "High",   "P0"],
    ["9",  "History of received top-ups (filter by sender)",        "Informative",   "Recipient", "Medium", "Low",    "P0"],
    # Sender — P0
    ["10", "Trigger IMTU based on recipient request",               "Purchase flow", "Sender",    "High",   "High",   "P0"],
    ["11", "Set top-ups subscription requested by recipient",       "Purchase flow", "Sender",    "High",   "High",   "P0"],
    # Recipient — P1
    ["12", "Low-balance & validity expiration alerts",              "Informative",   "Recipient", "High",   "High",   "P1"],
    ["13", "Thank you messaging to sender",                         "Informative",   "Recipient", "Medium", "Low",    "P1"],
    ["14", "Multi-sender management",                               "Management",    "Recipient", "Medium", "Medium", "P1"],
    # Sender — P1
    ["15", "Get low-balance alerts (carrier API)",                  "Informative",   "Sender",    "High",   "High",   "P1"],
    ["16", "Confirm delivery (carrier API)",                        "Informative",   "Sender",    "High",   "Medium", "P1"],
    ["17", "Thank you messaging from recipient",                    "Informative",   "Sender",    "Medium", "Low",    "P1"],
    ["18", "View transaction request history",                      "Informative",   "Sender",    "Medium", "Low",    "P1"],
    ["19", "Blocking numbers",                                      "Management",    "Sender",    "Low",    "Low",    "P1"],
]

NUM_ROWS = len(TABLE_DATA)
NUM_COLS = 7


def find_table(doc_data):
    """Return (table_elem, start_idx, end_idx) for the first table in the doc."""
    for element in doc_data["body"]["content"]:
        if "table" in element:
            return element["table"], element["startIndex"], element["endIndex"]
    return None, None, None


def main():
    creds = get_credentials()
    docs_svc = build("docs", "v1", credentials=creds)

    # ── Phase 1: locate existing table ───────────────────────────────────────
    print("Locating existing table...")
    doc_data = docs_svc.documents().get(documentId=DOC_ID).execute()
    table_elem, table_start, table_end = find_table(doc_data)
    if table_start is None:
        print("⚠️  No table found in doc — aborting.")
        return
    print(f"  Existing table at [{table_start}, {table_end}]")

    # ── Phase 2: delete the existing table ──────────────────────────────────
    print("Deleting existing table...")
    docs_svc.documents().batchUpdate(
        documentId=DOC_ID,
        body={"requests": [
            {"deleteContentRange": {
                "range": {"startIndex": table_start, "endIndex": table_end}
            }}
        ]}
    ).execute()

    # ── Phase 3: insert new 7-column table at same position ──────────────────
    print(f"Inserting new {NUM_ROWS}x{NUM_COLS} table at index {table_start}...")
    docs_svc.documents().batchUpdate(
        documentId=DOC_ID,
        body={"requests": [
            {"insertTable": {
                "location": {"index": table_start},
                "rows": NUM_ROWS,
                "columns": NUM_COLS,
            }}
        ]}
    ).execute()

    # ── Phase 4: locate new table cells & populate ───────────────────────────
    print("Locating new table cells...")
    doc_data = docs_svc.documents().get(documentId=DOC_ID).execute()
    table_elem, table_start_idx, _ = find_table(doc_data)

    cells_to_fill = []
    for row_idx, row in enumerate(table_elem["tableRows"]):
        for col_idx, cell in enumerate(row["tableCells"]):
            cell_text_idx = cell["content"][0]["startIndex"]
            text = TABLE_DATA[row_idx][col_idx]
            cells_to_fill.append((cell_text_idx, text))

    # Sort descending so earlier indices don't shift as we insert
    cells_to_fill.sort(key=lambda x: x[0], reverse=True)

    print(f"Filling {len(cells_to_fill)} cells...")
    fill_requests = [
        {"insertText": {"location": {"index": idx}, "text": text}}
        for idx, text in cells_to_fill
    ]
    for i in range(0, len(fill_requests), 50):
        chunk = fill_requests[i:i + 50]
        docs_svc.documents().batchUpdate(
            documentId=DOC_ID,
            body={"requests": chunk},
        ).execute()
        time.sleep(0.3)

    # ── Phase 5: format header row (bold + grey shading) ─────────────────────
    print("Formatting header row...")
    doc_data = docs_svc.documents().get(documentId=DOC_ID).execute()
    table_elem, table_start_idx, _ = find_table(doc_data)

    format_requests = []
    header_row = table_elem["tableRows"][0]
    for cell in header_row["tableCells"]:
        cell_para = cell["content"][0].get("paragraph", {})
        for elem in cell_para.get("elements", []):
            if "textRun" in elem:
                start = elem["startIndex"]
                end = elem["endIndex"]
                format_requests.append({
                    "updateTextStyle": {
                        "range": {"startIndex": start, "endIndex": end},
                        "textStyle": {"bold": True},
                        "fields": "bold",
                    }
                })

    # Shade header row background
    format_requests.append({
        "updateTableCellStyle": {
            "tableCellStyle": {
                "backgroundColor": {
                    "color": {"rgbColor": {"red": 0.93, "green": 0.93, "blue": 0.93}}
                }
            },
            "fields": "backgroundColor",
            "tableRange": {
                "tableCellLocation": {
                    "tableStartLocation": {"index": table_start_idx},
                    "rowIndex": 0,
                    "columnIndex": 0,
                },
                "rowSpan": 1,
                "columnSpan": NUM_COLS,
            }
        }
    })

    if format_requests:
        docs_svc.documents().batchUpdate(
            documentId=DOC_ID,
            body={"requests": format_requests},
        ).execute()

    print(f"\n✅  Done!")
    print(f"   Google Doc: https://docs.google.com/document/d/{DOC_ID}/edit\n")


if __name__ == "__main__":
    main()
