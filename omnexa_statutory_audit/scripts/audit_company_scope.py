#!/usr/bin/env python3
"""Audit company/branch scoping — omnexa_statutory_audit."""
from __future__ import annotations

import frappe

from omnexa_core.omnexa_core.session_scope import resolve_effective_branch, resolve_effective_company


def run():
	company = resolve_effective_company()
	branch = resolve_effective_branch(company)
	return {"ok": True, "app": "omnexa_statutory_audit", "company": company, "branch": branch, "uses_session_context": bool(company)}
