#!/usr/bin/env python3

import sys
import os

def test_vector_store():
    """Test VectorStore initialization and basic operations."""
    print("🧪 Testing VectorStore...")
    
    try:
        from vector_store import VectorStore
        print("✓ VectorStore import successful")
        
        # Test initialization
        vs = VectorStore()
        print("✓ VectorStore initialization successful")
        
        # Test adding a short document
        doc_id = vs.add_document("This is a test document", {"title": "Test"})
        print(f"✓ Short document added with ID: {doc_id}")
        
        # Test adding a long document that will be chunked
        long_content = """
        This is a very long document that should be split into multiple chunks. It contains multiple sentences and paragraphs to test the chunking functionality. 
        
        The chunking system should split this content intelligently at sentence boundaries rather than cutting words in half. This ensures that each chunk maintains semantic coherence and readability.
        
        Additionally, the system implements overlap between chunks to preserve context across boundaries. This helps maintain continuity when information spans multiple chunks.
        
        The vector store will create separate embeddings for each chunk while maintaining metadata that links them back to the original document. This approach balances retrieval granularity with context preservation.
        """ * 3  # Make it even longer
        
        long_doc_id = vs.add_document(long_content, {"title": "Long Test Document", "type": "test"})
        print(f"✓ Long document added with ID: {long_doc_id}")
        
        # Test search
        results = vs.search("chunking functionality", n_results=3)
        print(f"✓ Search returned {len(results)} results")
        
        if results:
            print(f"  First result: {results[0]['content'][:100]}...")
            if 'chunk_index' in results[0]['metadata']:
                print(f"  Chunk info: {results[0]['metadata']['chunk_index']}/{results[0]['metadata']['total_chunks']}")
        
        # Test collection info
        info = vs.get_collection_info()
        print(f"✓ Collection info: {info}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vector_store()
    sys.exit(0 if success else 1)