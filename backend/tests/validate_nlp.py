"""
Standalone validation script for Medical NLP pipeline.
Doesn't require pytest - can run directly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from medical_nlp import (
    TestExtraction,
    ReferenceRange,
    ExtractionStatus,
    AbnormalityType,
    TerminologyNormalizer,
    ReportExtraction,
    ExtractionMetadata
)

def test_reference_range():
    """Test reference range functionality."""
    print("\n[TEST] Reference Range Validation")
    
    # Test numeric range
    ref = ReferenceRange(text="12.0-16.0 g/dL", low=12.0, high=16.0, unit="g/dL")
    assert ref.is_numeric(), "Numeric range should return True"
    assert ref.low == 12.0, "Lower bound mismatch"
    assert ref.high == 16.0, "Upper bound mismatch"
    print("✓ Numeric range validation passed")
    
    # Test text-only range
    ref2 = ReferenceRange(text="Negative")
    assert not ref2.is_numeric(), "Text-only range should return False"
    print("✓ Text-only range validation passed")


def test_test_extraction():
    """Test individual test extraction."""
    print("\n[TEST] Test Extraction Validation")
    
    # Test normal value
    extraction = TestExtraction(
        test_name="Hemoglobin",
        value=14.5,
        value_text="14.5",
        unit="g/dL",
        reference_range=ReferenceRange(text="12.0-16.0", low=12.0, high=16.0),
        abnormal_flag=False
    )
    
    assert extraction.is_numeric(), "Should be numeric"
    assert extraction.is_in_range() is True, "Should be in range"
    assert extraction.calculate_abnormality() == AbnormalityType.NORMAL, "Should be normal"
    print("✓ Normal value extraction passed")
    
    # Test high value
    extraction2 = TestExtraction(
        test_name="Glucose",
        value=180.0,
        value_text="180",
        unit="mg/dL",
        reference_range=ReferenceRange(text="70-100", low=70.0, high=100.0),
        abnormal_flag=True
    )
    
    assert extraction2.is_in_range() is False, "Should be out of range"
    abnormality = extraction2.calculate_abnormality()
    # 180 is 1.8x upper limit, so >= 1.5x means CRITICAL
    assert abnormality in [AbnormalityType.HIGH, AbnormalityType.CRITICAL], f"Should be HIGH or CRITICAL, got {abnormality}"
    print(f"✓ High value extraction passed (detected as {abnormality.value})")
    
    # Test low value
    extraction3 = TestExtraction(
        test_name="Hemoglobin",
        value=10.0,
        value_text="10.0",
        unit="g/dL",
        reference_range=ReferenceRange(text="12.0-16.0", low=12.0, high=16.0),
        abnormal_flag=True
    )
    
    assert extraction3.calculate_abnormality() == AbnormalityType.LOW, "Should be low"
    print("✓ Low value extraction passed")


def test_terminology_normalizer():
    """Test medical terminology normalization."""
    print("\n[TEST] Terminology Normalization")
    
    normalizer = TerminologyNormalizer()
    
    # Test exact match
    normalized, category, confidence = normalizer.normalize("hemoglobin")
    assert normalized == "Hemoglobin", f"Expected Hemoglobin, got {normalized}"
    assert category == "hematology", f"Expected hematology, got {category}"
    assert confidence == 1.0, f"Expected confidence 1.0, got {confidence}"
    print("✓ Exact match normalization passed")
    
    # Test abbreviation
    normalized2, _, _ = normalizer.normalize("HB")
    assert normalized2 == "Hemoglobin", f"Expected Hemoglobin, got {normalized2}"
    print("✓ Abbreviation normalization passed")
    
    # Test variant spelling
    normalized3, _, _ = normalizer.normalize("haemoglobin")
    assert normalized3 == "Hemoglobin", f"Expected Hemoglobin, got {normalized3}"
    print("✓ Variant spelling normalization passed")
    
    # Test multiple variations map to same standard
    tests = ["WBC", "white blood cell", "leukocyte count"]
    for test in tests:
        norm, _, _ = normalizer.normalize(test)
        assert norm == "White Blood Cell Count", f"Expected WBC normalization, got {norm} for {test}"
    print("✓ Multiple variations normalization passed")
    
    # Test category retrieval
    cat = normalizer.get_category("Hemoglobin")
    assert cat == "hematology", f"Expected hematology category, got {cat}"
    print("✓ Category retrieval passed")


def test_extraction_statistics():
    """Test extraction statistics calculation."""
    print("\n[TEST] Extraction Statistics")
    
    tests = [
        TestExtraction(
            test_name="Hemoglobin",
            value=14.5,
            value_text="14.5",
            reference_range=ReferenceRange(text="12-16", low=12.0, high=16.0),
            abnormal_flag=False,
            extraction_status=ExtractionStatus.VALIDATED
        ),
        TestExtraction(
            test_name="Glucose",
            value=180.0,
            value_text="180",
            reference_range=ReferenceRange(text="70-100", low=70.0, high=100.0),
            abnormal_flag=True,
            extraction_status=ExtractionStatus.VALIDATED
        ),
        TestExtraction(
            test_name="Unknown Test",
            value=None,
            value_text="N/A",
            extraction_status=ExtractionStatus.FAILED
        ),
    ]
    
    # Calculate abnormality types
    for test in tests:
        test.abnormality_type = test.calculate_abnormality()
    
    metadata = ExtractionMetadata(pdf_filename="test.pdf")
    extraction = ReportExtraction(metadata=metadata, tests=tests)
    
    stats = extraction.get_statistics()
    
    assert stats["total_tests"] == 3, f"Expected 3 tests, got {stats['total_tests']}"
    assert stats["validated"] == 2, f"Expected 2 validated, got {stats['validated']}"
    assert stats["failed"] == 1, f"Expected 1 failed, got {stats['failed']}"
    assert stats["numeric_values"] == 2, f"Expected 2 numeric, got {stats['numeric_values']}"
    
    print("✓ Statistics calculation passed")
    print(f"  Total: {stats['total_tests']}, Normal: {stats['normal']}, High: {stats['high']}, Low: {stats['low']}")


def test_legacy_format_conversion():
    """Test conversion to legacy format."""
    print("\n[TEST] Legacy Format Conversion")
    
    tests = [
        TestExtraction(
            test_name="Hemoglobin",
            test_name_normalized="Hemoglobin",
            value=14.5,
            value_text="14.5",
            reference_range=ReferenceRange(text="12-16"),
            abnormal_flag=False
        )
    ]
    
    tests[0].abnormality_type = tests[0].calculate_abnormality()
    
    metadata = ExtractionMetadata(pdf_filename="test.pdf")
    extraction = ReportExtraction(metadata=metadata, tests=tests)
    
    legacy = extraction.to_legacy_format()
    
    assert len(legacy) == 1, f"Expected 1 test, got {len(legacy)}"
    assert legacy[0]["test"] == "Hemoglobin", "Test name mismatch"
    assert legacy[0]["value"] == "14.5", "Value mismatch"
    assert legacy[0]["flag"] is False, "Flag should be False"
    
    print("✓ Legacy format conversion passed")


def main():
    """Run all validation tests."""
    print("="*60)
    print("Medical NLP Pipeline Validation")
    print("="*60)
    
    tests = [
        ("Reference Range", test_reference_range),
        ("Test Extraction", test_test_extraction),
        ("Terminology Normalizer", test_terminology_normalizer),
        ("Extraction Statistics", test_extraction_statistics),
        ("Legacy Format", test_legacy_format_conversion),
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
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
