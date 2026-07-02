// Copyright (c) 2026, Octo Advisory and contributors
// For license information, please see license.txt

frappe.ui.form.on("SF Upload Rule", {
	refresh(frm) {
		set_field_options(frm);
	},
	target_doctype(frm) {
		// clear stale field picks when the doctype changes
		(frm.doc.folder_segments || []).forEach((row) => {
			if (row.segment_type === "Field Value") {
				frappe.model.set_value(row.doctype, row.name, "field_name", "");
			}
		});
		if (frm.doc.customer_field) {
			frm.set_value("customer_field", "");
		}
		set_field_options(frm);
	},
});

// Populate the field dropdowns from the selected target doctype:
//  - folder segment "Field" → any field (sorted A-Z)
//  - "Customer Field"       → Link / Dynamic Link fields (sorted A-Z)
function set_field_options(frm) {
	const grid = frm.fields_dict.folder_segments.grid;
	const dt = frm.doc.target_doctype;

	if (!dt) {
		grid.update_docfield_property("field_name", "options", "");
		grid.refresh();
		frm.set_df_property("customer_field", "options", "");
		return;
	}

	frappe.model.with_doctype(dt, () => {
		const skip = [
			"Section Break", "Column Break", "Tab Break", "HTML", "Table",
			"Table MultiSelect", "Button", "Fold", "Heading", "Image",
		];
		const fields = frappe.get_meta(dt).fields || [];

		const fieldnames = fields
			.filter((df) => df.fieldname && !skip.includes(df.fieldtype))
			.map((df) => df.fieldname)
			.sort((a, b) => a.localeCompare(b));
		grid.update_docfield_property("field_name", "options", ["", ...fieldnames].join("\n"));
		grid.refresh();

		const linkFields = fields
			.filter((df) => ["Link", "Dynamic Link"].includes(df.fieldtype) && df.fieldname)
			.map((df) => df.fieldname)
			.sort((a, b) => a.localeCompare(b));
		frm.set_df_property("customer_field", "options", ["", ...linkFields].join("\n"));
	});
}
