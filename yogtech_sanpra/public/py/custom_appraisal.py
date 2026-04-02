import frappe
def fetch_template_goals(doc, method):
    if not doc.appraisal_template:
        return
    template = frappe.get_doc("Appraisal Template", doc.appraisal_template)
    doc.set("custom_appraisal_goal_item", [])
    for row in template.custom_goal:
        goal_name = frappe.db.get_value("Goal", row.goal, "goal_name")
        progress = frappe.db.get_value("Goal", row.goal, "progress")
        goal_score_weighted = (progress * row.weightage) / 100
        doc.append("custom_appraisal_goal_item", {
            "goal": goal_name,
            "weightage": row.weightage,
            "goal_completion": progress or 0,
            "goal_score_weighted": goal_score_weighted
        })
