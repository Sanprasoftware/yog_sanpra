frappe.ui.form.on("Stock Entry", {
    custom_additional_costs_template(frm) {

        if (!frm.doc.custom_additional_costs_template) {
            frm.clear_table("additional_costs");
            frm.refresh_field("additional_costs");
            return;
        }

        frappe.call({
            method: "yogtech_sanpra.public.py.stock_entry.get_additional_costs_temp",
            args: { doc: JSON.stringify(frm.doc) },
            callback(r) {
                frm.clear_table("additional_costs");

                if (!r.message) {
                    frm.refresh_field("additional_costs");
                    return;
                }

                r.message.forEach(row => {
                    frm.add_child("additional_costs", row);
                });

                frm.refresh_field("additional_costs");
            }
        });
    }
});
