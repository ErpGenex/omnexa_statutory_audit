# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class AuditEvidence(Document):
	def validate(self):
		self._validate_company_consistency()
		self._validate_reference()

	def _validate_company_consistency(self):
		engagement_company = frappe.db.get_value("Audit Engagement", self.audit_engagement, "company")
		if engagement_company and engagement_company != self.company:
			frappe.throw(_("Audit Engagement must belong to the same company."), title=_("Validation"))
		if self.audit_finding:
			finding_company = frappe.db.get_value("Audit Finding", self.audit_finding, "company")
			if finding_company and finding_company != self.company:
				frappe.throw(_("Audit Finding must belong to the same company."), title=_("Validation"))

	def _validate_reference(self):
		if not (self.file_url or "").strip() and not (self.reference_note or "").strip():
			frappe.throw(_("Set File URL or Reference Note for evidence."), title=_("Validation"))
