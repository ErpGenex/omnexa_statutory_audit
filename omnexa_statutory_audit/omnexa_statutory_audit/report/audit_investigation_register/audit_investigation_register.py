# Copyright (c) 2026, ErpGenEx
# Auto-generated Global Excellence report pack

import frappe
from frappe import _


def execute(filters=None):
	data = frappe.db.sql(
		"""
		SELECT `name`, `alert`, `title`, `status`, `owner_user`
		FROM `tabAudit Investigation`
		ORDER BY modified DESC
		LIMIT 500
		""",
		as_dict=True,
	)
	columns = [
		{"label": _("Name"), "fieldname": "name", "fieldtype": "Link", "width": 140},
		{"label": _("Audit Alert"), "fieldname": "alert", "fieldtype": "Link", "width": 120},
		{"label": _("Title"), "fieldname": "title", "fieldtype": "Data", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Select", "width": 120},
		{"label": _("Owner"), "fieldname": "owner_user", "fieldtype": "Link", "width": 120}
	]
	return columns, data
