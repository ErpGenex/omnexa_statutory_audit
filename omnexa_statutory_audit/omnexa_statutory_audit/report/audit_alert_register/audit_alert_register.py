# Copyright (c) 2026, ErpGenEx
# Auto-generated Global Excellence report pack

import frappe
from frappe import _


def execute(filters=None):
	data = frappe.db.sql(
		"""
		SELECT `name`, `title`, `status`, `severity`, `applies_to`, `rule_code`
		FROM `tabAudit Alert`
		ORDER BY modified DESC
		LIMIT 500
		""",
		as_dict=True,
	)
	columns = [
		{"label": _("Name"), "fieldname": "name", "fieldtype": "Link", "width": 140},
		{"label": _("Title"), "fieldname": "title", "fieldtype": "Data", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Select", "width": 120},
		{"label": _("Severity"), "fieldname": "severity", "fieldtype": "Select", "width": 120},
		{"label": _("Area"), "fieldname": "applies_to", "fieldtype": "Select", "width": 120},
		{"label": _("Rule Code"), "fieldname": "rule_code", "fieldtype": "Data", "width": 120}
	]
	return columns, data
