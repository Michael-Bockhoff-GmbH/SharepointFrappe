import frappe
from frapnexus.cloud import sharepoint, google_drive


def _provider(conn):
    if conn.provider == "SharePoint":
        return sharepoint
    if conn.provider == "Google Drive":
        return google_drive
    frappe.throw(f"Provider '{conn.provider}' not ready yet.")


def connect(connection_name):
    conn = frappe.get_doc("FN Cloud Connection", connection_name)
    return _provider(conn).connect(conn)


def upload(connection_name, path, file_name, content, conflict="Rename"):
    """Ensure folder path, then upload the file into it.

    `conflict` is the rule's Conflict Behavior (Rename / Replace / Fail) and
    decides what happens when a file of the same name already exists.
    """
    conflict = (conflict or "Rename").strip().lower()
    if conflict not in ("rename", "replace", "fail"):
        conflict = "rename"

    conn = frappe.get_doc("FN Cloud Connection", connection_name)
    provider = _provider(conn)
    folder_id = provider.ensure_folder(conn, path)
    return provider.upload(conn, folder_id, file_name, content, conflict)