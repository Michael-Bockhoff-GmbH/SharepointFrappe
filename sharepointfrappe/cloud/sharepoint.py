import requests
from datetime import timedelta
import frappe
from frappe.utils import now_datetime, get_datetime

GRAPH = "https://graph.microsoft.com/v1.0"


def get_token(conn):
    """Get a login token. Reuse the saved one until it expires."""
    expiry = frappe.db.get_value("SF Cloud Connection", conn.name, "token_expiry")
    if expiry and get_datetime(expiry) > now_datetime():
        cached = conn.get_password("cached_token")
        if cached:
            return cached

    url = f"https://login.microsoftonline.com/{conn.tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": conn.client_id,
        "client_secret": conn.get_password("client_secret"),
        "scope": "https://graph.microsoft.com/.default",
    }
    res = requests.post(url, data=data, timeout=30)
    res.raise_for_status()
    token_info = res.json()
    token = token_info["access_token"]

    expires_in = token_info.get("expires_in", 3600) - 300
    conn.db_set("cached_token", token)
    conn.db_set("token_expiry", now_datetime() + timedelta(seconds=expires_in))
    return token


def _normalize_site_path(site_path):
    """Turn a user-entered site path into the form Graph expects.

    Accepts just the site name ("FrappeTest"), the full path ("sites/FrappeTest")
    or one with a leading slash ("/sites/FrappeTest"). Prepends "sites/" unless a
    "sites/" or "teams/" prefix is already present, so the user doesn't have to.
    """
    path = (site_path or "").strip().strip("/")
    if not path:
        return ""
    if not path.startswith(("sites/", "teams/")):
        path = f"sites/{path}"
    return path


def get_site_id(conn, token):
    """Find the SharePoint site id."""
    site_path = _normalize_site_path(conn.site_path)
    url = f"{GRAPH}/sites/{conn.site_name}.sharepoint.com:/{site_path}"
    res = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    res.raise_for_status()
    return res.json()["id"]


def get_drive_id(conn, token, site_id):
    """Find the drive (document library) id by its name."""
    url = f"{GRAPH}/sites/{site_id}/drives"
    res = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    res.raise_for_status()
    for drive in res.json()["value"]:
        if drive["name"] == conn.drive_name:
            return drive["id"]
    frappe.throw(f"Drive '{conn.drive_name}' not found.")


def connect(conn):
    """Verify login + site + drive, and save the ids for reuse."""
    try:
        conn.db_set("cached_token", "")
        conn.db_set("token_expiry", None)
        token = get_token(conn)
        site_id = get_site_id(conn, token)
        drive_id = get_drive_id(conn, token, site_id)
        conn.db_set("site_id", site_id)
        conn.db_set("drive_id", drive_id)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _get_child_id(base, headers, parent, name):
    """Find an existing child folder's id by name."""
    url = f"{base}/items/{parent}/children?$filter=name eq '{name}'"
    res = requests.get(url, headers=headers, timeout=30)
    res.raise_for_status()
    items = res.json()["value"]
    return items[0]["id"] if items else None


def ensure_folder(conn, path):
    """Create the folder path if missing. Return the leaf folder id."""
    token = get_token(conn)
    headers = {"Authorization": f"Bearer {token}"}
    base = f"{GRAPH}/sites/{conn.site_id}/drives/{conn.drive_id}"

    parent = "root"
    folder_id = None
    for name in [p for p in path.strip("/").split("/") if p]:
        url = f"{base}/items/{parent}/children"
        data = {"name": name, "folder": {}, "@microsoft.graph.conflictBehavior": "fail"}
        res = requests.post(url, headers=headers, json=data, timeout=30)

        if res.status_code == 201:
            folder_id = res.json()["id"]
        elif res.status_code == 409:
            folder_id = _get_child_id(base, headers, parent, name)
        else:
            res.raise_for_status()
        parent = folder_id
    return parent


def upload(conn, folder_id, file_name, content, conflict="rename"):
    """Upload bytes into folder_id. Return {'id', 'web_url'}.

    `conflict` maps straight to Graph's conflictBehavior: rename / replace / fail.
    """
    token = get_token(conn)
    headers = {"Authorization": f"Bearer {token}"}
    base = f"{GRAPH}/sites/{conn.site_id}/drives/{conn.drive_id}"
    url = f"{base}/items/{folder_id}:/{file_name}:/content?@microsoft.graph.conflictBehavior={conflict}"
    res = requests.put(url, headers=headers, data=content, timeout=60)
    if res.status_code == 409:
        frappe.throw(f"A file named '{file_name}' already exists in the target folder.")
    res.raise_for_status()
    data = res.json()
    return {"id": data["id"], "web_url": data.get("webUrl")}