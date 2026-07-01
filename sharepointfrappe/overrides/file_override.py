import frappe
from frappe.core.doctype.file.file import File
from sharepointfrappe.cloud import rule as rule_module
from sharepointfrappe.cloud import path_builder, picker


class CustomFile(File):
    def save_file(self, *args, **kwargs):
        rule = rule_module.get_rule(self.attached_to_doctype)

        # no rule, or Frappe-only mode → behave exactly like stock Frappe
        if not rule or rule.storage_mode == "Frappe only":
            return super().save_file(*args, **kwargs)

        # make sure content is loaded (handles content passed via kwargs/args)
        if args:
            self.content = args[0]
        elif "content" in kwargs:
            self.content = kwargs["content"]
        self.get_content()
        if not self._content:
            return super().save_file(*args, **kwargs)

        # populate metadata so the record is valid even without a disk write
        self._set_metadata()

        if rule.storage_mode == "Both":
            # normal disk write first, then push a copy to cloud
            result = super().save_file(*args, **kwargs)
            self._upload_to_cloud(rule)
            return result

        if rule.storage_mode == "Cloud only":
            # skip disk entirely → upload → point file_url at the cloud url
            cloud = self._upload_to_cloud(rule)
            self.file_url = cloud["web_url"]
            return {"file_name": self.file_name, "file_url": self.file_url}

        return super().save_file(*args, **kwargs)

    # ---- helpers ----

    def _set_metadata(self):
        import mimetypes
        from frappe.utils import cint
        from frappe.utils.file_manager import get_content_hash

        self.is_private = cint(self.is_private)
        self.content_type = mimetypes.guess_type(self.file_name)[0]
        self.file_size = len(self._content or b"")
        self.content_hash = get_content_hash(self._content)

    def _upload_to_cloud(self, rule):
        path = path_builder.build_path(rule, self)
        cloud_file_name = path_builder.build_filename(rule, self)
        result = picker.upload(
            rule.cloud_connection,
            path,
            cloud_file_name,
            self._content,
            rule.conflict_behavior,
        )
        # remember where it went, for serving/debugging later
        self.db_set("cloud_id", result["id"]) if not self.is_new() else None
        return result