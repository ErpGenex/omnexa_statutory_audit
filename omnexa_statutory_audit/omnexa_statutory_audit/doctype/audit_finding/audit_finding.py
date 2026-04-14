# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class AuditFinding(Document):
	def validate(self):
		self._validate_company_consistency()
		self._validate_closure_reason()

	def _validate_company_consistency(self):
		engagement_company = frappe.db.get_value("Audit Engagement", self.audit_engagement, "company")
		if engagement_company and engagement_company != self.company:
			frappe.throw(_("Audit Engagement must belong to the same company."), title=_("Validation"))
		if self.balance_snapshot:
			snapshot_company = frappe.db.get_value("Audit Balance Snapshot", self.balance_snapshot, "company")
			if snapshot_company and snapshot_company != self.company:
				frappe.throw(_("Balance Snapshot must belong to the same company."), title=_("Validation"))

	def _validate_closure_reason(self):
		if self.status == "Closed" and not (self.closure_note or "").strip():
			frappe.throw(_("Closure Note is required when finding is Closed."), title=_("Validation"))
