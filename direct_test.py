#!/usr/bin/env python3
"""
Direct component testing - bypass Flask to isolate issues
"""

import sys
import os

# Add current directory to path
sys.path.append('.')

def test_detector_directly():
    print("Testing DecisionDetector directly...")
    try:
        from services.detector import DecisionDetector
        detector = DecisionDetector()

        message = "We decided to migrate to PostgreSQL because the schema is stable"
        print(f"Testing message: {message}")

        result = detector.detect(message)
        print(f"Result: {result}")

        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_embedder_directly():
    print("\nTesting GeminiEmbedder directly...")
    try:
        from services.embedder import GeminiEmbedder
        embedder = GeminiEmbedder()

        text = "Test decision text"
        print(f"Testing text: {text}")

        embedding = embedder.embed(text)
        print(f"Embedding dimensions: {len(embedding)}")

        query_embedding = embedder.embed_query("Test query")
        print(f"Query embedding dimensions: {len(query_embedding)}")

        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_store_directly():
    print("\nTesting VectorStore directly...")
    try:
        from services.vector_store import VectorStore
        store = VectorStore()

        print(f"Index has {store.index.ntotal} vectors")

        # Test upsert
        test_embedding = [0.1] * 768  # Mock embedding
        test_metadata = {"title": "Test", "owner": "Test User"}

        store.upsert("test_id", test_embedding, test_metadata)
        print("Upsert successful")

        # Test query
        matches = store.query(test_embedding, top_k=1)
        print(f"Query returned {len(matches)} matches")

        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_engine_directly():
    print("\nTesting RAGEngine directly...")
    try:
        from services.rag_engine import RAGEngine
        rag = RAGEngine()

        query = "Why did we switch to PostgreSQL?"
        print(f"Testing query: {query}")

        result = rag.query(query)
        print(f"RAG result keys: {list(result.keys())}")

        return True
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 Direct Component Testing\n")

    results = {}

    results['detector'] = test_detector_directly()
    results['embedder'] = test_embedder_directly()
    results['vector_store'] = test_vector_store_directly()
    results['rag_engine'] = test_rag_engine_directly()

    print("\n" + "="*50)
    print("RESULTS SUMMARY:")
    for component, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {component}: {status}")

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All components working!")
    else:
        print("\n⚠️  Some components failed - check errors above")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
