# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Ensure statutory audit script reports have consistent desk visibility."""

import frappe

REPORT_NAMES = (
	"Audit Engagement Summary",
	"Audit Finding Summary",
	"Audit Evidence Summary",
)

ROLES = (
	"System Manager",
	"Company Admin",
	"Desk User",
	"Report Manager",
)


def execute():
	valid_roles = set(frappe.get_all("Role", pluck="name"))
	roles = tuple(r for r in ROLES if r in valid_roles)
	if not roles:
		return

	for name in REPORT_NAMES:
		if not frappe.db.exists("Report", name):
			continue
		doc = frappe.get_doc("Report", name)
		doc.roles = []
		for role in roles:
			doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)

	frappe.clear_cache()
