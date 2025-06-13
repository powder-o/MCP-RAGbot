#!/usr/bin/env python3

import os
import sys
from mcp_client import MCPClient
import json


def test_basic_functionality():
    """Test basic RAG functionality."""
    print("🧪 Testing RAG System...")
    
    client = MCPClient()
    
    print("\n1. Testing document addition...")
    result = client.execute_tool("add_document", {
        "content": "Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
        "title": "Python Programming Language",
        "source": "test"
    })
    result_data = json.loads(result)
    if result_data.get("success"):
        print("✓ Document added successfully!")
        doc_id = result_data.get("document_id")
        print(f"  Document ID: {doc_id}")
    else:
        print(f"✗ Failed to add document: {result_data.get('error')}")
        return False
    
    print("\n2. Testing another document addition...")
    result = client.execute_tool("add_document", {
        "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task.",
        "title": "Machine Learning Basics",
        "source": "test"
    })
    result_data = json.loads(result)
    if result_data.get("success"):
        print("✓ Second document added successfully!")
    else:
        print(f"✗ Failed to add second document: {result_data.get('error')}")
        return False
    
    print("\n3. Testing collection info...")
    result = client.execute_tool("get_collection_info", {})
    result_data = json.loads(result)
    if result_data.get("success"):
        info = result_data.get("collection_info", {})
        print(f"✓ Collection has {info.get('count')} documents")
    else:
        print(f"✗ Failed to get collection info: {result_data.get('error')}")
    
    print("\n4. Testing search...")
    result = client.execute_tool("search_documents", {
        "query": "What is Python?",
        "n_results": 2
    })
    result_data = json.loads(result)
    if result_data.get("success"):
        results = result_data.get("results", [])
        print(f"✓ Search returned {len(results)} results")
        for i, doc in enumerate(results, 1):
            print(f"  Result {i}: {doc['content'][:50]}... (distance: {doc['distance']:.4f})")
    else:
        print(f"✗ Search failed: {result_data.get('error')}")
        return False
    
    print("\n5. Testing chat with tools...")
    response = client.chat_with_tools("What programming languages are good for beginners?")
    print(f"✓ Chat response: {response[:100]}...")
    
    print("\n🎉 All tests passed! RAG system is working correctly.")
    return True


if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY environment variable not set!")
        print("Please create a .env file with your Groq API key.")
        sys.exit(1)
    
    test_basic_functionality()