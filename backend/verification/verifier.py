"""
Main verification pipeline that orchestrates all validation checks.
"""

from typing import Optional, List
import re

from .schemas import VerificationResult, VerificationStatus, ClaimValidation
from .citation_validator import CitationValidator
from .numeric_validator import NumericValidator


class ResponseVerifier:
    """Orchestrates multiple verification checks on generated responses."""
    
    def __init__(self, use_nli: bool = False):
        """Initialize verifier.
        
        Args:
            use_nli: Whether to use NLI-based claim verification (requires model)
        """
        self.citation_validator = CitationValidator()
        self.numeric_validator = NumericValidator()
        self.use_nli = use_nli
    
    def verify(
        self,
        generated_text: str,
        retrieved_passage_count: int,
        cited_sources: List[int],
        test_value: Optional[float] = None,
        test_value_text: Optional[str] = None,
        reference_range_text: Optional[str] = None,
        reference_low: Optional[float] = None,
        reference_high: Optional[float] = None,
        retrieved_passages: Optional[List[str]] = None
    ) -> VerificationResult:
        """Perform complete verification of a generated response.
        
        Args:
            generated_text: The generated response text
            retrieved_passage_count: Number of passages retrieved
            cited_sources: List of cited source indices
            test_value: Expected test value from report
            test_value_text: Original value text
            reference_range_text: Original reference range text
            reference_low: Lower bound of reference range
            reference_high: Upper bound of reference range
            retrieved_passages: Actual retrieved passage texts (for NLI)
        
        Returns:
            VerificationResult with all validation results
        """
        # Run citation validation
        citation_result = self.citation_validator.validate(
            generated_text=generated_text,
            retrieved_passage_count=retrieved_passage_count,
            cited_sources=cited_sources
        )
        
        # Run numeric validation
        numeric_result = self.numeric_validator.validate(
            generated_text=generated_text,
            test_value=test_value,
            test_value_text=test_value_text,
            reference_range_text=reference_range_text,
            reference_low=reference_low,
            reference_high=reference_high
        )
        
        # Run NLI validation if enabled and passages provided
        claim_result = None
        if self.use_nli and retrieved_passages:
            claim_result = self._validate_claims_simple(
                generated_text=generated_text,
                retrieved_passages=retrieved_passages
            )
        
        # Aggregate results
        total_issues = (
            len(citation_result.issues) +
            len(numeric_result.issues) +
            (len(claim_result.issues) if claim_result else 0)
        )
        
        # Count critical issues
        critical_issues = 0
        if citation_result.status == VerificationStatus.FAILED:
            critical_issues += 1
        if numeric_result.status == VerificationStatus.FAILED:
            critical_issues += 1
        if claim_result and claim_result.status == VerificationStatus.FAILED:
            critical_issues += 1
        
        # Count warnings
        warnings = 0
        if citation_result.status == VerificationStatus.WARNING:
            warnings += 1
        if numeric_result.status == VerificationStatus.WARNING:
            warnings += 1
        if claim_result and claim_result.status == VerificationStatus.WARNING:
            warnings += 1
        
        # Determine overall status
        if critical_issues > 0:
            overall_status = VerificationStatus.FAILED
            passed = False
        elif warnings > 1:
            overall_status = VerificationStatus.WARNING
            passed = True  # Pass with warnings
        else:
            overall_status = VerificationStatus.PASSED
            passed = True
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            citation_result,
            numeric_result,
            claim_result
        )
        
        # Generate recommendations
        recommendations = []
        should_regenerate = False
        should_abstain = False
        
        if citation_result.validation_rate < 0.8:
            recommendations.append("Improve citation accuracy")
            should_regenerate = True
        
        if numeric_result.consistency_rate < 0.9:
            recommendations.append("Verify numeric values against report")
            should_regenerate = True
        
        if claim_result and claim_result.support_rate < 0.7:
            recommendations.append("Ensure claims are supported by evidence")
            should_regenerate = True
        
        if citation_result.total_citations == 0:
            recommendations.append("Add source citations to response")
            should_abstain = True
        
        if critical_issues >= 2:
            recommendations.append("Multiple critical issues - consider abstaining")
            should_abstain = True
        
        return VerificationResult(
            overall_status=overall_status,
            passed=passed,
            confidence=confidence,
            citation_validation=citation_result,
            numeric_validation=numeric_result,
            claim_validation=claim_result,
            total_issues=total_issues,
            critical_issues=critical_issues,
            warnings=warnings,
            should_regenerate=should_regenerate,
            should_abstain=should_abstain,
            recommendations=recommendations
        )
    
    def _validate_claims_simple(
        self,
        generated_text: str,
        retrieved_passages: List[str]
    ) -> ClaimValidation:
        """Simple claim validation without NLI model.
        
        Uses heuristics to check if claims might be supported.
        For production, replace with actual NLI model.
        
        Args:
            generated_text: Generated response
            retrieved_passages: Retrieved evidence passages
        
        Returns:
            ClaimValidation result
        """
        # Extract sentences as claims
        sentences = [s.strip() for s in re.split(r'[.!?]+', generated_text) if s.strip()]
        
        # Simple keyword-based checking
        supported = 0
        neutral = 0
        
        for sentence in sentences:
            # Check if any passage contains similar keywords
            words = set(sentence.lower().split())
            words = {w for w in words if len(w) > 3}  # Filter short words
            
            if not words:
                neutral += 1
                continue
            
            # Check overlap with passages
            found_support = False
            for passage in retrieved_passages:
                passage_words = set(passage.lower().split())
                overlap = len(words & passage_words) / len(words)
                if overlap > 0.3:  # 30% word overlap
                    found_support = True
                    break
            
            if found_support:
                supported += 1
            else:
                neutral += 1
        
        total_claims = len(sentences)
        support_rate = supported / total_claims if total_claims > 0 else 0.0
        
        # Determine status
        if support_rate >= 0.7:
            status = VerificationStatus.PASSED
        elif support_rate >= 0.5:
            status = VerificationStatus.WARNING
        else:
            status = VerificationStatus.WARNING  # Not FAILED since this is heuristic
        
        issues = []
        if support_rate < 0.5:
            issues.append(f"Low claim support rate: {support_rate:.1%}")
        
        return ClaimValidation(
            status=status,
            claims_checked=total_claims,
            supported_claims=supported,
            contradicted_claims=0,  # Would need NLI model
            neutral_claims=neutral,
            support_rate=support_rate,
            issues=issues
        )
    
    def _calculate_confidence(
        self,
        citation_result,
        numeric_result,
        claim_result
    ) -> float:
        """Calculate overall confidence score.
        
        Args:
            citation_result: CitationValidation
            numeric_result: NumericValidation
            claim_result: Optional ClaimValidation
        
        Returns:
            Confidence score (0-1)
        """
        # Weighted average of validation rates
        weights = {
            'citation': 0.4,
            'numeric': 0.4,
            'claims': 0.2
        }
        
        confidence = (
            citation_result.validation_rate * weights['citation'] +
            numeric_result.consistency_rate * weights['numeric']
        )
        
        if claim_result:
            confidence += claim_result.support_rate * weights['claims']
        else:
            # Redistribute claim weight
            confidence += 0.5 * weights['claims']  # Neutral score
        
        return round(confidence, 3)
