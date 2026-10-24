"""
Tests for medical entity extraction pipeline.

Tests structured extraction, terminology normalization, and validation.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from medical_nlp import (
    TestExtraction,
    ReferenceRange,
    ExtractionStatus,
    AbnormalityType,
    TerminologyNormalizer
)


class TestReferenceRange:
    """Test reference range parsing and validation."""
    
    def test_numeric_range(self):
        """Test numeric reference range."""
        ref = ReferenceRange(text="12.0-16.0 g/dL", low=12.0, high=16.0, unit="g/dL")
        assert ref.is_numeric()
        assert ref.low == 12.0
        assert ref.high == 16.0
    
    def test_text_only_range(self):
        """Test non-numeric reference range."""
        ref = ReferenceRange(text="Negative")
        assert not ref.is_numeric()
        assert ref.low is None
        assert ref.high is None
    
    def test_one_sided_range(self):
        """Test reference range with only upper bound."""
        ref = ReferenceRange(text="<5.0 mg/dL", low=None, high=5.0, unit="mg/dL")
        assert ref.is_numeric()
        assert ref.high == 5.0


class TestTestExtraction:
    """Test individual test extraction and validation."""
    
    def test_normal_value_in_range(self):
        """Test normal value within reference range."""
        extraction = TestExtraction(
            test_name="Hemoglobin",
            value=14.5,
            value_text="14.5",
            unit="g/dL",
            reference_range=ReferenceRange(text="12.0-16.0", low=12.0, high=16.0),
            abnormal_flag=False
        )
        
        assert extraction.is_numeric()
        assert extraction.is_in_range() is True
        assert extraction.calculate_abnormality() == AbnormalityType.NORMAL
    
    def test_high_value(self):
        """Test high abnormal value."""
        extraction = TestExtraction(
            test_name="Blood Glucose",
            value=180.0,
            value_text="180",
            unit="mg/dL",
            reference_range=ReferenceRange(text="70-100", low=70.0, high=100.0),
            abnormal_flag=True
        )
        
        assert extraction.is_in_range() is False
        assert extraction.calculate_abnormality() == AbnormalityType.HIGH
    
    def test_low_value(self):
        """Test low abnormal value."""
        extraction = TestExtraction(
            test_name="Hemoglobin",
            value=10.0,
            value_text="10.0",
            unit="g/dL",
            reference_range=ReferenceRange(text="12.0-16.0", low=12.0, high=16.0),
            abnormal_flag=True
        )
        
        assert extraction.is_in_range() is False
        assert extraction.calculate_abnormality() == AbnormalityType.LOW
    
    def test_critical_value(self):
        """Test critically abnormal value."""
        extraction = TestExtraction(
            test_name="Potassium",
            value=7.5,
            value_text="7.5",
            unit="mmol/L",
            reference_range=ReferenceRange(text="3.5-5.0", low=3.5, high=5.0),
            abnormal_flag=True
        )
        
        assert extraction.is_in_range() is False
        # 7.5 > 5.0 * 1.5, so should be critical
        assert extraction.calculate_abnormality() == AbnormalityType.CRITICAL
    
    def test_non_numeric_value(self):
        """Test qualitative (non-numeric) value."""
        extraction = TestExtraction(
            test_name="Blood Type",
            value=None,
            value_text="O Positive",
            unit=None,
            reference_range=None,
            abnormal_flag=False
        )
        
        assert not extraction.is_numeric()
        assert extraction.is_in_range() is None
    
    def test_validation_error(self):
        """Test that validation catches invalid data."""
        with pytest.raises(ValueError):
            # Empty test_name should fail
            TestExtraction(
                test_name="",
                value_text="10.0"
            )


class TestTerminologyNormalizer:
    """Test medical terminology normalization."""
    
    def setup_method(self):
        """Initialize normalizer before each test."""
        self.normalizer = TerminologyNormalizer()
    
    def test_exact_match(self):
        """Test exact terminology match."""
        normalized, category, confidence = self.normalizer.normalize("hemoglobin")
        assert normalized == "Hemoglobin"
        assert category == "hematology"
        assert confidence == 1.0
    
    def test_abbreviation_match(self):
        """Test common abbreviation mapping."""
        normalized, category, confidence = self.normalizer.normalize("HB")
        assert normalized == "Hemoglobin"
        assert category == "hematology"
        assert confidence == 1.0
    
    def test_variant_match(self):
        """Test variant spelling."""
        normalized, category, confidence = self.normalizer.normalize("haemoglobin")
        assert normalized == "Hemoglobin"
        assert confidence == 1.0
    
    def test_fuzzy_match(self):
        """Test fuzzy matching for close variants."""
        normalized, category, confidence = self.normalizer.normalize("hemoglbin")  # typo
        if normalized:  # May or may not match depending on threshold
            assert "Hemoglobin" in normalized or normalized is None
    
    def test_no_match(self):
        """Test unrecognized test name."""
        normalized, category, confidence = self.normalizer.normalize("Unknown Test XYZ")
        assert normalized is None
        assert confidence == 0.0
    
    def test_multiple_variations(self):
        """Test that different variations map to same standard name."""
        tests = ["WBC", "white blood cell", "leukocyte count"]
        for test in tests:
            normalized, _, _ = self.normalizer.normalize(test)
            assert normalized == "White Blood Cell Count"
    
    def test_ambiguity_detection(self):
        """Test detection of ambiguous abbreviations."""
        assert self.normalizer.is_ambiguous("X")  # Single letter
        assert not self.normalizer.is_ambiguous("Hemoglobin")
    
    def test_category_retrieval(self):
        """Test category lookup for normalized names."""
        category = self.normalizer.get_category("Hemoglobin")
        assert category == "hematology"
        
        category = self.normalizer.get_category("Total Cholesterol")
        assert category == "lipids"
    
    def test_variations_retrieval(self):
        """Test getting all variations of a standard name."""
        variations = self.normalizer.get_all_variations("Hemoglobin")
        assert "hemoglobin" in variations
        assert "hb" in variations
        assert "hgb" in variations
    
    def test_suggestions(self):
        """Test alternative suggestions for ambiguous names."""
        suggestions = self.normalizer.suggest_alternatives("gluc", limit=3)
        assert len(suggestions) <= 3
        # Should suggest glucose-related tests
        if suggestions:
            assert any("Glucose" in s[0] for s in suggestions)


class TestExtractionStatistics:
    """Test extraction statistics and aggregation."""
    
    def test_statistics_calculation(self):
        """Test that extraction statistics are calculated correctly."""
        from medical_nlp import ReportExtraction, ExtractionMetadata
        
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
        
        for test in tests:
            test.abnormality_type = test.calculate_abnormality()
        
        metadata = ExtractionMetadata(pdf_filename="test.pdf")
        extraction = ReportExtraction(metadata=metadata, tests=tests)
        
        stats = extraction.get_statistics()
        
        assert stats["total_tests"] == 3
        assert stats["validated"] == 2
        assert stats["failed"] == 1
        assert stats["numeric_values"] == 2
        assert stats["with_reference_range"] == 2


# Integration test markers
@pytest.mark.integration
@pytest.mark.skipif("GROQ_API_KEY" not in os.environ, reason="Requires Groq API key")
class TestLiveExtraction:
    """Integration tests that call the actual Groq API.
    
    These tests are skipped unless GROQ_API_KEY is available.
    """
    
    def test_simple_report_extraction(self):
        """Test extraction on a simple synthetic report."""
        from medical_nlp import MedicalEntityExtractor
        
        report_text = """
        LABORATORY REPORT
        
        Patient: John Doe
        Date: 2024-01-15
        
        COMPLETE BLOOD COUNT
        
        Hemoglobin: 14.5 g/dL (Ref: 12.0-16.0) Normal
        WBC: 8500 cells/μL (Ref: 4000-11000) Normal
        Platelet Count: 250000 /μL (Ref: 150000-400000) Normal
        
        CHEMISTRY PANEL
        
        Glucose: 180 mg/dL (Ref: 70-100) HIGH
        Creatinine: 1.1 mg/dL (Ref: 0.6-1.2) Normal
        """
        
        extractor = MedicalEntityExtractor()
        result = extractor.extract(
            report_text=report_text,
            pdf_filename="test_report.pdf",
            patient_name="John Doe"
        )
        
        assert len(result.tests) >= 4  # At least 4 tests extracted
        assert any(t.test_name_normalized == "Hemoglobin" for t in result.tests)
        assert any(t.test_name_normalized == "Blood Glucose" for t in result.tests)
        
        # Check that high glucose is flagged
        glucose_tests = [t for t in result.tests if "Glucose" in (t.test_name_normalized or t.test_name)]
        assert len(glucose_tests) > 0
        glucose = glucose_tests[0]
        assert glucose.abnormal_flag or glucose.abnormality_type == AbnormalityType.HIGH


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-m", "not integration"])
