import frappe

def validate_weightage(doc, method):
    total_weightage = 0
    for row in doc.custom_goal:
        total_weightage += float(row.weightage or 0)
    if round(total_weightage, 2) != 100:
        frappe.throw(
            f"Total weightage for all Criteria must add up to 100. Currently, it is {total_weightage}%"
        )
