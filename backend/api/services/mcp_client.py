"""
MCP Client Service
Direct function calls to MCP server tools (since we're in the same codebase).
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add MCP server to path
mcp_server_path = str(Path(__file__).parent.parent.parent / "mcp-server")
if mcp_server_path not in sys.path:
    sys.path.insert(0, mcp_server_path)


class MCPClient:
    """
    Direct client for MCP server tools.

    Simplified implementation that calls MCP functions directly
    since API and MCP server are in the same codebase.
    """

    def __init__(self):
        # Import MCP tools
        from tools.get_user_profile import get_user_profile
        from tools.calculate_credit_score import calculate_credit_score
        from tools.generate_emi_options import generate_emi_options
        from tools.explain_credit_decision import explain_credit_decision

        self.tools = {
            "get_user_profile_tool": get_user_profile,
            "calculate_credit_score_tool": calculate_credit_score,
            "generate_emi_options_tool": generate_emi_options,
            "explain_credit_decision_tool": explain_credit_decision
        }

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call an MCP tool.

        Args:
            tool_name: Name of the MCP tool
            parameters: Tool parameters

        Returns:
            Tool execution result as dictionary
        """
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool_func = self.tools[tool_name]

        # Call the synchronous function and get Pydantic model result
        # (FastAPI will handle this in a thread pool)
        if tool_name == "get_user_profile_tool":
            result = tool_func(parameters["user_id"])

        elif tool_name == "calculate_credit_score_tool":
            result = tool_func(
                parameters["user_id"],
                parameters.get("purchase_amount", 0)
            )

        elif tool_name == "generate_emi_options_tool":
            result = tool_func(
                parameters["credit_tier"],
                parameters["purchase_amount"],
                parameters["credit_limit"]
            )

        elif tool_name == "explain_credit_decision_tool":
            result = tool_func(
                parameters["user_id"],
                parameters["credit_score_result"],
                parameters["user_profile"]
            )

        # Convert Pydantic model to dictionary if it has model_dump method
        if hasattr(result, 'model_dump'):
            return result.model_dump()
        elif hasattr(result, 'dict'):
            return result.dict()
        else:
            return result

    async def close(self):
        """Close client (no-op for direct calls)."""
        pass


# Singleton instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
