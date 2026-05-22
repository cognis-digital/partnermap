"""PARTNERMAP MCP server — exposes scan() as an MCP tool for Cognis.Studio."""
from __future__ import annotations
from partnermap.core import scan, to_json

def serve() -> int:
    """Start an MCP stdio server. Requires the optional 'mcp' extra:
        pip install "cognis-partnermap[mcp]"
    """
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception:
        print("Install the MCP extra: pip install 'cognis-partnermap[mcp]'")
        return 1
    app = FastMCP("partnermap")

    @app.tool()
    def partnermap_scan(target: str) -> str:
        """Track partnership/channel agreements as YAML records and compute account overlap, co-sell coverage gaps, and renewal/expiry alerts.. Returns JSON findings."""
        return to_json(scan(target))

    app.run()
    return 0
