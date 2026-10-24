"""
Schemas for hallucination verification and validation results.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class VerificationStatus(str, Enum):
    """Status of verification check."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class CitationValidation(BaseModel):
    """Result of citation validation."""
    
    status: VerificationStatus
    cited_indices: List[int] = Field(default_factory=list)
    valid_indices: List[int] = Field(default_factory=list)
    invalid_indices: List[int] = Field(default_factory=list)
    total_citations: int = 0
    validation_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    issues: List[str] = Field(default_factory=list)


class NumericValidation(BaseModel):
    """Result of numeric consistency validation."""
    
    status: VerificationStatus
    extracted_numbers: List[Dict[str, Any]] = Field(default_factory=list)
    verified_numbers: List[Dict[str, Any]] = Field(default_factory=list)
    mismatches: List[Dict[str, Any]] = Field(default_factory=list)
    consistency_rate: float = Field(ge=0.0, le=1.0, default=1.0)
    issues: List[str] = Field(default_factory=list)


class ClaimValidation(BaseModel):
    """Result of NLI-based claim validation."""
    
    status: VerificationStatus
    claims_checked: int = 0
    supported_claims: int = 0
    contradicted_claims: int = 0
    neutral_claims: int = 0
    support_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    issues: List[str] = Field(default_factory=list)
    detailed_results: List[Dict[str, Any]] = Field(default_factory=list)


class VerificationResult(BaseModel):
    """Complete verification result for a generated response."""
    
    # Overall status
    overall_status: VerificationStatus
    passed: bool = False
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Individual validations
    citation_validation: CitationValidation
    numeric_validation: NumericValidation
    claim_validation: Optional[ClaimValidation] = None
    
    # Aggregated metrics
    total_issues: int = 0
    critical_issues: int = 0
    warnings: int = 0
    
    # Recommendations
    should_regenerate: bool = False
    should_abstain: bool = False
    recommendations: List[str] = Field(default_factory=list)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of verification results."""
        return {
            "status": self.overall_status.value,
            "passed": self.passed,
            "confidence": self.confidence,
            "citations_valid": self.citation_validation.validation_rate,
            "numeric_consistent": self.numeric_validation.consistency_rate,
            "claims_supported": self.claim_validation.support_rate if self.claim_validation else None,
            "total_issues": self.total_issues,
            "should_regenerate": self.should_regenerate,
            "should_abstain": self.should_abstain
        }
