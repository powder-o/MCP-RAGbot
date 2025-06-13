from mcp.server.fastmcp import FastMCP
from vector_store import VectorStore
import json
from typing import Dict, Any, List
import os

print("Initializing FastMCP server...")
mcp = FastMCP("RAG Vector Store Server")

print("Initializing vector store...")
vector_store = VectorStore()
print("Vector store initialized successfully")


@mcp.tool()
def search_documents(query: str, n_results: int = 5) -> str:
    """
    Search for relevant documents in the vector store based on a query.
    
    Args:
        query: The search query string
        n_results: Number of results to return (default: 5)
    
    Returns:
        JSON string containing the search results with content, metadata, and relevance scores
    """
    try:
        results = vector_store.search(query, n_results)
        return json.dumps({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@mcp.tool()
def add_document(content: str, title: str = None, source: str = None, **metadata) -> str:
    """
    Add a document to the vector store.
    
    Args:
        content: The document content to add
        title: Optional title for the document
        source: Optional source information
        **metadata: Additional metadata as key-value pairs
    
    Returns:
        JSON string containing the operation result and document ID
    """
    try:
        doc_metadata = {}
        if title:
            doc_metadata['title'] = title
        if source:
            doc_metadata['source'] = source
        doc_metadata.update(metadata)
        
        doc_id = vector_store.add_document(content, doc_metadata)
        return json.dumps({
            "success": True,
            "document_id": doc_id,
            "message": "Document added successfully",
            "metadata": doc_metadata
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@mcp.tool()
def add_file(file_path: str, title: str = None) -> str:
    """
    Add a file's content to the vector store.
    
    Args:
        file_path: Path to the file to add
        title: Optional title for the document (defaults to filename)
    
    Returns:
        JSON string containing the operation result and document ID
    """
    try:
        if not os.path.exists(file_path):
            return json.dumps({
                "success": False,
                "error": f"File not found: {file_path}"
            })
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not title:
            title = os.path.basename(file_path)
        
        metadata = {
            'title': title,
            'source': file_path,
            'type': 'file'
        }
        
        doc_id = vector_store.add_document(content, metadata)
        return json.dumps({
            "success": True,
            "document_id": doc_id,
            "message": f"File '{file_path}' added successfully",
            "metadata": metadata
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@mcp.tool()
def get_collection_info() -> str:
    """
    Get information about the vector store collection.
    
    Returns:
        JSON string containing collection information
    """
    try:
        info = vector_store.get_collection_info()
        return json.dumps({
            "success": True,
            "collection_info": info
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@mcp.tool()
def delete_document(document_id: str) -> str:
    """
    Delete a document from the vector store.
    
    Args:
        document_id: The ID of the document to delete
    
    Returns:
        JSON string containing the operation result
    """
    try:
        success = vector_store.delete_document(document_id)
        if success:
            return json.dumps({
                "success": True,
                "message": f"Document '{document_id}' deleted successfully"
            })
        else:
            return json.dumps({
                "success": False,
                "error": f"Failed to delete document '{document_id}'"
            })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    try:
        print("Starting MCP server...")
        mcp.run()
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()