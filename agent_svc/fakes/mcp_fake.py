"""Local stand-in for an MCP client session pointed at the W7D4 server.

`list_tools()` returns the tool catalogue the api agent discovers at runtime;
`call_tool()` dispatches to the in-repo mock orders-svc, honouring the X-Tenant and
Idempotency-Key headers the api agent attaches (Topic 4).
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from .. import mock_backend
from ..config import TENANTS


class _Tool:
    def __init__(self, name: str, description: str, input_schema: dict) -> None:
        self.name = name
        self.description = description
        self.inputSchema = input_schema


class _Catalogue:
    def __init__(self, tools: list[_Tool]) -> None:
        self.tools = tools


class _ToolResult:
    def __init__(self, content: Any) -> None:
        self.content = content


_TENANT_ENUM = {"type": "string", "enum": list(TENANTS)}

_TOOLS = [
    _Tool("orders.get_order", "Fetch an order by id for the caller tenant.",
          {"type": "object", "additionalProperties": False,
           "properties": {"order_id": {"type": "string"}, "tenant_id": _TENANT_ENUM},
           "required": ["order_id", "tenant_id"]}),
    _Tool("orders.create_refund", "Refund an order for the caller tenant.",
          {"type": "object", "additionalProperties": False,
           "properties": {"order_id": {"type": "string"}, "tenant_id": _TENANT_ENUM,
                          "reason": {"type": "string"}},
           "required": ["order_id", "tenant_id"]}),
]


class ClientSession:
    """A minimal async MCP session over the in-repo backend."""

    async def list_tools(self) -> _Catalogue:
        return _Catalogue(_TOOLS)

    async def call_tool(self, name: str, arguments: dict,
                        headers: dict | None = None) -> _ToolResult:
        headers = headers or {}
        tenant = headers.get("X-Tenant", arguments.get("tenant_id", "tenant-a"))
        idem = headers.get("Idempotency-Key")
        try:
            if name == "orders.get_order":
                return _ToolResult(mock_backend.get_order(arguments["order_id"], tenant))
            if name == "orders.create_refund":
                return _ToolResult(mock_backend.create_refund(
                    arguments["order_id"], tenant, amount=None, idempotency_key=idem))
        except mock_backend.NotFound as e:
            return _ToolResult({"error": "not_found", "detail": str(e)})
        return _ToolResult({"error": "unknown_tool", "name": name})


def open_session() -> ClientSession:
    return ClientSession()
