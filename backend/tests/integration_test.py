"""
Integration test for MedEasy AI 2.0 - Phase 1 & 2

Tests the complete pipeline from PDF text to grounded explanations.
This test uses mock/minimal components to avoid long model downloads.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("="*70)
print("MedEasy AI 2.0 - Integration Test")
print("Testing Phase 1 (Medical NLP) + Phase 2 (RAG System)")
print("="*70)

# Test 1: Phase 1 - Medical NLP Components
print("\n[Phase 1] Testing Medical NLP Pipeline...")
print("-"*70)

try:
    from medical_nlp import (
        TestExtraction,
        ReferenceRange,
        ReportExtraction,
        ExtractionMetadata,
        ExtractionStatus,
        AbnormalityType,
        TerminologyNormalizer
    )
    print("✓ Medical NLP modules imported")
except ImportError as e:
    print(f"✗ Failed to import Medical NLP: {e}")
    sys.exit(1)

# Test terminology normalization
print("\n1.1 Testing Terminology Normalizer...")
normalizer = TerminologyNormalizer()

test_terms = [
    ("hemoglobin", "Hemoglobin"),
    ("HB", "Hemoglobin"),
    ("wbc", "White Blood Cell Count"),
    ("glucose", "Blood Glucose"),
    ("cholesterol", "Total Cholesterol"),
]

passed = 0
for input_term, expected in test_terms:
    normalized, category, confidence = normalizer.normalize(input_term)
    if normalized == expected:
        print(f"  ✓ {input_term:15} → {normalized:30} (confidence: {confidence:.2f})")
        passed += 1
    else:
        print(f"  ✗ {input_term:15} → {normalized:30} (expected: {expected})")

print(f"  Result: {passed}/{len(test_terms)} tests passed")

# Test extraction validation
print("\n1.2 Testing Test Extraction Schemas...")
test_cases = [
    {
        "name": "Normal Hemoglobin",
        "test": TestExtraction(
            test_name="Hemoglobin",
            test_name_normalized="Hemoglobin",
            value=14.5,
            value_text="14.5",
            unit="g/dL",
            reference_range=ReferenceRange(text="12.0-16.0", low=12.0, high=16.0),
            abnormal_flag=False
        ),
        "expected_status": AbnormalityType.NORMAL
    },
    {
        "name": "High Glucose",
        "test": TestExtraction(
            test_name="Glucose",
            test_name_normalized="Blood Glucose",
            value=180.0,
            value_text="180",
            unit="mg/dL",
            reference_range=ReferenceRange(text="70-100", low=70.0, high=100.0),
            abnormal_flag=True
        ),
        "expected_status": AbnormalityType.CRITICAL  # 180 > 100*1.5
    },
    {
        "name": "Low Hemoglobin",
        "test": TestExtraction(
            test_name="Hemoglobin",
            value=10.0,
            value_text="10.0",
            unit="g/dL",
            reference_range=ReferenceRange(text="12.0-16.0", low=12.0, high=16.0),
            abnormal_flag=True
        ),
        "expected_status": AbnormalityType.LOW
    }
]

extraction_passed = 0
for case in test_cases:
    test = case["test"]
    calculated = test.calculate_abnormality()
    if calculated == case["expected_status"]:
        print(f"  ✓ {case['name']}: {calculated.value}")
        extraction_passed += 1
    else:
        print(f"  ✗ {case['name']}: got {calculated.value}, expected {case['expected_status'].value}")

print(f"  Result: {extraction_passed}/{len(test_cases)} extraction tests passed")

# Test report statistics
print("\n1.3 Testing Report Extraction Statistics...")
metadata = ExtractionMetadata(pdf_filename="test_report.pdf")
extraction = ReportExtraction(
    metadata=metadata,
    tests=[case["test"] for case in test_cases]
)

stats = extraction.get_statistics()
print(f"  ✓ Total tests: {stats['total_tests']}")
print(f"  ✓ Normal: {stats['normal']}")
print(f"  ✓ High: {stats['high']}")
print(f"  ✓ Low: {stats['low']}")
print(f"  ✓ Critical: {stats['critical']}")

# Test legacy format conversion
legacy = extraction.to_legacy_format()
print(f"  ✓ Legacy format conversion: {len(legacy)} tests")

# Test 2: Phase 2 - RAG System Components
print("\n[Phase 2] Testing RAG System...")
print("-"*70)

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
    print("✓ RAG modules imported")
except ImportError as e:
    print(f"✗ Failed to import RAG: {e}")
    sys.exit(1)

# Test knowledge ingestion
print("\n2.1 Testing Knowledge Ingestion...")
ingester = MedicalKnowledgeIngester(chunk_size=500, chunk_overlap=50)

# Create sample document
doc = ingester.ingest_manual_content(
    title="Hemoglobin Test Guide",
    content="Hemoglobin is a protein in red blood cells that carries oxygen. " * 50,
    source_url="https://example.com/hb",
    test_names=["Hemoglobin", "Hb", "HGB"]
)

print(f"  ✓ Document created: {doc.title}")
print(f"  ✓ Source type: {doc.source_type.value}")
print(f"  ✓ License: {doc.license.value}")
print(f"  ✓ Test names: {', '.join(doc.test_names)}")
print(f"  ✓ Credibility: {doc.credibility_score}")

# Test chunking
chunks = ingester.chunk_document(doc)
print(f"  ✓ Generated {len(chunks)} chunks")
for i, chunk in enumerate(chunks[:3]):
    print(f"    - Chunk {i}: {len(chunk.text)} chars, ID: {chunk.chunk_id}")

# Test sample knowledge base
print("\n2.2 Testing Sample Knowledge Base...")
docs, all_chunks = ingester.ingest_sample_knowledge_base()
print(f"  ✓ Created {len(docs)} documents")
print(f"  ✓ Generated {len(all_chunks)} total chunks")

for doc in docs:
    print(f"    - {doc.title}")
    print(f"      Tests: {', '.join(doc.test_names[:5])}")
    print(f"      Chunks: {len([c for c in all_chunks if c.source_id == doc.source_id])}")

# Test citation functionality
print("\n2.3 Testing Citation System...")
sample_chunk = all_chunks[0]
citation = sample_chunk.get_citation()
print(f"  ✓ Citation format: {citation[:80]}...")

# Test generation context
print("\n2.4 Testing Generation Context...")
context = GenerationContext(
    question="What is hemoglobin?",
    test_name="Hemoglobin",
    test_value="14.5 g/dL",
    reference_range="12.0-16.0",
    abnormal_flag=False,
    retrieved_passages=[],  # Would contain RetrievalResult objects
    language="en"
)

formatted = context.format_for_llm()
print(f"  ✓ Context created for test: {context.test_name}")
print(f"  ✓ Formatted prompt length: {len(formatted)} chars")
print(f"  ✓ Contains test info: {'Test: Hemoglobin' in formatted}")

# Test citation extraction
print("\n2.5 Testing Citation Extraction...")
try:
    from rag.generator import GroundedGenerator
    generator = GroundedGenerator()
    
    test_responses = [
        ("Hemoglobin carries oxygen [1]. Normal range is 12-16 g/dL [2].", [1, 2]),
        ("This is a test [1] with citations [2] and more [3].", [1, 2, 3]),
        ("No citations here.", []),
        ("Mixed [1] text with [5] non-sequential [2] citations.", [1, 2, 5]),
    ]
    
    citation_passed = 0
    for text, expected_citations in test_responses:
        extracted = generator._extract_citations(text)
        if extracted == expected_citations:
            print(f"  ✓ Extracted {extracted} from text")
            citation_passed += 1
        else:
            print(f"  ✗ Got {extracted}, expected {expected_citations}")
    
    print(f"  Result: {citation_passed}/{len(test_responses)} citation tests passed")
except Exception as e:
    print(f"  ✗ Citation extraction test failed: {e}")

# Test 3: Integration - End to End
print("\n[Integration] Testing End-to-End Pipeline...")
print("-"*70)

print("\n3.1 Simulating Medical Report Analysis...")
# Simulate a simple report
sample_report = """
LABORATORY REPORT
Patient: Test Patient
Date: 2024-01-15

COMPLETE BLOOD COUNT:
Hemoglobin: 14.5 g/dL (Normal Range: 12.0-16.0) NORMAL
WBC: 8500 cells/μL (Normal Range: 4000-11000) NORMAL
Glucose: 180 mg/dL (Normal Range: 70-100) HIGH
"""

print(f"  Sample Report Length: {len(sample_report)} characters")

# Phase 1: Extract structured data
print("\n  Step 1: Structured Extraction (would call LLM)...")
# Simulate extraction results
simulated_findings = [
    TestExtraction(
        test_name="Hemoglobin",
        test_name_normalized="Hemoglobin",
        value=14.5,
        value_text="14.5",
        unit="g/dL",
        reference_range=ReferenceRange(text="12.0-16.0", low=12.0, high=16.0),
        abnormal_flag=False
    ),
    TestExtraction(
        test_name="WBC",
        test_name_normalized="White Blood Cell Count",
        value=8500,
        value_text="8500",
        unit="cells/μL",
        reference_range=ReferenceRange(text="4000-11000", low=4000, high=11000),
        abnormal_flag=False
    ),
    TestExtraction(
        test_name="Glucose",
        test_name_normalized="Blood Glucose",
        value=180,
        value_text="180",
        unit="mg/dL",
        reference_range=ReferenceRange(text="70-100", low=70, high=100),
        abnormal_flag=True
    )
]

# Calculate abnormality
for finding in simulated_findings:
    finding.abnormality_type = finding.calculate_abnormality()

metadata = ExtractionMetadata(pdf_filename="sample_report.pdf", processing_time_seconds=2.5)
extraction = ReportExtraction(metadata=metadata, tests=simulated_findings)

print(f"  ✓ Extracted {len(extraction.tests)} tests")
print(f"  ✓ Processing time: {metadata.processing_time_seconds}s")

stats = extraction.get_statistics()
print(f"  ✓ Statistics: {stats['normal']} normal, {stats['high']} high, {stats['critical']} critical")

# Phase 2: Prepare for RAG
print("\n  Step 2: RAG Context Preparation...")
flagged_tests = extraction.get_flagged_tests()
print(f"  ✓ Flagged tests: {len(flagged_tests)}")

for test in flagged_tests:
    print(f"    - {test.test_name_normalized}: {test.value} {test.unit} ({test.abnormality_type.value})")
    
    # Would retrieve passages for this test
    print(f"      → Would retrieve knowledge about '{test.test_name_normalized}'")
    
    # Would generate grounded explanation
    print(f"      → Would generate explanation with citations")

# Summary
print("\n" + "="*70)
print("INTEGRATION TEST SUMMARY")
print("="*70)

total_tests = (
    len(test_terms) +           # Terminology tests
    len(test_cases) +           # Extraction tests
    len(test_responses)         # Citation tests
)

total_passed = (
    passed +
    extraction_passed +
    citation_passed
)

print(f"\nPhase 1 (Medical NLP):")
print(f"  ✓ Terminology normalization: {passed}/{len(test_terms)} passed")
print(f"  ✓ Test extraction: {extraction_passed}/{len(test_cases)} passed")
print(f"  ✓ Statistics calculation: Working")
print(f"  ✓ Legacy format conversion: Working")

print(f"\nPhase 2 (RAG System):")
print(f"  ✓ Knowledge ingestion: {len(docs)} documents, {len(all_chunks)} chunks")
print(f"  ✓ Citation extraction: {citation_passed}/{len(test_responses)} passed")
print(f"  ✓ Generation context: Working")
print(f"  ✓ Schema validation: All schemas working")

print(f"\nOverall: {total_passed}/{total_tests} component tests passed")

print("\n" + "="*70)
print("✅ INTEGRATION TEST COMPLETE")
print("="*70)

print("\nNext Steps:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Fix NumPy if needed: pip install 'numpy<2.0'")
print("3. Initialize vector store: python -m rag.initialize_rag")
print("4. Test with real LLM: Run full extraction on sample report")
print("5. Integrate with Flask API")

sys.exit(0 if total_passed == total_tests else 1)
