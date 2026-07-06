import frappe
from frappe import _
from frappe.model.document import Document

from sharepointfrappe.cloud import path_builder


class SFUploadRule(Document):
    def validate(self):
        if self.folder_structure == "Group by Customer":
            if not path_builder.resolve_customer_field(self.target_doctype, self):
                frappe.throw(
                    _("Couldn't find a customer field on '{0}'. Pick one in 'Customer Field'.").format(
                        self.target_doctype
                    )
                )
            if self.prepend_company and not frappe.get_meta(self.target_doctype).get_field("company"):
                frappe.throw(
                    _("'{0}' has no 'company' field; turn off 'Company as Top Folder'.").format(
                        self.target_doctype
                    )
                )
