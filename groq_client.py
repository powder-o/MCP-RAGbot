from groq import Groq
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()


class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "deepseek-r1-distill-llama-70b"
    
    def chat_completion(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a chat completion with the Groq API using Deepseek model.
        
        Args:
            messages: List of message dictionaries
            tools: Optional list of tools for function calling
        
        Returns:
            The response from the API
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**kwargs)
            return response
        except Exception as e:
            print(f"Error in chat completion: {e}")
            return None
    
    def generate_response(self, user_message: str, context: str = None) -> str:
        """
        Generate a response to a user message, optionally with context.
        
        Args:
            user_message: The user's message
            context: Optional context from vector search
        
        Returns:
            The generated response
        """
        messages = []
        
        if context:
            system_message = f"""You are a helpful AI assistant with access to a knowledge base. 
Use the following context to answer the user's question accurately and helpfully.

Context:
{context}

If the context doesn't contain relevant information, say so and provide a general response based on your knowledge."""
            messages.append({"role": "system", "content": system_message})
        else:
            messages.append({"role": "system", "content": "You are a helpful AI assistant."})
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.chat_completion(messages)
        
        if response and response.choices:
            return response.choices[0].message.content
        else:
            return "I'm sorry, I couldn't generate a response at this time."