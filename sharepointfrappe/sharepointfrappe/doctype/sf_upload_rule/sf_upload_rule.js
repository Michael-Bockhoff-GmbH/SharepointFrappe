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
		set_field_options(frm);
	},
});

// Populate the folder segment "Field" dropdown with the fields of the
// selected target doctype (layout-only fieldtypes excluded), sorted A-Z.
function set_field_options(frm) {
	const grid = frm.fields_dict.folder_segments.grid;
	const dt = frm.doc.target_doctype;

	if (!dt) {
		grid.update_docfield_property("field_name", "options", "");
		grid.refresh();
		return;
	}

	frappe.model.with_doctype(dt, () => {
		const skip = [
			"Section Break", "Column Break", "Tab Break", "HTML", "Table",
			"Table MultiSelect", "Button", "Fold", "Heading", "Image",
		];
		const fieldnames = (frappe.get_meta(dt).fields || [])
			.filter((df) => df.fieldname && !skip.includes(df.fieldtype))
			.map((df) => df.fieldname)
			.sort((a, b) => a.localeCompare(b));

		grid.update_docfield_property("field_name", "options", ["", ...fieldnames].join("\n"));
		grid.refresh();
	});
}
