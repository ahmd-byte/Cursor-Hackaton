"""
Custom MCP server for financial data tools.

Provides MCP-compatible server that exposes financial
extraction tools for AI agents.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.mcp.extractors import FinancialExtractor
from app.ai.gemini_client import gemini_client
from app.ai.groq_client import groq_client


class MCPServer:
    """
    Custom MCP server for financial AI tools.
    
    Exposes financial data extraction and analysis tools
    following the MCP protocol specification.
    """
    
    def __init__(self):
        """Initialize MCP server."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.gemini = gemini_client
        self.groq = groq_client
        self.extractor = FinancialExtractor()
        
        # Define available tools
        self.tools = {
            "extract_financial_data": {
                "name": "extract_financial_data",
                "description": "Extract structured financial data from text or documents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Content to extract from"
                        },
                        "content_type": {
                            "type": "string",
                            "enum": ["text", "image", "document"],
                            "description": "Type of content"
                        },
                        "extraction_type": {
                            "type": "string",
                            "enum": ["bank_statement", "pay_stub", "receipt", "general"],
                            "description": "Type of extraction"
                        }
                    },
                    "required": ["content"]
                }
            },
            "categorize_transaction": {
                "name": "categorize_transaction",
                "description": "Categorize a financial transaction",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Transaction description"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Transaction amount"
                        }
                    },
                    "required": ["description", "amount"]
                }
            },
            "analyze_spending": {
                "name": "analyze_spending",
                "description": "Analyze spending patterns from transaction list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transactions": {
                            "type": "array",
                            "description": "List of transactions to analyze"
                        }
                    },
                    "required": ["transactions"]
                }
            },
            "extract_amounts": {
                "name": "extract_amounts",
                "description": "Extract monetary amounts from text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to extract amounts from"
                        }
                    },
                    "required": ["text"]
                }
            }
        }
    
    async def connect(self, client_id: str) -> Dict[str, Any]:
        """
        Handle client connection.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Connection response with session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "client_id": client_id,
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        return {
            "session_id": session_id,
            "status": "connected",
            "server_info": {
                "name": "Financial AI MCP Server",
                "version": "1.0.0",
                "capabilities": ["tools", "resources"]
            }
        }
    
    async def disconnect(self, session_id: str) -> Dict[str, Any]:
        """
        Handle client disconnection.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Disconnection response
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        return {"status": "disconnected"}
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools.
        
        Returns:
            List of tool definitions
        """
        return list(self.tools.values())
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool call.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            session_id: Optional session ID
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        # Update session activity
        if session_id and session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
        
        # Route to appropriate handler
        handlers = {
            "extract_financial_data": self._handle_extract_financial_data,
            "categorize_transaction": self._handle_categorize_transaction,
            "analyze_spending": self._handle_analyze_spending,
            "extract_amounts": self._handle_extract_amounts
        }
        
        handler = handlers.get(tool_name)
        if handler:
            try:
                return await handler(arguments)
            except Exception as e:
                return {"error": str(e)}
        
        return {"error": "Handler not implemented"}
    
    async def _handle_extract_financial_data(
        self,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle extract_financial_data tool call."""
        content = arguments.get("content", "")
        content_type = arguments.get("content_type", "text")
        extraction_type = arguments.get("extraction_type", "general")
        
        if content_type == "text":
            # Use extractor for text content
            if extraction_type == "bank_statement":
                data = self.extractor.parse_bank_statement_text(content)
            else:
                data = {
                    "amounts": self.extractor.extract_amounts(content),
                    "dates": self.extractor.extract_dates(content),
                    "accounts": self.extractor.extract_account_numbers(content),
                    "transactions": self.extractor.extract_transactions(content)
                }
            
            return {
                "success": True,
                "extraction_type": extraction_type,
                "data": data,
                "confidence_score": 75
            }
        
        elif content_type == "image":
            # Use Gemini for image content
            try:
                data = await self.gemini.extract_financial_data_from_image(
                    image_data=content,
                    document_type=extraction_type
                )
                return {
                    "success": True,
                    "extraction_type": extraction_type,
                    "data": data,
                    "confidence_score": data.get("confidence_score", 70)
                }
            except Exception as e:
                return {"error": f"Image extraction failed: {str(e)}"}
        
        return {"error": f"Unsupported content type: {content_type}"}
    
    async def _handle_categorize_transaction(
        self,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle categorize_transaction tool call."""
        description = arguments.get("description", "")
        amount = arguments.get("amount", 0)
        
        # Use local extractor for quick categorization
        category = self.extractor.categorize_description(description)
        
        # Enhance with AI if confidence is low
        if category["confidence"] < 0.7:
            try:
                ai_category = await self.gemini.categorize_transaction(
                    description, amount
                )
                if ai_category.get("confidence", 0) > category["confidence"]:
                    category = ai_category
            except Exception:
                pass
        
        return {
            "success": True,
            "category": category["category"],
            "subcategory": category.get("subcategory"),
            "confidence": category["confidence"],
            "merchant_type": category.get("merchant_type"),
            "is_recurring": category.get("is_recurring", False)
        }
    
    async def _handle_analyze_spending(
        self,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle analyze_spending tool call."""
        transactions = arguments.get("transactions", [])
        
        if not transactions:
            return {
                "success": False,
                "error": "No transactions provided"
            }
        
        try:
            analysis = await self.groq.analyze_spending(transactions)
            return {
                "success": True,
                "analysis": analysis
            }
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def _handle_extract_amounts(
        self,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle extract_amounts tool call."""
        text = arguments.get("text", "")
        
        amounts = self.extractor.extract_amounts(text)
        
        return {
            "success": True,
            "amounts": amounts,
            "count": len(amounts)
        }
    
    def get_resources(
        self,
        resource_type: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Get available resources.
        
        Args:
            resource_type: Type of resources to return
            
        Returns:
            List of available resources
        """
        resources = [
            {
                "uri": "financial://categories",
                "name": "Transaction Categories",
                "description": "List of supported transaction categories",
                "mimeType": "application/json"
            },
            {
                "uri": "financial://extraction-types",
                "name": "Document Extraction Types",
                "description": "Supported document types for extraction",
                "mimeType": "application/json"
            }
        ]
        
        if resource_type != "all":
            resources = [r for r in resources if resource_type in r["uri"]]
        
        return resources


# Singleton instance
mcp_server = MCPServer()

