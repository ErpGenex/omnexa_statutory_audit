from __future__ import annotations

import frappe


@frappe.whitelist()
def preview_grc_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	from omnexa_core.omnexa_core.parity_api import preview_grc_kpi as _p
	return _p("statutory_audit", scenario=scenario, params=params)

