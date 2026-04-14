# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class AuditBalanceSnapshot(Document):
	def validate(self):
		self._validate_engagement_company()
		self._validate_account_company()
		self._set_variance()

	def _validate_engagement_company(self):
		engagement_company = frappe.db.get_value("Audit Engagement", self.audit_engagement, "company")
		if engagement_company and engagement_company != self.company:
			frappe.throw(_("Audit Engagement must belong to the same company."), title=_("Validation"))

	def _validate_account_company(self):
		account_company = frappe.db.get_value("GL Account", self.gl_account, "company")
		if account_company and account_company != self.company:
			frappe.throw(_("GL Account must belong to the same company."), title=_("Validation"))

	def _set_variance(self):
		self.variance_amount = flt(self.audited_balance) - flt(self.book_balance)
