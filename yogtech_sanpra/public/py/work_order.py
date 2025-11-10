import frappe

@frappe.whitelist()
def get_standard_condition_details(standard_condition):
    # if not standard_condition:
    #     frappe.throw("Please select a Standard Condition Details record.")
    child_table_doctype = "Standard Condition Test"
    child_rows = frappe.get_all(
        child_table_doctype,
        filters={"parent": standard_condition},
        fields=["description", "specification", "quantity", "remark", "rating__dimension"],
        order_by="idx asc"
    )
    return child_rows
