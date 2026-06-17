// ============================================================================
// FrapNexus — adds a small "Guide" shortcut to the FrapNexus config forms.
// No styling is applied; the forms keep Frappe's stock look.
// ============================================================================

frappe.provide("frapnexus");

frapnexus.GUIDE_URL = "/frapnexus-guide";

frapnexus.add_guide_button = function (frm) {
	frm.add_custom_button(__("Guide"), () => window.open(frapnexus.GUIDE_URL, "_blank"));
};

["FN Cloud Connection", "FN Upload Rule"].forEach((dt) => {
	frappe.ui.form.on(dt, { refresh: frapnexus.add_guide_button });
});
