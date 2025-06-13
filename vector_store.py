import chromadb
from chromadb.config import Settings
from chromadb.errors import NotFoundError
from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict, Any
import uuid
import re


class VectorStore:
    def __init__(self, collection_name: str = "documents", chunk_size: int = 800, chunk_overlap: int = 100):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except NotFoundError:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks with smart sentence/paragraph boundaries."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                current_chunk += (" " if current_chunk else "") + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    
                    if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                        overlap_text = current_chunk[-self.chunk_overlap:]
                        current_chunk = overlap_text + " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    if len(sentence) > self.chunk_size:
                        words = sentence.split()
                        current_word_chunk = ""
                        for word in words:
                            if len(current_word_chunk) + len(word) + 1 <= self.chunk_size:
                                current_word_chunk += (" " if current_word_chunk else "") + word
                            else:
                                if current_word_chunk:
                                    chunks.append(current_word_chunk.strip())
                                current_word_chunk = word
                        if current_word_chunk:
                            current_chunk = current_word_chunk
                    else:
                        current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        if metadata is None:
            metadata = {}
        
        doc_id = str(uuid.uuid4())
        chunks = self._split_text_into_chunks(content)
        
        documents = []
        embeddings = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'parent_doc_id': doc_id,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'chunk_size': len(chunk)
            })
            
            embedding = self.embedding_model.encode([chunk])[0].tolist()
            
            documents.append(chunk)
            embeddings.append(embedding)
            metadatas.append(chunk_metadata)
            ids.append(chunk_id)
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return doc_id
    
    def search(self, query: str, n_results: int = 5, max_context_chars: int = 4000) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 2  # Get more results to filter by context size
        )
        
        documents = []
        total_chars = 0
        
        for i in range(len(results['documents'][0])):
            content = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            
            if total_chars + len(content) <= max_context_chars:
                documents.append({
                    'content': content,
                    'metadata': metadata,
                    'distance': results['distances'][0][i],
                    'id': results['ids'][0][i]
                })
                total_chars += len(content)
            
            if len(documents) >= n_results:
                break
        
        return documents
    
    def delete_document(self, doc_id: str) -> bool:
        try:
            # Find all chunks for this document
            results = self.collection.get(
                where={"parent_doc_id": doc_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                return True
            else:
                # Try deleting as single document (backward compatibility)
                self.collection.delete(ids=[doc_id])
                return True
        except Exception:
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        total_count = self.collection.count()
        
        # Try to get unique document count
        try:
            all_metadata = self.collection.get()['metadatas']
            unique_docs = set()
            for metadata in all_metadata:
                if 'parent_doc_id' in metadata:
                    unique_docs.add(metadata['parent_doc_id'])
                else:
                    unique_docs.add('legacy_doc')
            
            return {
                'name': self.collection_name,
                'total_chunks': total_count,
                'unique_documents': len(unique_docs),
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap
            }
        except Exception:
            return {
                'name': self.collection_name,
                'total_chunks': total_count,
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap
            }