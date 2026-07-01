frappe.ui.form.on('SF Cloud Connection', {
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
    }
});