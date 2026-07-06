import os
import re

import frappe
from frappe import _
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
    if getattr(rule, "folder_structure", None) == "Group by Customer":
        return _customer_path(rule, file_doc)
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
            value = _doctype_folder(doctype, rule)
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


def resolve_customer_field(doctype, rule=None):
    """Find the field on `doctype` that identifies the customer.

    Order: an explicit override on the rule, then a field literally named
    'customer', then a Link field pointing at Customer, then a Dynamic Link
    party field (e.g. Quotation's 'party_name'). Returns None if nothing fits.
    """
    meta = frappe.get_meta(doctype)

    override = getattr(rule, "customer_field", None) if rule else None
    if override:
        return override if meta.get_field(override) else None

    if meta.get_field("customer"):
        return "customer"
    for df in meta.fields:
        if df.fieldtype == "Link" and df.options == "Customer":
            return df.fieldname
    for df in meta.fields:
        if df.fieldtype == "Dynamic Link":
            return df.fieldname
    return None


def _link_target(doctype, docname, fieldname):
    """The doctype a link/dynamic-link field points at (for readable-name lookup)."""
    df = frappe.get_meta(doctype).get_field(fieldname)
    if not df:
        return None
    if df.fieldtype == "Link":
        return df.options
    if df.fieldtype == "Dynamic Link":
        return frappe.db.get_value(doctype, docname, df.options)
    return None


def _customer_path(rule, file_doc):
    """Build '<customer> / <doctype>', optionally under a '<company>' top folder.

    The customer field is auto-detected (or set on the rule); the folder is that
    id with the customer's readable name appended as 'id - name' when they differ
    (e.g. a naming-series 'CUST-0001 - Acme'). When 'Company as Top Folder' is on,
    the record's `company` field is prepended.
    """
    doctype = file_doc.attached_to_doctype
    docname = file_doc.attached_to_name

    parts = []
    if getattr(rule, "prepend_company", 0):
        company = _field_value(doctype, docname, "company")
        parts.append(_party_folder("Company", company))

    cust_field = resolve_customer_field(doctype, rule)
    if not cust_field:
        frappe.throw(
            _("No customer field found on '{0}'. Set a Customer Field on the SF Upload Rule.").format(
                doctype
            )
        )
    customer_id = _field_value(doctype, docname, cust_field)
    linked_doctype = _link_target(doctype, docname, cust_field)
    parts.append(_party_folder(linked_doctype, customer_id))
    parts.append(_doctype_folder(doctype, rule) or "Unfiled")
    return "/".join(parts)


def _doctype_folder(doctype, rule):
    """Render the doctype subfolder name, optionally translated per the rule.

    doctype_folder_naming: 'Original' | 'Translated' | 'Original - Translated' |
    'Translated - Original'. Translation uses doctype_folder_language; when no
    translation exists the original is kept (so it never reads 'Quotation -
    Quotation').
    """
    original = _clean(doctype)
    naming = getattr(rule, "doctype_folder_naming", None) or "Original"
    if naming == "Original":
        return original

    lang = getattr(rule, "doctype_folder_language", None)
    translated = _clean(_(doctype, lang=lang)) if lang else original
    if naming == "Translated":
        return translated or original

    if not translated or translated == original:
        return original
    if naming == "Translated - Original":
        return f"{translated} - {original}"
    return f"{original} - {translated}"


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


# characters SharePoint/OneDrive forbid in item names, plus control chars
_ILLEGAL = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
# reserved device names SharePoint rejects (case-insensitive, with/without ext)
_RESERVED = {
    "con", "prn", "aux", "nul", "desktop.ini", ".lock",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}


def _clean(value):
    """Sanitize a value into a safe SharePoint folder/file name segment.

    Replaces forbidden characters, trims leading/trailing spaces and trailing
    dots, drops a leading '~$', and guards reserved device names.
    """
    if value is None:
        return ""
    # SharePoint forbids leading/trailing spaces and trailing dots
    name = _ILLEGAL.sub("_", str(value)).strip().rstrip(". ")
    if name.startswith("~$"):
        name = name[2:].strip()
    if name in (".", ".."):
        return ""
    if name.split(".", 1)[0].lower() in _RESERVED or name.lower() in _RESERVED:
        name = f"_{name}"
    return name