# Copyright (c) 2026, ErpGenEx
from frappe.tests.utils import FrappeTestCase

from omnexa_core.omnexa_core.grc_parity import preview_grc


class TestSapParityGrcApp(FrappeTestCase):
	def test_grc_kpi(self):
		out = preview_grc("statutory_audit", open_findings=1, evidence_locked=5, evidence_total=10)
		self.assertEqual(out["vertical"], "statutory_audit")
