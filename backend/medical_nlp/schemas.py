"""
Pydantic schemas for structured medical data extraction and validation.

These schemas ensure data integrity and provide clear validation rules
for extracted laboratory test results.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import date, datetime
from enum import Enum


class ExtractionStatus(str, Enum):
    """Status of the extraction process for a test value."""
    VALIDATED = "validated"      # Successfully extracted and validated
    AMBIGUOUS = "ambiguous"      # Extracted but uncertain
    FAILED = "failed"            # Extraction failed
    MISSING = "missing"          # Value not present in report


class AbnormalityType(str, Enum):
    """Classification of abnormality flags."""
    NORMAL = "normal"
    HIGH = "high"
    LOW = "low"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ReferenceRange(BaseModel):
    """Represents a reference range for a laboratory test.
    
    Always preserves the original text from the report as the primary source.
    Numeric bounds are extracted where possible but may be None for complex ranges.
    """
    text: str = Field(..., description="Original text from the report (e.g., '12.0-16.0 g/dL')")
    low: Optional[float] = Field(None, description="Lower bound if numeric")
    high: Optional[float] = Field(None, description="Upper bound if numeric")
    unit: Optional[str] = Field(None, description="Unit from reference range if different from value unit")
    gender_specific: bool = Field(default=False, description="Whether range varies by gender")
    age_specific: bool = Field(default=False, description="Whether range varies by age")
    
    @field_validator('low', 'high')
    @classmethod
    def validate_bounds(cls, v, info):
        """Ensure bounds are positive where appropriate."""
        if v is not None and v < 0:
            # Allow negative values for certain tests (e.g., temperature in Celsius)
            pass  # Could add test-specific validation here
        return v
    
    def is_numeric(self) -> bool:
        """Check if this range has numeric bounds."""
        return self.low is not None or self.high is not None


class TestExtraction(BaseModel):
    """Represents a single extracted laboratory test result.
    
    Maintains both original and normalized representations to preserve
    data fidelity while enabling downstream processing.
    """
    
    # Core identifiers
    test_name: str = Field(..., description="Test name as it appears in the report")
    test_name_normalized: Optional[str] = Field(
        None, 
        description="Standardized test name (e.g., 'Hemoglobin' for 'Hb', 'HGB', etc.)"
    )
    test_code: Optional[str] = Field(None, description="LOINC or other standard code if available")
    
    # Value information
    value: Optional[float] = Field(None, description="Numeric value if parseable")
    value_text: str = Field(..., description="Original value text from report (e.g., '13.5', '<5', 'Positive')")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., 'g/dL', 'mg/dL', 'mmol/L')")
    
    # Reference information
    reference_range: Optional[ReferenceRange] = Field(
        None, 
        description="Reference range from the report"
    )
    
    # Abnormality flags
    abnormal_flag: Optional[bool] = Field(
        None, 
        description="Whether flagged as abnormal in the report"
    )
    abnormality_type: AbnormalityType = Field(
        default=AbnormalityType.UNKNOWN,
        description="Classification of abnormality"
    )
    
    # Metadata
    collection_date: Optional[date] = Field(None, description="Specimen collection date")
    report_date: Optional[date] = Field(None, description="Report generation date")
    specimen_type: Optional[str] = Field(None, description="Type of specimen (e.g., 'Blood', 'Urine')")
    source_page: int = Field(default=1, ge=1, description="Page number in source PDF")
    source_location: Optional[str] = Field(
        None, 
        description="Location descriptor (e.g., 'Table 1, Row 3')"
    )
    
    # Extraction quality
    extraction_confidence: float = Field(
        default=0.0, 
        ge=0.0, 
        le=1.0,
        description="Confidence score for this extraction (0.0-1.0)"
    )
    extraction_status: ExtractionStatus = Field(
        default=ExtractionStatus.VALIDATED,
        description="Status of the extraction"
    )
    extraction_notes: Optional[str] = Field(
        None,
        description="Notes about extraction issues or ambiguities"
    )
    
    @field_validator('value_text')
    @classmethod
    def validate_value_text(cls, v):
        """Ensure value text is not empty."""
        if not v or not v.strip():
            raise ValueError("value_text cannot be empty")
        return v.strip()
    
    @field_validator('test_name')
    @classmethod
    def validate_test_name(cls, v):
        """Ensure test name is not empty."""
        if not v or not v.strip():
            raise ValueError("test_name cannot be empty")
        return v.strip()
    
    def is_numeric(self) -> bool:
        """Check if the value is numeric."""
        return self.value is not None
    
    def is_in_range(self) -> Optional[bool]:
        """Determine if the numeric value is within the reference range.
        
        Returns:
            True if in range, False if out of range, None if unable to determine
        """
        if not self.is_numeric() or not self.reference_range or not self.reference_range.is_numeric():
            return None
        
        value = self.value
        low = self.reference_range.low
        high = self.reference_range.high
        
        if low is not None and high is not None:
            return low <= value <= high
        elif low is not None:
            return value >= low
        elif high is not None:
            return value <= high
        
        return None
    
    def calculate_abnormality(self) -> AbnormalityType:
        """Calculate abnormality type based on value and reference range."""
        in_range = self.is_in_range()
        
        if in_range is None:
            # Can't determine numerically, use flag if available
            if self.abnormal_flag is True:
                return AbnormalityType.UNKNOWN
            elif self.abnormal_flag is False:
                return AbnormalityType.NORMAL
            return AbnormalityType.UNKNOWN
        
        if in_range:
            return AbnormalityType.NORMAL
        
        # Out of range - determine if high or low
        if self.value is not None and self.reference_range:
            if self.reference_range.high is not None and self.value > self.reference_range.high:
                # Check if critically high (>1.5x upper limit)
                if self.value >= self.reference_range.high * 1.5:
                    return AbnormalityType.CRITICAL
                return AbnormalityType.HIGH
            elif self.reference_range.low is not None and self.value < self.reference_range.low:
                # Check if critically low (<0.75x lower limit)
                if self.value <= self.reference_range.low * 0.75:
                    return AbnormalityType.CRITICAL
                return AbnormalityType.LOW
        
        return AbnormalityType.UNKNOWN


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process."""
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    extractor_version: str = Field(default="1.0.0")
    pdf_filename: str
    patient_name: Optional[str] = None
    is_scanned: bool = Field(default=False, description="Whether PDF was scanned and required OCR")
    page_count: int = Field(default=1, ge=1)
    extraction_method: Literal["text", "ocr", "hybrid"] = "text"
    processing_time_seconds: Optional[float] = None
    error_count: int = Field(default=0, ge=0)
    warning_count: int = Field(default=0, ge=0)


class ReportExtraction(BaseModel):
    """Complete extraction result for a laboratory report."""
    
    metadata: ExtractionMetadata
    tests: List[TestExtraction] = Field(default_factory=list)
    raw_text: Optional[str] = Field(None, description="Raw extracted text from PDF")
    
    def get_flagged_tests(self) -> List[TestExtraction]:
        """Get all tests flagged as abnormal."""
        return [t for t in self.tests if t.abnormal_flag is True]
    
    def get_normal_tests(self) -> List[TestExtraction]:
        """Get all tests with normal values."""
        return [t for t in self.tests if t.abnormal_flag is False]
    
    def get_critical_tests(self) -> List[TestExtraction]:
        """Get all tests marked as critical."""
        return [t for t in self.tests if t.abnormality_type == AbnormalityType.CRITICAL]
    
    def get_tests_by_status(self, status: ExtractionStatus) -> List[TestExtraction]:
        """Get tests by extraction status."""
        return [t for t in self.tests if t.extraction_status == status]
    
    def get_statistics(self) -> dict:
        """Get summary statistics about the extraction."""
        return {
            "total_tests": len(self.tests),
            "normal": len([t for t in self.tests if t.abnormality_type == AbnormalityType.NORMAL]),
            "high": len([t for t in self.tests if t.abnormality_type == AbnormalityType.HIGH]),
            "low": len([t for t in self.tests if t.abnormality_type == AbnormalityType.LOW]),
            "critical": len([t for t in self.tests if t.abnormality_type == AbnormalityType.CRITICAL]),
            "unknown": len([t for t in self.tests if t.abnormality_type == AbnormalityType.UNKNOWN]),
            "validated": len(self.get_tests_by_status(ExtractionStatus.VALIDATED)),
            "ambiguous": len(self.get_tests_by_status(ExtractionStatus.AMBIGUOUS)),
            "failed": len(self.get_tests_by_status(ExtractionStatus.FAILED)),
            "numeric_values": len([t for t in self.tests if t.is_numeric()]),
            "with_reference_range": len([t for t in self.tests if t.reference_range is not None]),
        }
    
    def to_legacy_format(self) -> List[dict]:
        """Convert to the legacy findings format for backward compatibility.
        
        Returns a list of dictionaries matching the existing database schema.
        """
        legacy = []
        for test in self.tests:
            # Map to existing database fields
            legacy.append({
                "test": test.test_name_normalized or test.test_name,
                "value": test.value_text,
                "reference_range": test.reference_range.text if test.reference_range else "Not specified",
                "status": test.abnormality_type.value.capitalize(),
                "flag": test.abnormal_flag if test.abnormal_flag is not None else False,
                # These fields would be filled by the LLM generation step
                "what_it_measures": "",
                "explanation": "",
                "symptoms": [],
                "urgency": "Routine",
                "likely_next_step": "",
                "action": "",
            })
        return legacy
