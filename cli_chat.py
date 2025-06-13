#!/usr/bin/env python3

import os
import sys
from mcp_client import MCPClient
from typing import List, Dict
import json


class CLIChat:
    def __init__(self):
        self.client = MCPClient()
        self.conversation_history = []
        self.commands = {
            '/help': self.show_help,
            '/add': self.add_document_interactive,
            '/addfile': self.add_file_interactive,
            '/search': self.search_interactive,
            '/info': self.show_collection_info,
            '/clear': self.clear_history,
            '/quit': self.quit_chat,
            '/exit': self.quit_chat
        }
    
    def show_help(self):
        """Display help information."""
        help_text = """
RAG Chatbot Commands:
---------------------
/help      - Show this help message
/add       - Add a document to the knowledge base
/addfile   - Add a file to the knowledge base
/search    - Search the knowledge base
/info      - Show collection information
/clear     - Clear conversation history
/quit      - Exit the chat
/exit      - Exit the chat

You can also just type your questions naturally, and the AI will automatically
search the knowledge base when needed and provide informed responses.
        """
        print(help_text)
    
    def add_document_interactive(self):
        """Interactive document addition."""
        print("\n--- Add Document ---")
        content = input("Enter document content: ").strip()
        if not content:
            print("Error: Content cannot be empty")
            return
        
        title = input("Enter title (optional): ").strip() or None
        source = input("Enter source (optional): ").strip() or None
        
        try:
            result = self.client.execute_tool("add_document", {
                "content": content,
                "title": title,
                "source": source
            })
            result_data = json.loads(result)
            if result_data.get("success"):
                print(f"✓ Document added successfully! ID: {result_data.get('document_id')}")
            else:
                print(f"✗ Error: {result_data.get('error')}")
        except Exception as e:
            print(f"✗ Error adding document: {e}")
    
    def add_file_interactive(self):
        """Interactive file addition."""
        print("\n--- Add File ---")
        file_path = input("Enter file path: ").strip()
        if not file_path:
            print("Error: File path cannot be empty")
            return
        
        title = input("Enter title (optional, defaults to filename): ").strip() or None
        
        try:
            result = self.client.execute_tool("add_file", {
                "file_path": file_path,
                "title": title
            })
            result_data = json.loads(result)
            if result_data.get("success"):
                print(f"✓ File added successfully! ID: {result_data.get('document_id')}")
            else:
                print(f"✗ Error: {result_data.get('error')}")
        except Exception as e:
            print(f"✗ Error adding file: {e}")
    
    def search_interactive(self):
        """Interactive search."""
        print("\n--- Search Knowledge Base ---")
        query = input("Enter search query: ").strip()
        if not query:
            print("Error: Query cannot be empty")
            return
        
        n_results = input("Number of results (default 5): ").strip()
        try:
            n_results = int(n_results) if n_results else 5
        except ValueError:
            n_results = 5
        
        try:
            result = self.client.execute_tool("search_documents", {
                "query": query,
                "n_results": n_results
            })
            result_data = json.loads(result)
            if result_data.get("success"):
                results = result_data.get("results", [])
                print(f"\n✓ Found {len(results)} results:")
                for i, doc in enumerate(results, 1):
                    print(f"\n--- Result {i} ---")
                    print(f"Content: {doc['content'][:200]}{'...' if len(doc['content']) > 200 else ''}")
                    print(f"Distance: {doc['distance']:.4f}")
                    if doc.get('metadata'):
                        print(f"Metadata: {doc['metadata']}")
            else:
                print(f"✗ Error: {result_data.get('error')}")
        except Exception as e:
            print(f"✗ Error searching: {e}")
    
    def show_collection_info(self):
        """Show collection information."""
        try:
            result = self.client.execute_tool("get_collection_info", {})
            result_data = json.loads(result)
            if result_data.get("success"):
                info = result_data.get("collection_info", {})
                print(f"\n--- Collection Info ---")
                print(f"Name: {info.get('name')}")
                print(f"Document Count: {info.get('count')}")
            else:
                print(f"✗ Error: {result_data.get('error')}")
        except Exception as e:
            print(f"✗ Error getting collection info: {e}")
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("✓ Conversation history cleared")
    
    def quit_chat(self):
        """Quit the chat."""
        print("Goodbye!")
        sys.exit(0)
    
    def run(self):
        """Run the CLI chat interface."""
        print("🤖 RAG Chatbot with MCP Tools")
        print("="*40)
        print("Type '/help' for commands or ask any question!")
        print("Type '/quit' or '/exit' to leave")
        print("="*40)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input in self.commands:
                    self.commands[user_input]()
                    continue
                
                if user_input.startswith('/'):
                    print("Unknown command. Type '/help' for available commands.")
                    continue
                
                print("\n🤖 Assistant: ", end="", flush=True)
                
                try:
                    response = self.client.chat_with_tools(user_input, self.conversation_history)
                    print(response)
                    
                    self.conversation_history.append({"role": "user", "content": user_input})
                    self.conversation_history.append({"role": "assistant", "content": response})
                    
                    if len(self.conversation_history) > 20:
                        self.conversation_history = self.conversation_history[-20:]
                
                except Exception as e:
                    print(f"Error: {e}")
            
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except EOFError:
                print("\n\nGoodbye!")
                break


if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY environment variable not set!")
        print("Please create a .env file with your Groq API key:")
        print("GROQ_API_KEY=your_api_key_here")
        sys.exit(1)
    
    chat = CLIChat()
    chat.run()