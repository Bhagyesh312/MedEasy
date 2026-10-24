#!/usr/bin/env python3
"""
Test suite for Phase 3: Hallucination Verification System
Tests citation validation, numeric validation, and overall verification pipeline
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from verification.schemas import VerificationResult, CitationValidation, NumericValidation
from verification.citation_validator import CitationValidator
from verification.numeric_validator import NumericValidator
from verification.verifier import ResponseVerifier
from rag.schemas import SourceDocument, GeneratedResponse


def test_citation_validator():
    """Test citation extraction and validation"""
    print("\n=== Testing Citation Validator ===")
    
    validator = CitationValidator()
    
    # Test 1: Valid citations
    response = "Your hemoglobin is low [1]. Normal range is 13-17 g/dL [2]."
    sources = [
        SourceDocument(
            doc_id="source_1",
            title="Hemoglobin Guide",
            content="Hemoglobin is a protein in red blood cells.",
            source_type="medlineplus",
            url="https://example.com/hb"
        ),
        SourceDocument(
            doc_id="source_2",
            title="Reference Ranges",
            content="Normal hemoglobin: 13-17 g/dL for men.",
            source_type="medical_knowledge",
            url="https://example.com/ranges"
        )
    ]
    
    result = validator.validate(response, sources)
    print(f"✓ Valid citations: {result.valid_citations} (expected: [1, 2])")
    print(f"  Coverage: {result.coverage_percentage:.1f}%")
    assert result.all_valid, "All citations should be valid"
    assert result.coverage_percentage > 0, "Coverage should be positive"
    
    # Test 2: Invalid citation
    response_invalid = "Your results are abnormal [5]."
    result_invalid = validator.validate(response_invalid, sources)
    print(f"✓ Invalid citations: {result_invalid.invalid_citations} (expected: [5])")
    assert not result_invalid.all_valid, "Should detect invalid citation"
    
    # Test 3: No citations
    response_none = "Your results look normal."
    result_none = validator.validate(response_none, sources)
    print(f"✓ No citations: coverage = {result_none.coverage_percentage:.1f}%")
    assert result_none.all_valid, "No citations should be valid"
    
    return True


def test_numeric_validator():
    """Test numeric value consistency checking"""
    print("\n=== Testing Numeric Validator ===")
    
    validator = NumericValidator()
    
    # Test 1: Consistent values
    response_consistent = "Your hemoglobin is 11.5 g/dL, which is below normal (13-17 g/dL)."
    sources = [
        SourceDocument(
            doc_id="s1",
            title="Lab Report",
            content="Hemoglobin: 11.5 g/dL. Reference range: 13.0-17.0 g/dL.",
            source_type="lab_report",
            url=""
        )
    ]
    
    result = validator.validate(response_consistent, sources)
    print(f"✓ Consistent values: {len(result.consistent_values)} found")
    print(f"  Inconsistencies: {len(result.inconsistent_values)}")
    assert result.all_consistent, "Values should be consistent"
    
    # Test 2: Inconsistent values
    response_inconsistent = "Your hemoglobin is 15.0 g/dL."
    result_inconsistent = validator.validate(response_inconsistent, sources)
    print(f"✓ Inconsistent values: {len(result_inconsistent.inconsistent_values)} found")
    assert not result_inconsistent.all_consistent, "Should detect inconsistency"
    
    # Test 3: No numeric values
    response_no_nums = "Your results indicate anemia."
    result_no_nums = validator.validate(response_no_nums, sources)
    print(f"✓ No numeric values: consistent = {result_no_nums.all_consistent}")
    assert result_no_nums.all_consistent, "No values should be consistent"
    
    return True


def test_response_verifier():
    """Test full verification pipeline"""
    print("\n=== Testing Response Verifier ===")
    
    verifier = ResponseVerifier()
    
    # Test case: Well-grounded response
    generated_response = GeneratedResponse(
        text="Your hemoglobin level is 11.5 g/dL [1], which is below the normal range of 13-17 g/dL for men [2]. This indicates mild anemia.",
        sources=[
            SourceDocument(
                doc_id="source_1",
                title="Lab Report",
                content="Patient hemoglobin: 11.5 g/dL",
                source_type="lab_report",
                url=""
            ),
            SourceDocument(
                doc_id="source_2",
                title="Reference Ranges",
                content="Normal hemoglobin range for adult men: 13.0-17.0 g/dL",
                source_type="medical_knowledge",
                url="https://medlineplus.gov/hemoglobin"
            )
        ],
        metadata={"model": "test", "temperature": 0.0}
    )
    
    result = verifier.verify(generated_response)
    
    print(f"✓ Overall verification status: {result.status.value}")
    print(f"  Confidence score: {result.confidence_score:.2f}")
    print(f"  Citation validation: {result.citation_validation.all_valid}")
    print(f"  Numeric validation: {result.numeric_validation.all_consistent}")
    
    assert result.status.value in ["verified", "warning"], "Should be verified or warning"
    assert result.confidence_score >= 0.7, "Confidence should be high"
    assert result.citation_validation.all_valid, "Citations should be valid"
    assert result.numeric_validation.all_consistent, "Numbers should be consistent"
    
    # Test warning case: No citations
    response_no_citations = GeneratedResponse(
        text="You have anemia. You should eat more iron-rich foods.",
        sources=[SourceDocument(
            doc_id="s1",
            title="Nutrition Guide",
            content="Iron-rich foods include spinach and red meat.",
            source_type="medical_knowledge",
            url=""
        )],
        metadata={}
    )
    
    result_warning = verifier.verify(response_no_citations)
    print(f"\n✓ Warning case: status = {result_warning.status.value}")
    print(f"  Confidence: {result_warning.confidence_score:.2f}")
    assert result_warning.status.value == "warning", "Should be warning without citations"
    
    return True


def test_verification_recommendations():
    """Test verification recommendations generation"""
    print("\n=== Testing Verification Recommendations ===")
    
    verifier = ResponseVerifier()
    
    # Case 1: Invalid citations
    response = GeneratedResponse(
        text="Your test results are concerning [5][6].",
        sources=[
            SourceDocument(doc_id="s1", title="Guide", content="Content", source_type="web", url="")
        ],
        metadata={}
    )
    
    result = verifier.verify(response)
    print(f"✓ Invalid citations case:")
    print(f"  Recommendations: {result.recommendations}")
    assert len(result.recommendations) > 0, "Should have recommendations"
    assert any("citation" in r.lower() for r in result.recommendations), "Should mention citations"
    
    # Case 2: Low confidence
    response_low = GeneratedResponse(
        text="You might have a serious condition.",
        sources=[],
        metadata={}
    )
    
    result_low = verifier.verify(response_low)
    print(f"\n✓ Low confidence case:")
    print(f"  Status: {result_low.status.value}")
    print(f"  Recommendations: {result_low.recommendations}")
    assert result_low.status.value in ["warning", "failed"], "Should warn on low confidence"
    
    return True


def run_all_tests():
    """Run all Phase 3 verification tests"""
    print("=" * 60)
    print("PHASE 3: HALLUCINATION VERIFICATION SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Citation Validator", test_citation_validator),
        ("Numeric Validator", test_numeric_validator),
        ("Response Verifier", test_response_verifier),
        ("Verification Recommendations", test_verification_recommendations),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"\n✅ {test_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name}: FAILED")
            print(f"   Error: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"PHASE 3 TEST RESULTS: {passed}/{len(tests)} passed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ Phase 3 Hallucination Verification: PRODUCTION READY")
    else:
        print(f"\n⚠️  {failed} test(s) failed - review needed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
