# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe


@frappe.whitelist()
def preview_grc_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	from omnexa_core.omnexa_core.parity_api import preview_grc_kpi as _p

	return _p("statutory_audit", scenario=scenario, params=params)


@frappe.whitelist()
def preview_sector_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	"""SAP Wave C — sector KPI preview (omnexa_core bridge)."""
	from omnexa_core.omnexa_core.vertical_api import preview_sector_kpi as _core_preview

	return _core_preview("statutory_audit", scenario=scenario, params=params)
