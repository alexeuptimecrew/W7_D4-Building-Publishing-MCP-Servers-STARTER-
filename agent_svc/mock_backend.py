"""In-memory stand-in for the Spring Boot orders-svc the MCP server fronts.

No network, no Postgres. Orders are seeded per tenant; refunds are recorded and
deduped by idempotency key, so a retried refund happens exactly once — the property
the api agent (Topic 4) relies on.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

# order_id -> record. Each order belongs to exactly one tenant (tenant isolation).
_SEED: dict[str, dict[str, Any]] = {
    "ord-synth-9001": {"order_id": "ord-synth-9001", "tenant_id": "tenant-a",
                       "status": "PAID", "amount_cents": 4250, "item": "KBD-87"},
    "ord-synth-9002": {"order_id": "ord-synth-9002", "tenant_id": "tenant-a",
                       "status": "PAID", "amount_cents": 32900, "item": "MON-27"},
    "ord-synth-7777": {"order_id": "ord-synth-7777", "tenant_id": "tenant-b",
                       "status": "PENDING", "amount_cents": 1999, "item": "CBL-3"},
}

_orders: dict[str, dict[str, Any]] = {}
_refunds: list[dict[str, Any]] = []
_idem: dict[str, dict[str, Any]] = {}   # idempotency-key -> the refund it produced


class NotFound(Exception):
    """Order missing, or owned by a different tenant (looks like 404 to the caller)."""


def reset() -> None:
    """Restore seed state — call at the start of a demo/test for determinism."""
    global _orders, _refunds, _idem
    _orders = {k: dict(v) for k, v in _SEED.items()}
    _refunds = []
    _idem = {}


def get_order(order_id: str, tenant_id: str) -> dict[str, Any]:
    o = _orders.get(order_id)
    if o is None or o["tenant_id"] != tenant_id:   # cross-tenant reads are 404, not leaks
        raise NotFound(f"order {order_id} not found for {tenant_id}")
    return dict(o)


def create_refund(order_id: str, tenant_id: str, amount: Decimal | None = None,
                  idempotency_key: str | None = None) -> dict[str, Any]:
    # Dedup FIRST: a retry with the same key returns the original result, no second refund.
    if idempotency_key is not None and idempotency_key in _idem:
        return dict(_idem[idempotency_key])
    o = get_order(order_id, tenant_id)             # validates tenant ownership
    amt = amount if amount is not None else Decimal(o["amount_cents"]) / 100
    record = {"refund_id": f"rf-{len(_refunds) + 1:04d}", "order_id": order_id,
              "tenant_id": tenant_id, "amount": str(amt), "status": "REFUNDED"}
    _refunds.append(record)
    if idempotency_key is not None:
        _idem[idempotency_key] = dict(record)
    return dict(record)


def refunds() -> list[dict[str, Any]]:
    return [dict(r) for r in _refunds]


reset()
