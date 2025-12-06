"""
MCP (Model Context Protocol) module.

Contains MCP client and server implementations for financial data extraction.
"""

from app.mcp.mcp_client import MCPClient
from app.mcp.extractors import FinancialExtractor
from app.mcp.mcp_server import MCPServer

__all__ = [
    "MCPClient",
    "FinancialExtractor",
    "MCPServer",
]

