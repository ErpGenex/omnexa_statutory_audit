# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Engagement pipeline by company and fiscal period — supports ISA engagement documentation."""

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	conditions = ["e.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("e.branch = %(branch)s")
	if filters.get("fiscal_year"):
		conditions.append("e.fiscal_year = %(fiscal_year)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		if not filters.get("branch"):
			conditions.append("(e.branch IS NULL OR e.branch IN %(allowed_branches)s)")

	data = frappe.db.sql(
		f"""
		SELECT
			e.fiscal_year,
			e.status,
			COUNT(*) AS engagement_count
		FROM `tabAudit Engagement` e
		WHERE {' AND '.join(conditions)}
		GROUP BY e.fiscal_year, e.status
		ORDER BY e.fiscal_year, e.status
		""",
		filters,
		as_dict=True,
	)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Fiscal Year"), "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 140
	},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120
	},
		{"label": _("Engagements"), "fieldname": "engagement_count", "fieldtype": "Int", "width": 110
	},
	]
