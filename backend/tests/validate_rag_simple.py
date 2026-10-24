"""
Simple RAG validation without model downloads.
Tests schemas and logic only.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("Testing RAG System Components (no model downloads)...")

# Test 1: Import all RAG modules
print("\n[1] Testing imports...")
try:
    from rag import (
        SourceDocument,
        DocumentChunk,
        RetrievalResult,
        GenerationContext,
        GeneratedResponse,
        SourceType,
        LicenseType,
        MedicalKnowledgeIngester
    )
    print("✓ All RAG modules imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Create sample document
print("\n[2] Testing document creation...")
doc = SourceDocument(
    source_id="test_001",
    title="Hemoglobin Test Information",
    url="https://example.com/hb",
    source_type=SourceType.MANUAL,
    publisher="Test Publisher",
    license=LicenseType.EDUCATIONAL_USE,
    full_text="Hemoglobin is a protein in red blood cells. " * 20,
    test_names=["Hemoglobin", "Hb"]
)
print(f"✓ Created document: {doc.title}")
print(f"  - Source ID: {doc.source_id}")
print(f"  - Test names: {', '.join(doc.test_names)}")

# Test 3: Create chunks
print("\n[3] Testing document chunking...")
ingester = MedicalKnowledgeIngester(chunk_size=100, chunk_overlap=20)
chunks = ingester.chunk_document(doc)
print(f"✓ Created {len(chunks)} chunks")
for i, chunk in enumerate(chunks[:3]):
    print(f"  - Chunk {i}: {len(chunk.text)} chars")

# Test 4: Test sample knowledge base
print("\n[4] Testing sample knowledge base...")
docs, all_chunks = ingester.ingest_sample_knowledge_base()
print(f"✓ Sample KB: {len(docs)} documents, {len(all_chunks)} chunks")
for doc in docs:
    print(f"  - {doc.title}")
    print(f"    Tests: {', '.join(doc.test_names[:5])}")

# Test 5: Test chunk schema
print("\n[5] Testing chunk metadata...")
sample_chunk = all_chunks[0]
print(f"✓ Chunk ID: {sample_chunk.chunk_id}")
print(f"  - Source: {sample_chunk.source_title}")
print(f"  - Publisher: {sample_chunk.publisher}")
print(f"  - License: {sample_chunk.license.value}")
print(f"  - Credibility: {sample_chunk.credibility_score}")
citation = sample_chunk.get_citation()
print(f"  - Citation: {citation[:60]}...")

# Test 6: Test generation context
print("\n[6] Testing generation context...")
context = GenerationContext(
    question="What is hemoglobin?",
    test_name="Hemoglobin",
    test_value="13.5",
    reference_range="12.0-16.0",
    abnormal_flag=False,
    retrieved_passages=[],
    language="en"
)
formatted = context.format_for_llm()
print("✓ Generation context created")
print(f"  - Question: {context.question}")
print(f"  - Test: {context.test_name}")
print(f"  - Formatted length: {len(formatted)} chars")

# Test 7: Test citation extraction (without LLM)
print("\n[7] Testing citation extraction...")
from rag.generator import GroundedGenerator
generator = GroundedGenerator()
test_text = "Hemoglobin carries oxygen [1]. Normal range is 12-16 g/dL [2]. It is measured in a CBC [1]."
citations = generator._extract_citations(test_text)
print(f"✓ Found citations: {citations}")
assert 1 in citations and 2 in citations

print("\n" + "="*60)
print("✅ All RAG component tests passed!")
print("="*60)
print("\nNote: Full RAG system test (with embeddings) requires:")
print("  - sentence-transformers model download (~80MB)")
print("  - faiss-cpu library")
print("  - Run: python -m rag.initialize_rag")
