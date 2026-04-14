from frappe.tests.utils import FrappeTestCase

from omnexa_statutory_audit import hooks, license_gate


class TestStatutoryAuditLicenseSmoke(FrappeTestCase):
	def test_license_gate_is_wired(self):
		self.assertEqual(hooks.before_request, ["omnexa_statutory_audit.license_gate.before_request"])
		self.assertEqual(license_gate._APP, "omnexa_statutory_audit")
