"""
Medical Entity Extractor using structured LLM outputs.

Combines deterministic rules with Groq LLM's JSON mode for reliable
extraction of laboratory test results from medical reports.
"""

import json
import re
from typing import List, Optional, Tuple
from datetime import datetime
import time

from groq import Groq
import os
from dotenv import load_dotenv

from .schemas import (
    TestExtraction, 
    ReportExtraction, 
    ExtractionMetadata,
    ReferenceRange,
    ExtractionStatus,
    AbnormalityType
)
from .terminology import TerminologyNormalizer

load_dotenv()


class MedicalEntityExtractor:
    """Extracts structured medical entities from laboratory reports.
    
    Uses Groq's JSON mode for reliable structured output combined with
    post-processing validation and terminology normalization.
    """
    
    MODELS = [
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
        "allam-2-7b",
    ]
    
    EXTRACTION_PROMPT = """You are a medical data extraction specialist. Extract ALL laboratory test results from the medical report below.

For EACH test, extract:
- test_name: The exact test name as written in the report
- value_text: The exact result value as written (e.g., "13.5", "<5", "Positive", "Negative")
- value_numeric: The numeric value if the result is a number, otherwise null
- unit: The unit of measurement (e.g., "g/dL", "mg/dL", "%", "cells/μL"), or null if none
- reference_range_text: The reference range as written (e.g., "12.0-16.0", "Negative", "<5.0")
- reference_low: Lower bound of reference range if numeric, otherwise null
- reference_high: Upper bound of reference range if numeric, otherwise null
- abnormal_flag: true if marked as abnormal/high/low in the report, false if normal, null if unclear
- specimen_type: Type of specimen if mentioned (e.g., "Blood", "Serum", "Urine"), otherwise null
- source_page: Page number where this test appears (default to 1 if single page)

IMPORTANT RULES:
1. Extract EVERY test you can find - do not skip any
2. Copy values EXACTLY as written - do not convert units or modify values
3. If value contains operators like "<", ">", ">=", include them in value_text
4. For qualitative results (Positive/Negative/Present/Absent), leave value_numeric as null
5. If reference range is gender-specific, extract the appropriate range
6. Do NOT invent values - use null for missing data
7. Preserve decimal points exactly as shown
8. If multiple tests have same name but different panels, include panel context

Return a JSON object with single key "tests" containing array of test objects.

Report:
{report_text}

Respond with valid JSON only. No other text."""

    def __init__(self, api_key: Optional[str] = None, normalize_terms: bool = True):
        """Initialize the extractor.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            normalize_terms: Whether to normalize test terminology
        """
        self.client = Groq(
            api_key=api_key or os.getenv("GROQ_API_KEY"),
            max_retries=0
        )
        self.normalizer = TerminologyNormalizer() if normalize_terms else None
    
    def extract(
        self, 
        report_text: str, 
        pdf_filename: str,
        patient_name: Optional[str] = None,
        is_scanned: bool = False,
        page_count: int = 1
    ) -> ReportExtraction:
        """Extract structured test results from a medical report.
        
        Args:
            report_text: Raw text extracted from the PDF
            pdf_filename: Name of the source PDF file
            patient_name: Patient name if available
            is_scanned: Whether the PDF was scanned
            page_count: Number of pages in the report
        
        Returns:
            ReportExtraction object with structured test data
        """
        start_time = time.time()
        
        # Truncate very long reports for LLM processing
        truncated_text = report_text[:12000] if len(report_text) > 12000 else report_text
        
        try:
            # Call LLM for structured extraction
            raw_tests = self._call_llm_extraction(truncated_text)
            
            # Validate and enrich each extraction
            validated_tests = []
            for raw_test in raw_tests:
                try:
                    test = self._validate_and_enrich(raw_test)
                    validated_tests.append(test)
                except Exception as e:
                    # Log validation error but continue with other tests
                    print(f"[extractor] Validation error for test {raw_test.get('test_name', 'unknown')}: {e}")
                    # Create a failed extraction record
                    validated_tests.append(self._create_failed_extraction(raw_test, str(e)))
            
            processing_time = time.time() - start_time
            
            # Create metadata
            metadata = ExtractionMetadata(
                pdf_filename=pdf_filename,
                patient_name=patient_name,
                is_scanned=is_scanned,
                page_count=page_count,
                extraction_method="ocr" if is_scanned else "text",
                processing_time_seconds=round(processing_time, 2),
                error_count=len([t for t in validated_tests if t.extraction_status == ExtractionStatus.FAILED]),
                warning_count=len([t for t in validated_tests if t.extraction_status == ExtractionStatus.AMBIGUOUS])
            )
            
            return ReportExtraction(
                metadata=metadata,
                tests=validated_tests,
                raw_text=report_text
            )
            
        except Exception as e:
            # Catastrophic failure - return empty extraction with error
            print(f"[extractor] Critical extraction error: {e}")
            metadata = ExtractionMetadata(
                pdf_filename=pdf_filename,
                patient_name=patient_name,
                is_scanned=is_scanned,
                page_count=page_count,
                extraction_method="failed",
                processing_time_seconds=round(time.time() - start_time, 2),
                error_count=1
            )
            return ReportExtraction(
                metadata=metadata,
                tests=[],
                raw_text=report_text
            )
    
    def _call_llm_extraction(self, report_text: str) -> List[dict]:
        """Call Groq LLM with JSON mode for structured extraction."""
        prompt = self.EXTRACTION_PROMPT.format(report_text=report_text)
        
        last_error = None
        for model in self.MODELS:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a medical data extraction specialist. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # Low temperature for deterministic extraction
                    max_tokens=8000,
                    response_format={"type": "json_object"}  # Force JSON output
                )
                
                content = response.choices[0].message.content
                parsed = json.loads(content)
                
                # Handle different response formats
                if isinstance(parsed, dict):
                    if "tests" in parsed:
                        tests = parsed["tests"]
                    else:
                        # Try to find array in response
                        for value in parsed.values():
                            if isinstance(value, list):
                                tests = value
                                break
                        else:
                            tests = []
                elif isinstance(parsed, list):
                    tests = parsed
                else:
                    tests = []
                
                if not isinstance(tests, list):
                    print(f"[extractor] Unexpected response format from {model}")
                    continue
                
                return tests
                
            except json.JSONDecodeError as e:
                print(f"[extractor] JSON decode error with {model}: {e}")
                last_error = e
                continue
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "rate_limit" in err_str.lower():
                    print(f"[extractor] Rate limit on {model}, trying next...")
                    last_error = e
                    continue
                elif "503" in err_str or "unavailable" in err_str.lower():
                    print(f"[extractor] Model {model} unavailable, trying next...")
                    last_error = e
                    continue
                else:
                    print(f"[extractor] Unexpected error with {model}: {e}")
                    last_error = e
                    raise
        
        # All models failed
        raise Exception(f"All extraction models failed. Last error: {last_error}")
    
    def _validate_and_enrich(self, raw_test: dict) -> TestExtraction:
        """Validate and enrich a single test extraction."""
        
        # Parse reference range
        ref_range = None
        ref_text = raw_test.get("reference_range_text")
        if ref_text and ref_text.strip() and ref_text.strip() not in ["", "N/A", "-", "null"]:
            ref_range = ReferenceRange(
                text=ref_text.strip(),
                low=raw_test.get("reference_low"),
                high=raw_test.get("reference_high"),
                unit=raw_test.get("unit")  # May be None
            )
        
        # Determine extraction status
        status = ExtractionStatus.VALIDATED
        notes = None
        confidence = 1.0
        
        # Check for ambiguous extractions
        test_name = raw_test.get("test_name", "").strip()
        if not test_name:
            status = ExtractionStatus.FAILED
            notes = "Missing test name"
            confidence = 0.0
        elif self.normalizer and self.normalizer.is_ambiguous(test_name):
            status = ExtractionStatus.AMBIGUOUS
            notes = "Test name may be ambiguous"
            confidence = 0.7
        
        # Normalize terminology if available
        normalized_name = None
        if self.normalizer and test_name:
            norm_name, category, norm_confidence = self.normalizer.normalize(test_name)
            if norm_name:
                normalized_name = norm_name
                confidence = min(confidence, norm_confidence)
            elif status == ExtractionStatus.VALIDATED:
                status = ExtractionStatus.AMBIGUOUS
                notes = "Could not normalize test name"
                confidence = 0.6
        
        # Parse value
        value_text = raw_test.get("value_text", "").strip()
        value_numeric = raw_test.get("value_numeric")
        
        # Try to extract numeric value if not provided
        if value_numeric is None and value_text:
            value_numeric = self._extract_numeric_value(value_text)
        
        # Determine abnormality
        abnormal_flag = raw_test.get("abnormal_flag")
        abnormality_type = AbnormalityType.UNKNOWN
        
        # Create the extraction
        extraction = TestExtraction(
            test_name=test_name,
            test_name_normalized=normalized_name,
            value=value_numeric,
            value_text=value_text or "N/A",
            unit=raw_test.get("unit"),
            reference_range=ref_range,
            abnormal_flag=abnormal_flag,
            specimen_type=raw_test.get("specimen_type"),
            source_page=raw_test.get("source_page", 1),
            extraction_confidence=confidence,
            extraction_status=status,
            extraction_notes=notes
        )
        
        # Calculate abnormality type
        extraction.abnormality_type = extraction.calculate_abnormality()
        
        return extraction
    
    def _extract_numeric_value(self, value_text: str) -> Optional[float]:
        """Extract numeric value from text, handling common formats."""
        if not value_text:
            return None
        
        # Remove common non-numeric prefixes/suffixes
        cleaned = value_text.strip()
        cleaned = re.sub(r'^[<>≤≥±~]', '', cleaned)  # Remove operators
        cleaned = re.sub(r'[^\d.,\-]', '', cleaned)  # Keep only digits, decimals, minus
        
        # Handle comma as decimal separator (European format)
        if ',' in cleaned and '.' not in cleaned:
            cleaned = cleaned.replace(',', '.')
        
        # Try to parse as float
        try:
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _create_failed_extraction(self, raw_test: dict, error_msg: str) -> TestExtraction:
        """Create a failed extraction record for logging purposes."""
        return TestExtraction(
            test_name=raw_test.get("test_name", "Unknown"),
            test_name_normalized=None,
            value=None,
            value_text=raw_test.get("value_text", "N/A"),
            unit=raw_test.get("unit"),
            reference_range=None,
            abnormal_flag=None,
            extraction_confidence=0.0,
            extraction_status=ExtractionStatus.FAILED,
            extraction_notes=f"Validation failed: {error_msg}"
        )
    
    def extract_from_legacy_findings(self, findings: List[dict]) -> List[TestExtraction]:
        """Convert legacy findings format to TestExtraction objects.
        
        Used for backward compatibility with existing database records.
        """
        extractions = []
        for finding in findings:
            # Parse reference range
            ref_text = finding.get("reference_range", "")
            ref_range = None
            if ref_text and ref_text != "Not specified":
                ref_range = ReferenceRange(text=ref_text)
            
            # Parse value
            value_text = finding.get("value", "N/A")
            value_numeric = self._extract_numeric_value(value_text)
            
            # Determine abnormality type
            status_str = finding.get("status", "Unknown").lower()
            abnormality_map = {
                "normal": AbnormalityType.NORMAL,
                "high": AbnormalityType.HIGH,
                "low": AbnormalityType.LOW,
                "critical": AbnormalityType.CRITICAL,
            }
            abnormality_type = abnormality_map.get(status_str, AbnormalityType.UNKNOWN)
            
            extraction = TestExtraction(
                test_name=finding.get("test", "Unknown"),
                test_name_normalized=None,
                value=value_numeric,
                value_text=value_text,
                unit=None,
                reference_range=ref_range,
                abnormal_flag=finding.get("flag", False),
                abnormality_type=abnormality_type,
                extraction_confidence=0.5,  # Legacy data has lower confidence
                extraction_status=ExtractionStatus.AMBIGUOUS
            )
            
            extractions.append(extraction)
        
        return extractions
