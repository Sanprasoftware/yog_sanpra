import frappe
import json

@frappe.whitelist()
def get_additional_costs_temp(doc):
    doc = json.loads(doc)

    template = doc.get("custom_additional_costs_template")
    if not template:
        return []


    additional_cost = frappe.get_all(
        "Additional Costs Items",
        filters={"parent": template},
        fields=["expense_account", "description", "rate"],
        order_by="idx asc"
    )

    total_amount = 0
    for item in doc.get("items", []):
        if item.get("is_finished_item") == 1:
            total_amount = item.get("basic_amount", 0)
            break

    child_rows = []
    for row in additional_cost:
        child_rows.append({
            "expense_account": row.expense_account,
            "description": row.description,
            "custom_rate": row.rate,
            "amount": total_amount
        })
    return child_rows