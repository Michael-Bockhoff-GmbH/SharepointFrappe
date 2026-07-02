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
    """Resolve the rule's folder segments into a path like 'Sales Invoice/SINV-001'."""
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


def _clean(value):
    """Remove characters illegal in folder names."""
    if value is None:
        return ""
    return re.sub(r'[\\/:*?"<>|]', "_", str(value)).strip()