"""
Citation validator that verifies citations match retrieved passages.
"""

import re
from typing import List, Set

from .schemas import CitationValidation, VerificationStatus


class CitationValidator:
    """Validates that citations in generated text match retrieved passages."""
    
    def validate(
        self,
        generated_text: str,
        retrieved_passage_count: int,
        cited_sources: List[int]
    ) -> CitationValidation:
        """Validate citations in generated response.
        
        Args:
            generated_text: The generated response text
            retrieved_passage_count: Number of passages that were retrieved
            cited_sources: List of source indices that were actually cited
        
        Returns:
            CitationValidation with results
        """
        # Extract all citation patterns from text
        cited_indices = self._extract_citations(generated_text)
        
        # Determine valid range
        valid_range = set(range(1, retrieved_passage_count + 1))
        
        # Check which citations are valid
        valid_indices = [idx for idx in cited_indices if idx in valid_range]
        invalid_indices = [idx for idx in cited_indices if idx not in valid_range]
        
        # Calculate validation rate
        total_citations = len(cited_indices)
        validation_rate = len(valid_indices) / total_citations if total_citations > 0 else 1.0
        
        # Collect issues
        issues = []
        
        if invalid_indices:
            issues.append(f"Invalid citation indices found: {invalid_indices}")
        
        if total_citations == 0:
            issues.append("No citations found in response")
        
        # Check for fabricated citations (citing sources that weren't retrieved)
        fabricated = [idx for idx in cited_indices if idx > retrieved_passage_count]
        if fabricated:
            issues.append(f"Fabricated citations (beyond retrieved sources): {fabricated}")
        
        # Determine status
        if validation_rate == 1.0 and total_citations > 0:
            status = VerificationStatus.PASSED
        elif validation_rate >= 0.8:
            status = VerificationStatus.WARNING
        else:
            status = VerificationStatus.FAILED
        
        if total_citations == 0:
            status = VerificationStatus.WARNING
        
        return CitationValidation(
            status=status,
            cited_indices=cited_indices,
            valid_indices=valid_indices,
            invalid_indices=invalid_indices,
            total_citations=total_citations,
            validation_rate=validation_rate,
            issues=issues
        )
    
    def _extract_citations(self, text: str) -> List[int]:
        """Extract citation numbers from text.
        
        Looks for patterns like [1], [2], [3] in the text.
        
        Args:
            text: Text to search
        
        Returns:
            Sorted list of unique citation indices
        """
        citations = set()
        for match in re.finditer(r'\[(\d+)\]', text):
            citations.add(int(match.group(1)))
        return sorted(list(citations))
    
    def check_source_urls(self, cited_urls: List[str], expected_urls: List[str]) -> bool:
        """Verify that cited URLs actually exist in retrieved sources.
        
        Args:
            cited_urls: URLs mentioned in the response
            expected_urls: URLs from actually retrieved sources
        
        Returns:
            True if all cited URLs are valid
        """
        cited_set = set(cited_urls)
        expected_set = set(expected_urls)
        
        # Check if all cited URLs are in expected set
        return cited_set.issubset(expected_set)
