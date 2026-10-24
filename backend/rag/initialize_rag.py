"""
Initialize the RAG system with sample medical knowledge.

This script:
1. Creates sample medical knowledge documents
2. Chunks the documents
3. Generates embeddings
4. Builds FAISS vector index
5. Tests retrieval and generation

Usage:
    python -m rag.initialize_rag
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag import (
    MedicalKnowledgeIngester,
    VectorStore,
    MedicalRetriever,
    GroundedGenerator
)
from rag.schemas import GenerationContext


def initialize_knowledge_base(index_path: str = "knowledge_index.faiss") -> tuple:
    """Initialize the RAG system with sample knowledge.
    
    Args:
        index_path: Path to save the FAISS index
    
    Returns:
        Tuple of (vector_store, retriever, generator)
    """
    print("="*60)
    print("Initializing MedEasy RAG System")
    print("="*60)
    
    # Step 1: Ingest knowledge
    print("\n[1/5] Ingesting medical knowledge...")
    ingester = MedicalKnowledgeIngester(chunk_size=500, chunk_overlap=50)
    documents, chunks = ingester.ingest_sample_knowledge_base()
    print(f"✓ Ingested {len(documents)} documents")
    print(f"✓ Generated {len(chunks)} chunks")
    
    # Step 2: Initialize vector store
    print("\n[2/5] Initializing vector store...")
    vector_store = VectorStore(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        index_path=index_path
    )
    print(f"✓ Loaded embedding model")
    
    # Step 3: Add chunks to vector store
    print("\n[3/5] Generating embeddings and building index...")
    vector_store.add_chunks(chunks)
    print(f"✓ Added {len(chunks)} chunks to index")
    
    # Step 4: Save index
    print("\n[4/5] Saving index...")
    vector_store.save()
    print(f"✓ Saved index to {index_path}")
    
    # Step 5: Initialize retriever and generator
    print("\n[5/5] Initializing retriever and generator...")
    retriever = MedicalRetriever(vector_store)
    generator = GroundedGenerator()
    print("✓ RAG system ready")
    
    # Print coverage summary
    print("\n" + "="*60)
    print("Knowledge Base Coverage")
    print("="*60)
    coverage = retriever.get_coverage_summary()
    print(f"Total chunks: {coverage['total_chunks']}")
    print(f"Total sources: {coverage['total_sources']}")
    print(f"Covered tests: {', '.join(coverage['covered_tests'][:10])}")
    if len(coverage['covered_tests']) > 10:
        print(f"              ... and {len(coverage['covered_tests']) - 10} more")
    print(f"Source types: {', '.join(coverage['source_types'])}")
    
    return vector_store, retriever, generator


def test_rag_system(retriever: MedicalRetriever, generator: GroundedGenerator):
    """Test the RAG system with sample queries."""
    print("\n" + "="*60)
    print("Testing RAG System")
    print("="*60)
    
    test_queries = [
        {
            "name": "Hemoglobin Test Explanation",
            "test_name": "Hemoglobin",
            "query": "What is the hemoglobin test?",
            "k": 3
        },
        {
            "name": "High Glucose Interpretation",
            "test_name": "Glucose",
            "query": "What does high blood glucose mean?",
            "k": 3
        },
        {
            "name": "CBC Components",
            "test_name": None,
            "query": "What tests are included in a complete blood count?",
            "k": 3
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n[Test {i}] {test['name']}")
        print(f"Query: {test['query']}")
        print("-" * 60)
        
        # Retrieve
        results = retriever.retrieve(
            query=test['query'],
            k=test['k'],
            test_name=test['test_name']
        )
        
        print(f"\nRetrieved {len(results)} passages:")
        for j, result in enumerate(results, 1):
            print(f"\n[{j}] Score: {result.score:.3f}")
            print(f"Source: {result.chunk.source_title}")
            print(f"Text: {result.chunk.text[:150]}...")
        
        # Generate
        context = GenerationContext(
            question=test['query'],
            test_name=test['test_name'],
            retrieved_passages=results,
            language="en"
        )
        
        response = generator.generate(context)
        
        print(f"\nGenerated Response:")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Citations: {response.citations}")
        print(f"Answer: {response.answer}")
        
        if response.limitations:
            print(f"Limitations: {response.limitations}")
        
        print("\n" + "="*60)


def main():
    """Main initialization script."""
    # Check if index already exists
    index_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_index.faiss")
    
    if os.path.exists(index_path):
        print(f"Found existing index at {index_path}")
        choice = input("Reinitialize? (y/N): ").strip().lower()
        if choice != 'y':
            print("Loading existing index...")
            vector_store = VectorStore(index_path=index_path)
            vector_store.load()
            retriever = MedicalRetriever(vector_store)
            generator = GroundedGenerator()
            print("Loaded existing RAG system")
        else:
            # Delete old index
            os.remove(index_path)
            chunks_path = f"{index_path}.chunks.pkl"
            if os.path.exists(chunks_path):
                os.remove(chunks_path)
            vector_store, retriever, generator = initialize_knowledge_base(index_path)
    else:
        vector_store, retriever, generator = initialize_knowledge_base(index_path)
    
    # Run tests
    test_choice = input("\nRun test queries? (Y/n): ").strip().lower()
    if test_choice != 'n':
        test_rag_system(retriever, generator)
    
    print("\n✅ RAG system initialization complete!")
    print(f"Index saved to: {index_path}")
    print("\nYou can now use the RAG system in your application.")


if __name__ == "__main__":
    main()
