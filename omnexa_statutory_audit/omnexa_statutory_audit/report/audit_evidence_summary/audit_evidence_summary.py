# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Audit evidence workpaper index by type — supports ISA 230 documentation expectations."""

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	conditions = ["ev.company = %(company)s"]
	if filters.get("audit_engagement"):
		conditions.append("ev.audit_engagement = %(audit_engagement)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append(
			"""ev.audit_engagement in (
				SELECT e.name FROM `tabAudit Engagement` e
				WHERE e.company = %(company)s
				  AND (e.branch is null OR e.branch = '' OR e.branch in %(allowed_branches)s)
			)"""
		)

	data = frappe.db.sql(
		f"""
		SELECT
			ev.audit_engagement,
			ev.evidence_type,
			COUNT(*) AS evidence_count
		FROM `tabAudit Evidence` ev
		WHERE {' AND '.join(conditions)}
		GROUP BY ev.audit_engagement, ev.evidence_type
		ORDER BY ev.audit_engagement, ev.evidence_type
		""",
		filters,
		as_dict=True,
	)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Audit Engagement"), "fieldname": "audit_engagement", "fieldtype": "Link", "options": "Audit Engagement", "width": 200
	},
		{"label": _("Evidence type"), "fieldname": "evidence_type", "fieldtype": "Data", "width": 130
	},
		{"label": _("Items"), "fieldname": "evidence_count", "fieldtype": "Int", "width": 90
	},
	]
