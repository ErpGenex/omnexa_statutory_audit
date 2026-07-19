# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class AuditOpinionDraft(Document):
	def validate(self):
		self._validate_engagement_company()
		self._validate_status_requirements()

	def _validate_engagement_company(self):
		engagement_company = frappe.db.get_value("Audit Engagement", self.audit_engagement, "company")
		if engagement_company and engagement_company != self.company:
			frappe.throw(_("Audit Engagement must belong to the same company."), title=_("Validation"))

	def _validate_status_requirements(self):
		if self.status == "Issued" and not (self.opinion_text or "").strip():
			frappe.throw(_("Opinion Text is required before issuing the draft."), title=_("Validation"))
