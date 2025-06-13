from mcp.server.fastmcp import FastMCP
from groq_client import GroqClient
import json
import asyncio
from typing import List, Dict, Any
import subprocess
import threading
import time


class MCPClient:
    def __init__(self):
        self.groq_client = GroqClient()
        self.server_process = None
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_documents",
                    "description": "Search for relevant documents in the vector store based on a query",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query string"
                            },
                            "n_results": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_document",
                    "description": "Add a document to the vector store",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The document content to add"
                            },
                            "title": {
                                "type": "string",
                                "description": "Optional title for the document"
                            },
                            "source": {
                                "type": "string",
                                "description": "Optional source information"
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_file",
                    "description": "Add a file's content to the vector store",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to add"
                            },
                            "title": {
                                "type": "string",
                                "description": "Optional title for the document"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_collection_info",
                    "description": "Get information about the vector store collection",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool function by importing and calling it directly."""
        try:
            from mcp_server import (
                search_documents, add_document, add_file, 
                get_collection_info, delete_document
            )
            
            if tool_name == "search_documents":
                return search_documents(**arguments)
            elif tool_name == "add_document":
                return add_document(**arguments)
            elif tool_name == "add_file":
                return add_file(**arguments)
            elif tool_name == "get_collection_info":
                return get_collection_info()
            elif tool_name == "delete_document":
                return delete_document(**arguments)
            else:
                return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    def chat_with_tools(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Chat with the user, using MCP tools when needed.
        """
        if conversation_history is None:
            conversation_history = []
        
        system_message = {
            "role": "system",
            "content": """You are a helpful AI assistant with access to a vector database through MCP tools. 
You can search for documents, add new documents, and manage the knowledge base.

Available tools:
- search_documents: Search for relevant documents in the vector store
- add_document: Add new document content to the vector store  
- add_file: Add a file's content to the vector store
- get_collection_info: Get information about the vector store

Use these tools to help answer user questions by:
1. First searching for relevant information when users ask questions
2. Adding documents when users want to store information
3. Providing informed responses based on the retrieved context

Be helpful and use the tools appropriately to provide the best possible assistance."""
        }
        
        messages = [system_message] + conversation_history + [{"role": "user", "content": user_message}]
        
        response = self.groq_client.chat_completion(messages, self.tools)
        
        if not response or not response.choices:
            return "I'm sorry, I couldn't process your request."
        
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_responses = []
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                tool_result = self.execute_tool(tool_name, arguments)
                tool_responses.append(f"Tool: {tool_name}\nResult: {tool_result}")
                
                messages.append({
                    "role": "assistant", 
                    "content": None,
                    "tool_calls": [tool_call.dict()]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
            
            final_response = self.groq_client.chat_completion(messages)
            if final_response and final_response.choices:
                return final_response.choices[0].message.content
            else:
                return f"Tool executed successfully:\n\n" + "\n\n".join(tool_responses)
        else:
            return message.content