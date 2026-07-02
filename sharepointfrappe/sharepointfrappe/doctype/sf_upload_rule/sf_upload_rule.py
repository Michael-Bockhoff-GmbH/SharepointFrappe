import frappe
from frappe import _
from frappe.model.document import Document


class SFUploadRule(Document):
    def validate(self):
        if self.folder_structure == "Group by Customer":
            meta = frappe.get_meta(self.target_doctype)
            if not meta.get_field("customer"):
                frappe.throw(
                    _("'{0}' has no 'customer' field, so 'Group by Customer' can't be used.").format(
                        self.target_doctype
                    )
                )
            if self.prepend_company and not meta.get_field("company"):
                frappe.throw(
                    _("'{0}' has no 'company' field; turn off 'Company as Top Folder'.").format(
                        self.target_doctype
                    )
                )
