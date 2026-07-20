# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Finding register aggregate — severity and status for ISA 450 (misstatements) visibility."""

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	conditions = ["f.company = %(company)s"]
	if filters.get("audit_engagement"):
		conditions.append("f.audit_engagement = %(audit_engagement)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append(
			"""f.audit_engagement in (
				SELECT e.name FROM `tabAudit Engagement` e
				WHERE e.company = %(company)s
				  AND (e.branch is null OR e.branch = '' OR e.branch in %(allowed_branches)s)
			)"""
		)

	data = frappe.db.sql(
		f"""
		SELECT
			f.audit_engagement,
			f.severity,
			f.status,
			COUNT(*) AS finding_count
		FROM `tabAudit Finding` f
		WHERE {' AND '.join(conditions)}
		GROUP BY f.audit_engagement, f.severity, f.status
		ORDER BY f.audit_engagement, f.severity, f.status
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
		{"label": _("Severity"), "fieldname": "severity", "fieldtype": "Data", "width": 100
	},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110
	},
		{"label": _("Findings"), "fieldname": "finding_count", "fieldtype": "Int", "width": 90
	},
	]
