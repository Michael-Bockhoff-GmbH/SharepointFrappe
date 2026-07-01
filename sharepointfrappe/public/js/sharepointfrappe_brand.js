// ============================================================================
// SharepointFrappe — adds a small "Guide" shortcut to the SharepointFrappe config forms.
// No styling is applied; the forms keep Frappe's stock look.
// ============================================================================

frappe.provide("sharepointfrappe");

sharepointfrappe.GUIDE_URL = "/sharepointfrappe-guide";

sharepointfrappe.add_guide_button = function (frm) {
	frm.add_custom_button(__("Guide"), () => window.open(sharepointfrappe.GUIDE_URL, "_blank"));
};

["SF Cloud Connection", "SF Upload Rule"].forEach((dt) => {
	frappe.ui.form.on(dt, { refresh: sharepointfrappe.add_guide_button });
});
