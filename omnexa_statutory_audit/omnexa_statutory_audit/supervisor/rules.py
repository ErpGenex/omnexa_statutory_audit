from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Iterable

import frappe


@dataclass(frozen=True)
class Finding:
	rule_code: str
	title: str
	severity: str
	applies_to: str
	reference_doctype: str
	reference_name: str
	company: str | None = None
	evidence: dict[str, Any] | None = None


def _table_exists(table_name: str) -> bool:
	return bool(frappe.db.sql("show tables like %s", (table_name,)))


def _get_company_from_doc(doctype: str, name: str) -> str | None:
	try:
		return frappe.db.get_value(doctype, name, "company")
	except Exception:
		return None


def _recent_cutoff(hours: int) -> str:
	return frappe.utils.add_to_date(frappe.utils.now_datetime(), hours=-int(hours)).strftime("%Y-%m-%d %H:%M:%S")


def rule_modified_after_submit(hours: int = 24) -> Iterable[Finding]:
	"""Docs modified after submit (docstatus=1) in last N hours."""
	# Covers common transactional doctypes if tables exist.
	cutoff = _recent_cutoff(hours)
	targets = [
		"Sales Invoice",
		"Purchase Invoice",
		"Payment Entry",
		"Journal Entry",
		"Stock Reconciliation",
		"Bank Reconciliation",
		"HR Payroll Entry",
	]
	for dt in targets:
		table = f"tab{dt}"
		if not _table_exists(table):
			continue
		for row in frappe.db.sql(
			f"""
			select name, modified, modified_by
			from `{table}`
			where docstatus = 1 and modified >= %(cutoff)s
			order by modified desc
			limit 200
			""",
			{"cutoff": cutoff},
			as_dict=True,
		):
			yield Finding(
				rule_code="modified_after_submit",
				title=f"{dt} modified after submit",
				severity="High",
				applies_to="GL",
				reference_doctype=dt,
				reference_name=row.name,
				company=_get_company_from_doc(dt, row.name),
				evidence={"modified": str(row.modified), "modified_by": row.modified_by},
			)


def rule_duplicate_sales_invoice_last_7d() -> Iterable[Finding]:
	"""Potential duplicates: same customer + base_grand_total within last 7 days."""
	if not _table_exists("tabSales Invoice"):
		return []
	cutoff = frappe.utils.add_days(frappe.utils.today(), -7)
	rows = frappe.db.sql(
		"""
		select customer, base_grand_total, count(*) as cnt
		from `tabSales Invoice`
		where docstatus = 1 and posting_date >= %(cutoff)s and customer is not null
		group by customer, base_grand_total
		having count(*) >= 2
		limit 200
		""",
		{"cutoff": cutoff},
		as_dict=True,
	)
	for r in rows:
		# fetch one recent doc to link
		name = frappe.db.get_value(
			"Sales Invoice",
			{"customer": r.customer, "base_grand_total": r.base_grand_total, "docstatus": 1, "posting_date": (">=", cutoff)},
			"name",
			order_by="modified desc",
		)
		if not name:
			continue
		yield Finding(
			rule_code="duplicate_sales_invoice",
			title="Potential duplicate Sales Invoices",
			severity="High",
			applies_to="Sales",
			reference_doctype="Sales Invoice",
			reference_name=name,
			company=_get_company_from_doc("Sales Invoice", name),
			evidence={"customer": r.customer, "base_grand_total": float(r.base_grand_total or 0), "count": int(r.cnt)},
		)


def rule_duplicate_payment_entry_last_7d() -> Iterable[Finding]:
	"""Potential duplicates: same party + paid_amount within last 7 days."""
	if not _table_exists("tabPayment Entry"):
		return []
	cutoff = frappe.utils.add_days(frappe.utils.today(), -7)
	rows = frappe.db.sql(
		"""
		select party_type, party, paid_amount, count(*) as cnt
		from `tabPayment Entry`
		where docstatus = 1 and posting_date >= %(cutoff)s and party is not null
		group by party_type, party, paid_amount
		having count(*) >= 2
		limit 200
		""",
		{"cutoff": cutoff},
		as_dict=True,
	)
	for r in rows:
		name = frappe.db.get_value(
			"Payment Entry",
			{"party_type": r.party_type, "party": r.party, "paid_amount": r.paid_amount, "docstatus": 1, "posting_date": (">=", cutoff)},
			"name",
			order_by="modified desc",
		)
		if not name:
			continue
		yield Finding(
			rule_code="duplicate_payment_entry",
			title="Potential duplicate Payment Entries",
			severity="High",
			applies_to="Banking",
			reference_doctype="Payment Entry",
			reference_name=name,
			company=_get_company_from_doc("Payment Entry", name),
			evidence={
				"party_type": r.party_type,
				"party": r.party,
				"paid_amount": float(r.paid_amount or 0),
				"count": int(r.cnt),
			},
		)


def rule_journal_entry_near_period_close(days: int = 2) -> Iterable[Finding]:
	"""Journal Entries posted in last N days of current month."""
	if not _table_exists("tabJournal Entry"):
		return []
	today = frappe.utils.getdate(frappe.utils.today())
	# last day of month
	last = frappe.utils.get_last_day(today)
	if (last - today).days > int(days):
		return []
	start = frappe.utils.add_days(last, -int(days))
	for row in frappe.db.sql(
		"""
		select name, posting_date, modified_by
		from `tabJournal Entry`
		where docstatus = 1 and posting_date >= %(start)s and posting_date <= %(last)s
		order by posting_date desc, modified desc
		limit 200
		""",
		{"start": start, "last": last},
		as_dict=True,
	):
		yield Finding(
			rule_code="je_near_close",
			title="Journal Entry near period close",
			severity="Medium",
			applies_to="GL",
			reference_doctype="Journal Entry",
			reference_name=row.name,
			company=_get_company_from_doc("Journal Entry", row.name),
			evidence={"posting_date": str(row.posting_date), "modified_by": row.modified_by},
		)


def builtin_rule_set() -> list[tuple[str, Any]]:
	"""Return list of (rule_code, callable) for built-in rules."""
	return [
		("modified_after_submit", rule_modified_after_submit),
		("duplicate_sales_invoice", rule_duplicate_sales_invoice_last_7d),
		("duplicate_payment_entry", rule_duplicate_payment_entry_last_7d),
		("je_near_close", rule_journal_entry_near_period_close),
	]


def upsert_alert(f: Finding) -> str:
	"""Idempotent upsert: one open alert per (rule_code, reference_doctype, reference_name)."""
	key = {"rule_code": f.rule_code, "reference_doctype": f.reference_doctype, "reference_name": f.reference_name}
	existing = frappe.db.get_value("Audit Alert", key, "name")
	values = {
		"title": f.title,
		"severity": f.severity,
		"applies_to": f.applies_to,
		"rule_code": f.rule_code,
		"company": f.company,
		"evidence_json": json.dumps(f.evidence or {}, separators=(",", ":")),
	}
	if existing:
		# do not overwrite status if already in progress; keep latest evidence
		frappe.db.set_value("Audit Alert", existing, values, update_modified=True)
		return existing
	doc = frappe.get_doc({"doctype": "Audit Alert", **key, **values})
	doc.insert(ignore_permissions=True)
	return doc.name


def run_daily_supervisor(hours: int = 24) -> dict[str, Any]:
	"""Run built-in rules and create/update alerts. Designed for daily scheduler."""
	created_or_updated: list[str] = []
	for _code, fn in builtin_rule_set():
		try:
			findings = fn(hours) if _code == "modified_after_submit" else fn()
			for f in findings or []:
				try:
					created_or_updated.append(upsert_alert(f))
				except Exception:
					frappe.log_error(title=f"Audit Supervisor rule upsert: {_code}", message=frappe.get_traceback())
		except Exception:
			frappe.log_error(title=f"Audit Supervisor rule run: {_code}", message=frappe.get_traceback())
	return {"alerts_created_or_updated": len(created_or_updated), "alert_ids": created_or_updated[:50]}

