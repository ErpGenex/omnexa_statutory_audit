# Copyright (c) 2026, Omnexa
from frappe.tests.utils import FrappeTestCase


class TestWave4SessionScope(FrappeTestCase):
	def test_vertical_dashboard(self):
		from omnexa_statutory_audit.vertical_dashboard_api import get_vertical_dashboard

		out = get_vertical_dashboard()
		self.assertEqual(out.get("app"), "omnexa_statutory_audit")
		self.assertIn("uses_session_context", out)
