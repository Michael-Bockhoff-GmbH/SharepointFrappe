import frappe
from sharepointfrappe.cloud import sharepoint


def connect(connection_name):
    conn = frappe.get_doc("SF Cloud Connection", connection_name)
    return sharepoint.connect(conn)


def upload(connection_name, path, file_name, content, conflict="Rename"):
    """Ensure folder path, then upload the file into it.

    `conflict` is the rule's Conflict Behavior (Rename / Replace / Fail) and
    decides what happens when a file of the same name already exists.
    """
    conflict = (conflict or "Rename").strip().lower()
    if conflict not in ("rename", "replace", "fail"):
        conflict = "rename"

    conn = frappe.get_doc("SF Cloud Connection", connection_name)
    folder_id = sharepoint.ensure_folder(conn, path)
    return sharepoint.upload(conn, folder_id, file_name, content, conflict)