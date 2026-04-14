# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class AuditEngagement(Document):
	def validate(self):
		self._validate_branch_company()
		self._validate_date_window()

	def _validate_branch_company(self):
		if not self.branch:
			return
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if branch_company != self.company:
			frappe.throw(_("Branch must belong to the same company."), title=_("Validation"))

	def _validate_date_window(self):
		if self.engagement_start_date and self.engagement_end_date:
			if getdate(self.engagement_start_date) > getdate(self.engagement_end_date):
				frappe.throw(_("Engagement Start Date cannot be after Engagement End Date."), title=_("Validation"))
