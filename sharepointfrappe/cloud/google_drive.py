import io
import json
import frappe
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_service(conn):
    """Build an authenticated Google Drive client from the service-account JSON."""
    info = json.loads(conn.get_password("service_account_json"))
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def connect(conn):
    """Verify the service account can reach the root folder."""
    try:
        service = get_service(conn)
        service.files().get(
            fileId=conn.root_folder_id, fields="id, name", supportsAllDrives=True,
        ).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def ensure_folder(conn, path):
    """Create the folder path if missing. Return the leaf folder id."""
    service = get_service(conn)
    parent = conn.root_folder_id

    for name in [p for p in path.strip("/").split("/") if p]:
        query = (
            f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' "
            f"and '{parent}' in parents and trashed = false"
        )
        res = service.files().list(
            q=query, fields="files(id)", supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        files = res.get("files", [])

        if files:
            parent = files[0]["id"]
        else:
            meta = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent]}
            created = service.files().create(body=meta, fields="id", supportsAllDrives=True).execute()
            parent = created["id"]
    return parent


def _find_file(service, folder_id, name):
    """Return the id of a non-trashed file with this exact name in the folder, or None."""
    safe = name.replace("\\", "\\\\").replace("'", "\\'")
    query = (
        f"name = '{safe}' and '{folder_id}' in parents and trashed = false "
        f"and mimeType != 'application/vnd.google-apps.folder'"
    )
    res = service.files().list(
        q=query, fields="files(id)", supportsAllDrives=True, includeItemsFromAllDrives=True,
    ).execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None


def _unique_name(service, folder_id, name):
    """Append ' (n)' before the extension until the name is free in the folder."""
    import os

    stem, ext = os.path.splitext(name)
    candidate, i = name, 1
    while _find_file(service, folder_id, candidate):
        candidate = f"{stem} ({i}){ext}"
        i += 1
    return candidate


def upload(conn, folder_id, file_name, content, conflict="rename"):
    """Upload bytes into folder_id. Return {'id', 'web_url'}.

    Drive has no native conflict handling, so honour the rule manually:
      fail    -> raise if a file of the same name already exists
      replace -> overwrite the existing file's contents
      rename  -> upload under the next free ' (n)' name
    """
    service = get_service(conn)
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/octet-stream", resumable=True)

    existing = _find_file(service, folder_id, file_name)
    if existing:
        if conflict == "fail":
            frappe.throw(f"A file named '{file_name}' already exists in the target folder.")
        if conflict == "replace":
            updated = service.files().update(
                fileId=existing, media_body=media, fields="id, webViewLink", supportsAllDrives=True,
            ).execute()
            return {"id": updated["id"], "web_url": updated.get("webViewLink")}
        # rename
        file_name = _unique_name(service, folder_id, file_name)

    meta = {"name": file_name, "parents": [folder_id]}
    created = service.files().create(
        body=meta, media_body=media, fields="id, webViewLink", supportsAllDrives=True,
    ).execute()
    return {"id": created["id"], "web_url": created.get("webViewLink")}