import frappe


def get_rule(doctype):
    """Return the enabled SF Upload Rule for this doctype, or None."""
    if not doctype:
        return None
    name = frappe.db.exists("SF Upload Rule", {"target_doctype": doctype, "enabled": 1})
    return frappe.get_cached_doc("SF Upload Rule", name) if name else None