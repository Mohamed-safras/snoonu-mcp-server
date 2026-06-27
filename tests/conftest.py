import asyncio
import json

import pytest


@pytest.fixture
def fake_redis():
    """A fresh in-memory Redis stand-in per test, so cache/rate-limit state never leaks."""
    fakeredis = pytest.importorskip("fakeredis")
    return fakeredis.FakeRedis(decode_responses=True)


def call_tool(mcp, name: str, arguments: dict) -> dict:
    """Invoke an MCP tool synchronously and parse its JSON text content."""
    result = asyncio.run(mcp.call_tool(name, arguments))
    return json.loads(result[0].text)
