import os
import re

import frappe
from frappe.model import default_fields


def _field_value(doctype, docname, fieldname):
    """Read a field off the attached record, guarding against a bad fieldname.

    Raises a clear error instead of letting an unknown-column database error
    surface as a generic 500 during upload.
    """
    if not (doctype and docname and fieldname):
        return None
    meta = frappe.get_meta(doctype)
    if not meta.get_field(fieldname) and fieldname not in default_fields:
        frappe.throw(
            f"Folder/naming segment references field '{fieldname}', which does not "
            f"exist on DocType '{doctype}'. Fix the SF Upload Rule.",
            title="Invalid SF Upload Rule",
        )
    return frappe.db.get_value(doctype, docname, fieldname)


def build_filename(rule, file_doc):
    """Resolve the rule's naming strategy into the final stored file name.

    Templated naming supports these placeholders:
      {name}     -> the attached record's id
      {doctype}  -> the attached record's doctype
      {field}    -> the attach fieldname (e.g. upload_1)
      {<field>}  -> the value of that fieldname on the attached record
    The original file extension is preserved if the template doesn't add one.
    """
    original = file_doc.file_name or ""

    strategy = getattr(rule, "naming_strategy", None) or "Original"
    template = (getattr(rule, "naming_template", None) or "").strip()
    if strategy != "Templated" or not template:
        return original

    doctype = file_doc.attached_to_doctype
    docname = file_doc.attached_to_name
    field = file_doc.attached_to_field

    def resolve(match):
        key = match.group(1).strip()
        if key == "name":
            value = docname
        elif key == "doctype":
            value = doctype
        elif key == "field":
            value = field
        else:
            value = _field_value(doctype, docname, key)
        return _clean(value)

    base = re.sub(r"\{([^{}]+)\}", resolve, template).strip()
    base = _clean(base) or _clean(os.path.splitext(original)[0]) or "file"

    ext = os.path.splitext(original)[1]
    if ext and not base.lower().endswith(ext.lower()):
        base = f"{base}{ext}"
    return base


def build_path(rule, file_doc):
    """Resolve the rule into a cloud folder path, per its folder structure mode."""
    if getattr(rule, "folder_structure", None) == "Group by Link Field":
        return _grouped_path(rule, file_doc)
    return _segments_path(rule, file_doc)


def _segments_path(rule, file_doc):
    """Resolve the folder segments table into a path like 'Sales Invoice/SINV-001'."""
    doctype = file_doc.attached_to_doctype
    docname = file_doc.attached_to_name

    parts = []
    for seg in rule.folder_segments:
        if seg.segment_type == "Static Text":
            value = seg.value
        elif seg.segment_type == "Doctype Name":
            value = doctype
        elif seg.segment_type == "Record Name":
            value = docname
        elif seg.segment_type == "Field Value":
            # field_name is the current field; fall back to value for older rows
            fieldname = getattr(seg, "field_name", None) or seg.value
            value = _field_value(doctype, docname, fieldname)
        else:
            value = None

        value = _clean(value)
        if not value:
            value = "Unfiled"   # fallback so a blank field never loses the file
        parts.append(value)

    return "/".join(parts)


def _grouped_path(rule, file_doc):
    """Build '<party> / <doctype>' where the party comes from a link field.

    The link field (e.g. 'customer' on Sales Invoice) is configured on the rule.
    The party folder is the linked record's id, with its readable title appended
    as 'id - title' when the two differ (e.g. a naming-series 'CUST-0001 - Acme').
    """
    doctype = file_doc.attached_to_doctype
    docname = file_doc.attached_to_name

    fieldname = getattr(rule, "group_by_field", None)
    link_id = _field_value(doctype, docname, fieldname) if fieldname else None

    linked_doctype = None
    if fieldname:
        df = frappe.get_meta(doctype).get_field(fieldname)
        linked_doctype = df.options if df else None

    party = _party_folder(linked_doctype, link_id)
    subfolder = _clean(doctype) or "Unfiled"
    return f"{party}/{subfolder}"


def _party_folder(linked_doctype, link_id):
    """Folder name for a linked record: 'id - title' when they differ, else 'id'."""
    id_clean = _clean(link_id)
    if not id_clean:
        return "Unfiled"

    readable = None
    if linked_doctype:
        title_field = frappe.get_meta(linked_doctype).get_title_field()
        if title_field and title_field != "name":
            readable = frappe.db.get_value(linked_doctype, link_id, title_field)

    readable_clean = _clean(readable)
    if readable_clean and readable_clean != id_clean:
        return f"{id_clean} - {readable_clean}"
    return id_clean


def _clean(value):
    """Remove characters illegal in folder names."""
    if value is None:
        return ""
    return re.sub(r'[\\/:*?"<>|]', "_", str(value)).strip()