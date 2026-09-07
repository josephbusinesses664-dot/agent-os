"""Integration tests.

* The mock-MCP test runs everywhere (it spins up a local JSON-RPC HTTP server).
* Postgres / Redis tests only run when AGENTOS_TEST_DATABASE_URL /
  AGENTOS_TEST_REDIS_URL are set (they require live services).
"""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# MCP client against a real local HTTP server
# ---------------------------------------------------------------------------

class _McpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        request = json.loads(self.rfile.read(length) or b"{}")
        method = request.get("method")
        if method == "initialize":
            result = {"protocolVersion": "2025-03-26",
                      "capabilities": {"tools": {}},
                      "serverInfo": {"name": "mock-mcp", "version": "1.0"}}
        elif method == "tools/list":
            result = {"tools": [{"name": "ping", "description": "ping"},
                                {"name": "echo", "description": "echo"}]}
        elif method == "tools/call" and request.get("params", {}).get("name") == "echo":
            result = {"content": [{"type": "text",
                                   "text": json.dumps(request["params"]["arguments"])}]}
        else:
            self.send_response(400)
            self.end_headers()
            return
        payload = json.dumps({"jsonrpc": "2.0", "id": request.get("id", 1),
                              "result": result}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):  # silence
        pass


@pytest.fixture
def mock_mcp_server():
    server = HTTPServer(("127.0.0.1", 0), _McpHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


@pytest.mark.asyncio
async def test_mcp_client_streamable_http(mock_mcp_server):
    from agentos.domain.models import McpServer
    from agentos.registries.mcp_registry import McpClient

    port = mock_mcp_server.server_address[1]
    client = McpClient(McpServer(name="mock", endpoint=f"http://127.0.0.1:{port}/mcp"))
    init = await client.initialize()
    assert init["protocolVersion"] == "2025-03-26"
    tools = await client.list_tools()
    assert "echo" in tools
    result = await client.call_tool("echo", {"x": 1})
    assert '"x": 1' in str(result)


@pytest.mark.asyncio
async def test_mcp_registry_call(mock_mcp_server):
    from agentos.config import Settings
    from agentos.db.memory import MemoryRepository
    from agentos.db.store import EntityStore
    from agentos.domain.models import McpServer
    from agentos.registries.mcp_registry import McpRegistry

    port = mock_mcp_server.server_address[1]
    registry = McpRegistry(EntityStore(MemoryRepository()))
    await registry.register(McpServer(name="mock", endpoint=f"http://127.0.0.1:{port}/mcp"))
    result = await registry.call_tool("mock", "echo", {"hello": "world"})
    assert result["ok"] is True
    assert "hello" in str(result["result"])


# ---------------------------------------------------------------------------
# Live Postgres / Redis (skip unless env vars provided)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_postgres_repository_roundtrip():
    url = os.environ.get("AGENTOS_TEST_DATABASE_URL")
    if not url:
        pytest.skip("set AGENTOS_TEST_DATABASE_URL to run the Postgres integration test")
    from agentos.db.postgres import PostgresRepository

    repo = PostgresRepository(url)
    await repo.init()
    try:
        await repo.put("tasks", "t1", {"task_id": "t1", "title": "hello"})
        doc = await repo.get("tasks", "t1")
        assert doc["title"] == "hello"
        assert await repo.count("tasks") >= 1
        await repo.delete("tasks", "t1")
        assert await repo.get("tasks", "t1") is None
    finally:
        await repo.close()


@pytest.mark.asyncio
async def test_redis_kv_and_queue():
    url = os.environ.get("AGENTOS_TEST_REDIS_URL")
    if not url:
        pytest.skip("set AGENTOS_TEST_REDIS_URL to run the Redis integration test")
    from agentos.db.postgres import RedisKV, RedisQueue

    kv = RedisKV(url)
    await kv.set("k", "v")
    assert await kv.get("k") == "v"
    assert await kv.incr("counter") >= 1
    queue = RedisQueue(url, queue_name="agentos-test-queue")
    await queue.enqueue({"task_id": "t1"})
    item = await queue.dequeue(timeout=1.0)
    assert item == {"task_id": "t1"}