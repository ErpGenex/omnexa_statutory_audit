# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""ISA 230 working paper index — engagements, findings, and evidence (not a legal opinion)."""

from __future__ import annotations

import frappe
from frappe import _

from omnexa_statutory_audit.omnexa_statutory_audit.report.audit_engagement_summary.audit_engagement_summary import (
	execute as engagement_execute,
)
from omnexa_statutory_audit.omnexa_statutory_audit.report.audit_evidence_summary.audit_evidence_summary import (
	execute as evidence_execute,
)
from omnexa_statutory_audit.omnexa_statutory_audit.report.audit_finding_summary.audit_finding_summary import (
	execute as finding_execute,
)


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required"))

	columns = [
		{"label": _("Workpaper"), "fieldname": "workpaper", "fieldtype": "Data", "width": 140},
		{"label": _("Engagement"), "fieldname": "audit_engagement", "fieldtype": "Link", "options": "Audit Engagement", "width": 160},
		{"label": _("Dimension 1"), "fieldname": "dim1", "fieldtype": "Data", "width": 120},
		{"label": _("Dimension 2"), "fieldname": "dim2", "fieldtype": "Data", "width": 120},
		{"label": _("Count"), "fieldname": "metric_count", "fieldtype": "Int", "width": 90},
	]

	data = []

	_, eng_rows = engagement_execute(filters)
	for row in eng_rows or []:
		data.append(
			{
				"workpaper": _("Engagements"),
				"audit_engagement": "",
				"dim1": row.get("fiscal_year"),
				"dim2": row.get("status"),
				"metric_count": row.get("engagement_count"),
			}
		)

	_, find_rows = finding_execute(filters)
	for row in find_rows or []:
		data.append(
			{
				"workpaper": _("Findings"),
				"audit_engagement": row.get("audit_engagement"),
				"dim1": row.get("severity"),
				"dim2": row.get("status"),
				"metric_count": row.get("finding_count"),
			}
		)

	_, ev_rows = evidence_execute(filters)
	for row in ev_rows or []:
		data.append(
			{
				"workpaper": _("Evidence"),
				"audit_engagement": row.get("audit_engagement"),
				"dim1": row.get("evidence_type"),
				"dim2": "",
				"metric_count": row.get("evidence_count"),
			}
		)

	disclaimer = _(
		"Working paper pack only — not a statutory audit opinion. Formal sign-off required per ISA 700."
	)
	return columns, data, disclaimer, None, None, False
