frappe.ui.form.on("Work Order", {
    custom_standard_condition_details: function(frm) {
        if (!frm.doc.custom_standard_condition_details) return;

        frappe.call({
            method: "yogtech_sanpra.public.py.work_order.get_standard_condition_details",
            args: {
                standard_condition: frm.doc.custom_standard_condition_details
            },
            callback: function(r) {
                if (r.message) {
                    frm.clear_table("custom_items"); // clear previous rows
                    r.message.forEach(function(row) {
                        let new_row = frm.add_child("custom_items");
                        new_row.description = row.description;
                        new_row.specification = row.specification;
                        new_row.quantity = row.quantity;
                        new_row.remark = row.remark;
                        new_row.rating__dimension = row.rating__dimension;
                    });
                    frm.refresh_field("custom_items");
                }
            }
        });
    }
});
