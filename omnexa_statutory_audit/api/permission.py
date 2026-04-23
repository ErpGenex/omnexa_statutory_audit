# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

from urllib.parse import unquote

import frappe

_DEFAULT_ALLOWED_ROLES = frozenset({"General Manager", "Audit Supervisor", "المدير العام", "مراقب الحسابات"})
_AUDIT_DOCTYPES = frozenset(
	{"Audit Engagement", "Audit Finding", "Audit Evidence", "Audit Balance Snapshot", "Audit Opinion Draft"}
)


def _allowed_roles() -> set[str]:
	raw = frappe.conf.get("omnexa_statutory_audit_allowed_roles")
	if isinstance(raw, str) and raw.strip():
		return {r.strip() for r in raw.split(",") if r.strip()}
	if isinstance(raw, (list, tuple, set)):
		return {str(r).strip() for r in raw if str(r).strip()}
	return set(_DEFAULT_ALLOWED_ROLES)


def has_audit_supervisor_access(user: str | None = None) -> bool:
	user = user or frappe.session.user
	if not user or user == "Guest":
		return False
	if user == "Administrator":
		return True
	roles = set(frappe.get_roles(user) or [])
	return bool(roles.intersection(_allowed_roles()))


def assert_audit_supervisor_access(user: str | None = None) -> None:
	if has_audit_supervisor_access(user=user):
		return
	frappe.throw(
		frappe._("Access denied. Only General Manager and Audit Supervisor can access Statutory Audit."),
		frappe.PermissionError,
	)


def has_app_permission() -> bool:
	return has_audit_supervisor_access()


def has_doctype_permission(doc=None, user: str | None = None, permission_type: str | None = None) -> bool:
	return has_audit_supervisor_access(user=user)


def get_doctype_permission_query_conditions(user: str | None = None) -> str | None:
	if has_audit_supervisor_access(user=user):
		return None
	return "1=0"


def before_request() -> None:
	"""Request-level guard for Desk routes and direct API access to this app resources."""
	if not getattr(frappe.local, "request", None):
		return
	path = (frappe.local.request.path or "").strip()
	if not path:
		return
	for prefix in ("/assets/", "/files/", "/.well-known"):
		if path.startswith(prefix):
			return
	if has_audit_supervisor_access():
		return
	if path.startswith("/app/audit") or path.startswith("/app/statutory-audit"):
		assert_audit_supervisor_access()
	if path.startswith("/api/method/omnexa_statutory_audit."):
		assert_audit_supervisor_access()
	if path.startswith("/api/resource/"):
		resource = unquote(path[len("/api/resource/") :]).split("/", 1)[0].strip()
		if resource in _AUDIT_DOCTYPES:
			assert_audit_supervisor_access()

