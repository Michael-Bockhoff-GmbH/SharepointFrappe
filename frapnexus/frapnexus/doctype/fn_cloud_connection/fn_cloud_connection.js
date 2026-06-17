frappe.ui.form.on('FN Cloud Connection', {
    refresh: function (frm) {
        if (frm.is_dirty()) return;
        if (frm.doc.status === 'Connected') {
            frm.add_custom_button(__('Edit Details'), function () {
                frm.set_value('status', 'Not Connected');
                frm.save();
            });
        } else {
            frm.add_custom_button(__('Connect'), function () {
                frm.call('connect').then((r) => {
                    if (r.message.ok) {
                        frm.reload_doc();
                        frappe.show_alert({ message: __("Connected"), indicator: "green" });
                    } else {
                        frappe.msgprint({ title: __("Could not connect"), message: r.message.error, indicator: "red" });
                    }
                });
            }).addClass("btn-primary");
        }
    },

    service_account_json_file: function (frm) {
        const file = frm.doc.service_account_json_file;
        if (!file) return;
        if (!file.toLowerCase().endsWith(".json")) {
            frappe.msgprint({
                title: __("Invalid File"),
                message: __("Please upload a .json file only."),
                indicator: "red",
            });
            frm.set_value("service_account_json_file", "");
            return;
        }

        fetch(file)
            .then((res) => res.text())
            .then((text) => {
                const json = JSON.parse(text);

                if (json.type !== "service_account") {
                    throw new Error("Invalid JSON");
                }

                return frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: frm.doctype,
                        name: frm.doc.name,
                        fieldname: "service_account_json",
                        value: text
                    }
                });
            })
            .then(() => {
                frm.reload_doc();
            })
            .catch(() => {
                frappe.msgprint(__("Invalid service account JSON"));
            });
    }
});