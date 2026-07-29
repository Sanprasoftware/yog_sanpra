import frappe

def if_checkmark_enbl(self, method):
    company = frappe.defaults.get_user_default("Company")

    if company and frappe.db.get_value("Company", company, "custom_mandatory_update_stock") == 1:

        for row in self.items:
            if frappe.db.get_value("Item", row.item_code, "is_stock_item") == 1:
                
                if not self.update_stock:
                    frappe.throw("Please enable 'Update Stock' before submitting.")
                break