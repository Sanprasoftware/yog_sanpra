function get_goal_filters(frm) {
	const filters = { employee: frm.doc.employee };

	if (frm.doc.start_date) {
		filters.start_date = [">=", frm.doc.start_date];
	}
	if (frm.doc.end_date) {
		filters.end_date = ["<=", frm.doc.end_date];
	}

	return filters;
}

function set_weighted_score(cdt, cdn) {
	const row = frappe.get_doc(cdt, cdn);
	const weighted_score =
		5 * (flt(row.weightage) / 100) * (flt(row.goal_completion) / 100);
	frappe.model.set_value(cdt, cdn, "goal_score_weighted", weighted_score);
}

function validate_total_weightage(frm) {
	const total = (frm.doc.custom_appraisal_goal_item || []).reduce(
		(sum, row) => sum + flt(row.weightage),
		0,
	);

	if (total > 100) {
		frappe.throw(
			__("Total goal weightage cannot exceed 100%. Current total is {0}%.", [
				flt(total, 2),
			]),
		);
	}
}

frappe.ui.form.on("Appraisal", {
	setup(frm) {
		frm.set_query("goal", "custom_appraisal_goal_item", () => ({
			filters: get_goal_filters(frm),
		}));
	},

	validate(frm) {
		validate_total_weightage(frm);
	},
});

frappe.ui.form.on("Appraisal Goal Item", {
	goal(frm, cdt, cdn) {
		const row = frappe.get_doc(cdt, cdn);
		if (!row.goal) {
			frappe.model.set_value(cdt, cdn, "goal_completion", 0);
			return;
		}

		frappe.db.get_value("Goal", row.goal, "progress").then(({ message }) => {
			frappe.model.set_value(
				cdt,
				cdn,
				"goal_completion",
				flt(message?.progress),
			);
			set_weighted_score(cdt, cdn);
			frm.refresh_field("custom_appraisal_goal_item");
		});
	},

	weightage(frm, cdt, cdn) {
		set_weighted_score(cdt, cdn);
		validate_total_weightage(frm);
	},

	goal_completion(frm, cdt, cdn) {
		set_weighted_score(cdt, cdn);
	},
});
