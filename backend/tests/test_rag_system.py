"""
Validation tests for the RAG system.

Tests knowledge ingestion, vector store, retrieval, and generation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rag import (
    MedicalKnowledgeIngester,
    SourceDocument,
    DocumentChunk,
    GenerationContext
)


def test_knowledge_ingestion():
    """Test medical knowledge ingestion."""
    print("\n[TEST] Knowledge Ingestion")
    
    ingester = MedicalKnowledgeIngester(chunk_size=500, chunk_overlap=50)
    
    # Test manual content ingestion
    doc = ingester.ingest_manual_content(
        title="Test Document",
        content="This is a test medical document about hemoglobin. " * 50,  # Make it long enough
        source_url="https://test.com/doc",
        test_names=["Hemoglobin"]
    )
    
    assert isinstance(doc, SourceDocument)
    assert doc.title == "Test Document"
    assert len(doc.full_text) > 0
    assert "Hemoglobin" in doc.test_names
    print("✓ Manual content ingestion passed")
    
    # Test chunking
    chunks = ingester.chunk_document(doc)
    assert len(chunks) > 0
    assert all(isinstance(c, DocumentChunk) for c in chunks)
    assert all(c.source_id == doc.source_id for c in chunks)
    print(f"✓ Document chunking passed ({len(chunks)} chunks created)")
    
    # Test sample knowledge base
    docs, all_chunks = ingester.ingest_sample_knowledge_base()
    assert len(docs) >= 3  # At least 3 sample documents
    assert len(all_chunks) > 0
    assert all(isinstance(d, SourceDocument) for d in docs)
    assert all(isinstance(c, DocumentChunk) for c in all_chunks)
    print(f"✓ Sample knowledge base created ({len(docs)} docs, {len(all_chunks)} chunks)")


def test_document_schemas():
    """Test RAG data schemas."""
    print("\n[TEST] RAG Schemas")
    
    from rag.schemas import SourceType, LicenseType
    
    # Test SourceDocument
    doc = SourceDocument(
        source_id="test_001",
        title="Test Medical Document",
        url="https://example.com/test",
        source_type=SourceType.MANUAL,
        publisher="Test Publisher",
        license=LicenseType.EDUCATIONAL_USE,
        full_text="This is test content about medical topics.",
        test_names=["Hemoglobin", "Glucose"]
    )
    
    assert doc.source_id == "test_001"
    assert doc.credibility_score == 0.5  # Default
    print("✓ SourceDocument schema validation passed")
    
    # Test DocumentChunk
    chunk = DocumentChunk(
        chunk_id="test_001_chunk_0",
        source_id="test_001",
        text="This is a chunk of text.",
        chunk_index=0,
        source_title="Test Document",
        source_url="https://example.com/test",
        source_type=SourceType.MANUAL,
        publisher="Test Publisher",
        test_names=["Hemoglobin"]
    )
    
    assert chunk.chunk_id == "test_001_chunk_0"
    citation = chunk.get_citation()
    assert "Test Document" in citation
    assert "https://example.com/test" in citation
    print("✓ DocumentChunk schema validation passed")
    
    # Test GenerationContext
    context = GenerationContext(
        question="What is hemoglobin?",
        test_name="Hemoglobin",
        retrieved_passages=[],
        language="en"
    )
    
    assert context.question == "What is hemoglobin?"
    assert context.test_name == "Hemoglobin"
    formatted = context.format_for_llm()
    assert "Hemoglobin" in formatted
    print("✓ GenerationContext schema validation passed")


def test_retrieval_components():
    """Test retrieval component initialization."""
    print("\n[TEST] Retrieval Components")
    
    # These tests don't require embeddings, just validate structure
    ingester = MedicalKnowledgeIngester()
    docs, chunks = ingester.ingest_sample_knowledge_base()
    
    # Check chunks have required fields
    for chunk in chunks[:3]:
        assert chunk.text
        assert chunk.source_title
        assert chunk.source_url
        assert chunk.chunk_index >= 0
    print(f"✓ Chunks have required fields")
    
    # Check document attribution
    for doc in docs:
        assert doc.title
        assert doc.url
        assert doc.publisher
        assert doc.license
    print(f"✓ Documents have attribution metadata")


def test_citation_extraction():
    """Test citation extraction from generated text."""
    print("\n[TEST] Citation Extraction")
    
    from rag.generator import GroundedGenerator
    
    generator = GroundedGenerator()
    
    # Test citation extraction
    text_with_citations = "Hemoglobin is a protein [1] that carries oxygen [2]. Normal range is 12-16 g/dL [1]."
    citations = generator._extract_citations(text_with_citations)
    
    assert 1 in citations
    assert 2 in citations
    assert len(citations) == 2
    print(f"✓ Citation extraction passed: {citations}")
    
    # Test text without citations
    text_no_citations = "This is text without any citations."
    citations = generator._extract_citations(text_no_citations)
    assert len(citations) == 0
    print("✓ No false positives in citation extraction")


def main():
    """Run all validation tests."""
    print("="*60)
    print("RAG System Validation")
    print("="*60)
    
    tests = [
        ("Document Schemas", test_document_schemas),
        ("Knowledge Ingestion", test_knowledge_ingestion),
        ("Retrieval Components", test_retrieval_components),
        ("Citation Extraction", test_citation_extraction),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ {name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ {name} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
