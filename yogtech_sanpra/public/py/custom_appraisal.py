import frappe
from frappe.utils import flt


def calculate_goal_scores(doc, method=None):
	"""Sync Goal progress and calculate the weighted Appraisal goal score."""
	rows = doc.get("custom_appraisal_goal_item") or []
	total_weightage = sum(flt(row.weightage) for row in rows)
	if total_weightage > 100:
		frappe.throw(
			frappe._("Total goal weightage cannot exceed 100%. Current total is {0}%.").format(
				flt(total_weightage, 2)
			)
		)

	goal_names = list({row.goal for row in rows if row.goal})
	progress_by_goal = {}
	if goal_names:
		progress_by_goal = {
			goal.name: flt(goal.progress)
			for goal in frappe.get_all(
				"Goal",
				filters={"name": ("in", goal_names)},
				fields=["name", "progress"],
			)
		}

	goal_score_percentage = 0.0
	for row in rows:
		weightage = flt(row.weightage)
		goal_completion = progress_by_goal.get(row.goal, 0.0)
		goal_score_weighted = 5 * weightage / 100 * goal_completion / 100

		row.goal_completion = flt(
			goal_completion, row.precision("goal_completion")
		)
		row.goal_score_weighted = flt(
			goal_score_weighted, row.precision("goal_score_weighted")
		)
		goal_score_percentage += row.goal_score_weighted

	doc.goal_score_percentage = flt(
		goal_score_percentage, doc.precision("goal_score_percentage")
	)
	doc.total_score = flt(
		doc.goal_score_percentage, doc.precision("total_score")
	)
	doc.calculate_final_score()


# Backward-compatible hook name for sites/workers with cached hooks.
def fetch_template_goals(doc, method=None):
	calculate_goal_scores(doc, method)


def sync_goal_progress_to_draft_appraisals(doc, method=None):
	"""Push changed Goal progress into linked Draft Appraisals."""
	if isinstance(doc, str):
		doc = frappe.get_doc("Goal", doc)
	linked_rows = frappe.get_all(
		"Appraisal Goal Item",
		filters={
			"goal": doc.name,
			"parenttype": "Appraisal",
			"parentfield": "custom_appraisal_goal_item",
		},
		fields=["name", "parent", "weightage"],
	)
	if not linked_rows:
		return

	parent_names = list({row.parent for row in linked_rows})
	draft_appraisals = set(
		frappe.get_all(
			"Appraisal",
			filters={
				"name": ("in", parent_names),
				"employee": doc.employee,
				"docstatus": 0,
			},
			pluck="name",
		)
	)

	for appraisal_name in draft_appraisals:
		for row in linked_rows:
			if row.parent != appraisal_name:
				continue

			frappe.db.set_value(
				"Appraisal Goal Item",
				row.name,
				{
					"goal_completion": flt(doc.progress),
					"goal_score_weighted": 5 * flt(row.weightage) / 100 * flt(doc.progress) / 100,
				},
				update_modified=False,
			)

		appraisal_rows = frappe.get_all(
			"Appraisal Goal Item",
			filters={
				"parent": appraisal_name,
				"parenttype": "Appraisal",
				"parentfield": "custom_appraisal_goal_item",
			},
			fields=["weightage", "goal_completion"],
		)
		total_score = sum(
			5 * flt(row.weightage) / 100 * flt(row.goal_completion) / 100
			for row in appraisal_rows
		)
		appraisal = frappe.get_doc("Appraisal", appraisal_name)
		appraisal.goal_score_percentage = total_score
		appraisal.total_score = total_score
		appraisal.calculate_final_score()
		frappe.db.set_value(
			"Appraisal",
			appraisal_name,
			{
				"goal_score_percentage": appraisal.goal_score_percentage,
				"total_score": appraisal.total_score,
				"final_score": appraisal.final_score,
			},
		)
		appraisal.reload()
		appraisal.notify_update()
