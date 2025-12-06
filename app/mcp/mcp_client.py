"""
MCP (Model Context Protocol) client for financial data extraction.

Provides client implementation for connecting to MCP servers.
"""

import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx

from app.config import settings


class MCPClient:
    """
    Client for MCP (Model Context Protocol) interactions.
    
    MCP provides a standardized way to connect AI models
    to external data sources and tools.
    """
    
    def __init__(self):
        """Initialize MCP client."""
        self.server_url = settings.mcp_server_url
        self.api_key = settings.mcp_api_key
        self.timeout = settings.mcp_timeout
        self.enabled = settings.enable_mcp
        self._session_id: Optional[str] = None
    
    @property
    def is_available(self) -> bool:
        """Check if MCP is available and enabled."""
        return self.enabled and bool(self.server_url)
    
    async def connect(self) -> bool:
        """
        Establish connection to MCP server.
        
        Returns:
            True if connection successful
        """
        if not self.is_available:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.server_url}/connect",
                    headers=self._get_headers(),
                    json={"client_id": "financial_ai_app"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self._session_id = data.get("session_id")
                    return True
                    
        except Exception:
            pass
        
        return False
    
    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        if not self._session_id:
            return
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await client.post(
                    f"{self.server_url}/disconnect",
                    headers=self._get_headers(),
                    json={"session_id": self._session_id}
                )
        except Exception:
            pass
        finally:
            self._session_id = None
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from MCP server.
        
        Returns:
            List of available tool descriptions
        """
        if not self.is_available:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.server_url}/tools",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json().get("tools", [])
                    
        except Exception:
            pass
        
        return []
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            Tool execution result
        """
        if not self.is_available:
            return {"error": "MCP not available"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.server_url}/tools/{tool_name}",
                    headers=self._get_headers(),
                    json={
                        "session_id": self._session_id,
                        "arguments": arguments
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"Tool call failed: {response.status_code}",
                        "details": response.text
                    }
                    
        except Exception as e:
            return {"error": str(e)}
    
    async def extract_financial_data(
        self,
        content: str,
        content_type: str = "text",
        extraction_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Extract financial data using MCP tools.
        
        Args:
            content: Content to extract from (text, base64 image, etc.)
            content_type: Type of content (text, image, document)
            extraction_type: Type of extraction (bank_statement, pay_stub, etc.)
            
        Returns:
            Extracted financial data
        """
        return await self.call_tool(
            "extract_financial_data",
            {
                "content": content,
                "content_type": content_type,
                "extraction_type": extraction_type
            }
        )
    
    async def categorize_transaction(
        self,
        description: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Categorize a financial transaction using MCP.
        
        Args:
            description: Transaction description
            amount: Transaction amount
            
        Returns:
            Category information
        """
        return await self.call_tool(
            "categorize_transaction",
            {
                "description": description,
                "amount": amount
            }
        )
    
    async def analyze_document(
        self,
        document_content: str,
        document_type: str
    ) -> Dict[str, Any]:
        """
        Analyze a financial document using MCP.
        
        Args:
            document_content: Document content (text or base64)
            document_type: Type of document
            
        Returns:
            Document analysis results
        """
        return await self.call_tool(
            "analyze_document",
            {
                "content": document_content,
                "document_type": document_type
            }
        )
    
    async def get_resources(
        self,
        resource_type: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Get available resources from MCP server.
        
        Args:
            resource_type: Type of resources to retrieve
            
        Returns:
            List of resources
        """
        if not self.is_available:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.server_url}/resources",
                    headers=self._get_headers(),
                    params={"type": resource_type}
                )
                
                if response.status_code == 200:
                    return response.json().get("resources", [])
                    
        except Exception:
            pass
        
        return []
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for MCP requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        if self._session_id:
            headers["X-Session-ID"] = self._session_id
        
        return headers


# Singleton instance
mcp_client = MCPClient()

