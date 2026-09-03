# Copyright (c) 2026, ErpGenEx
# Auto-generated Global Excellence report pack

import frappe
from frappe import _


def execute(filters=None):
	data = frappe.db.sql(
		"""
		SELECT `name`, `audit_engagement`, `company`, `branch`, `evidence_title`, `evidence_type`
		FROM `tabAudit Evidence`
		ORDER BY modified DESC
		LIMIT 500
		""",
		as_dict=True,
	)
	columns = [
		{"label": _("Name"), "fieldname": "name", "fieldtype": "Link", "width": 140},
		{"label": _("Audit Engagement"), "fieldname": "audit_engagement", "fieldtype": "Link", "width": 120},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "width": 120},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "width": 120},
		{"label": _("Evidence Title"), "fieldname": "evidence_title", "fieldtype": "Data", "width": 120},
		{"label": _("Evidence Type"), "fieldname": "evidence_type", "fieldtype": "Select", "width": 120}
	]
	return columns, data
