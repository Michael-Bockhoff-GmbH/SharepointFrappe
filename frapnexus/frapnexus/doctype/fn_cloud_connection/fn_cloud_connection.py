import frappe
from frappe.model.document import Document
from frapnexus.cloud import picker


class FNCloudConnection(Document):
    @frappe.whitelist()
    def connect(self):
        try:
            result = picker.connect(self.name)
        except Exception as e:
            result = {"ok": False, "error": str(e)}
        self.db_set("status", "Connected" if result.get("ok") else "Not Connected")
        return result