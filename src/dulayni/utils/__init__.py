from typing import List, Dict, Any
from langchain.tools import StructuredTool
from pydantic import create_model
from fastmcp import Client


async def convert_mcp_tools_to_langchain(fastmcp_tools: List[Any], mcp_client: Client) -> List[StructuredTool]:
    """
    Convert FastMCP tools tfrom langchain.tools import StructuredTool
from pydantic import create_modelo LangChain StructuredTools.
    
    Args:
        fastmcp_tools: List of FastMCP tool objects
        mcp_client: FastMCP client instance
    
    Returns:
        List[StructuredTool]: List of LangChain tools
    """
    langchain_tools = []
    
    for mcp_tool in fastmcp_tools:
        langchain_tool = await _convert_single_mcp_tool(mcp_tool, mcp_client)
        langchain_tools.append(langchain_tool)
        
    return langchain_tools


async def _convert_single_mcp_tool(mcp_tool: Any, mcp_client: Client) -> StructuredTool:
    """
    Convert a single FastMCP tool to a LangChain StructuredTool.
    
    Args:
        mcp_tool: The FastMCP tool object
        mcp_client: FastMCP client instance
    
    Returns:
        StructuredTool: LangChain tool
    """
    # Extract basic info from MCP tool
    tool_name = mcp_tool.name
    tool_description = mcp_tool.description
    input_schema = mcp_tool.inputSchema
    
    # Create Pydantic model from input schema
    args_schema = _create_pydantic_model_from_schema(tool_name, input_schema)
    
    # Create the async function that will be called by LangChain
    async def call_tool(**kwargs) -> str:
        """Async function to call the MCP tool"""
        try:
            # Call the FastMCP tool through the client
            result = await mcp_client.call_tool(tool_name, kwargs)
            
            # Handle FastMCP wrapped results
            if isinstance(result, dict) and 'result' in result:
                return str(result['result'])
            else:
                return str(result)
                
        except Exception as e:
            return f"Error calling tool {tool_name}: {str(e)}"
    
    # Create and return LangChain StructuredTool
    return StructuredTool(
        name=tool_name,
        description=tool_description,
        args_schema=args_schema,
        coroutine=call_tool,
        response_format='content_and_artifact'
    )


def _create_pydantic_model_from_schema(tool_name: str, schema: Dict[str, Any]) -> type:
    """
    Create a Pydantic model from a JSON schema.
    
    Args:
        tool_name: Name of the tool (used for model naming)
        schema: JSON schema dictionary
    
    Returns:
        Pydantic model class
    """
    if not isinstance(schema, dict) or 'properties' not in schema:
        # If no proper schema, create a generic model
        return create_model(f"{tool_name.title()}Args")
    
    properties = schema.get('properties', {})
    required_fields = schema.get('required', [])
    
    # Build field definitions for Pydantic model
    field_definitions = {}
    
    for field_name, field_schema in properties.items():
        field_type = _get_python_type_from_schema(field_schema)
        
        # Determine if field is required
        if field_name in required_fields:
            field_definitions[field_name] = (field_type, ...)
        else:
            field_definitions[field_name] = (field_type, None)
    
    # Create the Pydantic model
    model_name = f"{tool_name.title()}Args"
    return create_model(model_name, **field_definitions)


def _get_python_type_from_schema(field_schema: Dict[str, Any]) -> type:
    """
    Convert JSON schema type to Python type.
    
    Args:
        field_schema: JSON schema for a single field
    
    Returns:
        Python type
    """
    schema_type = field_schema.get('type', 'string')
    
    type_mapping = {
        'string': str,
        'integer': int,
        'number': float,
        'boolean': bool,
        'array': list,
        'object': dict
    }
    
    return type_mapping.get(schema_type, str)

# Optional: Utility functions for standalone use
async def convert_mcp_tools_to_langchain_tools(
    mcp_tools: List[Any], 
    mcp_client: Client
) -> List[StructuredTool]:
    """
    Standalone utility function to convert FastMCP tools to LangChain tools.
    
    Args:
        mcp_tools: List of FastMCP tool objects
        mcp_client: FastMCP client instance
    
    Returns:
        List[StructuredTool]: List of LangChain tools
    """
    return await convert_mcp_tools_to_langchain(mcp_tools, mcp_client)


async def convert_mcp_tool_to_langchain_tool(
    mcp_tool: Any, 
    mcp_client: Client
) -> StructuredTool:
    """
    Standalone utility function to convert a single FastMCP tool to LangChain tool.
    
    Args:
        mcp_tool: The FastMCP tool object
        mcp_client: FastMCP client instance
    
    Returns:
        StructuredTool: LangChain tool
    """
    return await _convert_single_mcp_tool(mcp_tool, mcp_client)
