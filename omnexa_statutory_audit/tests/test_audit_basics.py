import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, today


class TestStatutoryAuditBasics(FrappeTestCase):
	def setUp(self):
		super().setUp()
		if not frappe.db.exists("Currency", "EGP"):
			frappe.get_doc({"doctype": "Currency", "currency_name": "EGP", "symbol": "E£", "enabled": 1}).insert(
				ignore_permissions=True
			)
		if not frappe.db.exists("Country", "Egypt"):
			frappe.get_doc({"doctype": "Country", "country_name": "Egypt", "code": "EG"}).insert(
				ignore_permissions=True
			)

	def _make_company(self, abbr):
		if frappe.db.exists("Company", {"abbr": abbr}):
			return frappe.db.get_value("Company", {"abbr": abbr}, "name")
		return frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": f"Audit Co {abbr}",
				"abbr": abbr,
				"default_currency": "EGP",
				"country": "Egypt",
				"status": "Active",
			}
		).insert(ignore_permissions=True).name

	def _make_branch(self, company, code):
		return frappe.get_doc(
			{"doctype": "Branch", "company": company, "branch_name": f"Branch {code}", "branch_code": code, "status": "Active"}
		).insert(ignore_permissions=True).name

	def _make_fiscal_year(self, company):
		fy = frappe.get_doc(
			{
				"doctype": "Fiscal Year",
				"title": "Audit FY",
				"company": company,
				"year_start_date": getdate(today()),
				"year_end_date": add_days(getdate(today()), 365),
				"periods": [
					{
						"period_name": "P1",
						"period_start_date": getdate(today()),
						"period_end_date": add_days(getdate(today()), 365),
						"frozen": 0,
					}
				],
			}
		)
		fy.insert(ignore_permissions=True)
		return fy.name

	def _make_gl(self, company):
		return frappe.get_doc(
			{
				"doctype": "GL Account",
				"company": company,
				"account_number": f"9{frappe.generate_hash(length=5)}",
				"account_name": "Audit Test Account",
				"is_group": 0,
				"account_type": "Asset",
			}
		).insert(ignore_permissions=True).name

	def test_engagement_rejects_cross_company_branch(self):
		company_a = self._make_company("AUA")
		company_b = self._make_company("AUB")
		branch_b = self._make_branch(company_b, "B1")
		fy_a = self._make_fiscal_year(company_a)
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Audit Engagement",
					"engagement_title": "Annual Audit",
					"company": company_a,
					"branch": branch_b,
					"fiscal_year": fy_a,
					"engagement_start_date": today(),
					"engagement_end_date": add_days(today(), 30),
				}
			).insert(ignore_permissions=True)

	def test_balance_snapshot_sets_variance(self):
		company = self._make_company("AUC")
		branch = self._make_branch(company, "C1")
		fy = self._make_fiscal_year(company)
		eng = frappe.get_doc(
			{
				"doctype": "Audit Engagement",
				"engagement_title": "Audit 2026",
				"company": company,
				"branch": branch,
				"fiscal_year": fy,
				"engagement_start_date": today(),
				"engagement_end_date": add_days(today(), 30),
			}
		).insert(ignore_permissions=True)
		gl = self._make_gl(company)
		snap = frappe.get_doc(
			{
				"doctype": "Audit Balance Snapshot",
				"audit_engagement": eng.name,
				"company": company,
				"fiscal_year": fy,
				"gl_account": gl,
				"book_balance": 1000,
				"audited_balance": 900,
			}
		).insert(ignore_permissions=True)
		self.assertEqual(float(snap.variance_amount), -100.0)

	def test_finding_evidence_and_opinion_flow(self):
		company = self._make_company("AUD")
		branch = self._make_branch(company, "D1")
		fy = self._make_fiscal_year(company)
		eng = frappe.get_doc(
			{
				"doctype": "Audit Engagement",
				"engagement_title": "Audit Flow",
				"company": company,
				"branch": branch,
				"fiscal_year": fy,
				"engagement_start_date": today(),
				"engagement_end_date": add_days(today(), 30),
			}
		).insert(ignore_permissions=True)
		gl = self._make_gl(company)
		snap = frappe.get_doc(
			{
				"doctype": "Audit Balance Snapshot",
				"audit_engagement": eng.name,
				"company": company,
				"fiscal_year": fy,
				"gl_account": gl,
				"book_balance": 1000,
				"audited_balance": 1000,
			}
		).insert(ignore_permissions=True)
		finding = frappe.get_doc(
			{
				"doctype": "Audit Finding",
				"audit_engagement": eng.name,
				"company": company,
				"balance_snapshot": snap.name,
				"finding_title": "Sample Finding",
				"severity": "Medium",
				"status": "Open",
				"observation": "Observation text",
			}
		).insert(ignore_permissions=True)
		evidence = frappe.get_doc(
			{
				"doctype": "Audit Evidence",
				"audit_engagement": eng.name,
				"company": company,
				"audit_finding": finding.name,
				"evidence_title": "Evidence 1",
				"evidence_type": "Document",
				"reference_note": "Working paper ref",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(evidence.name)

		opinion = frappe.get_doc(
			{
				"doctype": "Audit Opinion Draft",
				"audit_engagement": eng.name,
				"company": company,
				"opinion_type": "Unmodified",
				"status": "Issued",
				"opinion_text": "Draft opinion text",
			}
		).insert(ignore_permissions=True)
		self.assertTrue(opinion.name)
