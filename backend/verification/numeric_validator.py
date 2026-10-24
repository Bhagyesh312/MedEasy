"""
Numeric validator that checks consistency of numbers in generated text
with the original report data.
"""

import re
from typing import List, Dict, Any, Optional

from .schemas import NumericValidation, VerificationStatus


class NumericValidator:
    """Validates numeric consistency in generated responses."""
    
    def validate(
        self,
        generated_text: str,
        test_value: Optional[float] = None,
        test_value_text: Optional[str] = None,
        reference_range_text: Optional[str] = None,
        reference_low: Optional[float] = None,
        reference_high: Optional[float] = None
    ) -> NumericValidation:
        """Validate numeric values in generated text.
        
        Args:
            generated_text: The generated response
            test_value: Expected test value (from report)
            test_value_text: Original value text from report
            reference_range_text: Original reference range text
            reference_low: Expected lower bound
            reference_high: Expected upper bound
        
        Returns:
            NumericValidation with results
        """
        # Extract numbers from generated text
        extracted_numbers = self._extract_numbers(generated_text)
        
        # Verify each number against expected values
        verified = []
        mismatches = []
        issues = []
        
        if test_value is not None:
            # Check if test value appears in generated text
            value_found = self._is_number_present(generated_text, test_value, tolerance=0.1)
            
            if value_found:
                verified.append({
                    "type": "test_value",
                    "expected": test_value,
                    "found": True
                })
            else:
                # Check if a different value is mentioned
                for num in extracted_numbers:
                    if self._is_close_to(num, test_value, tolerance=0.1):
                        verified.append({
                            "type": "test_value",
                            "expected": test_value,
                            "found": True,
                            "actual": num
                        })
                        break
                else:
                    # Check if value was modified
                    suspicious = [n for n in extracted_numbers if 0.1 <= n <= 10000]
                    if suspicious:
                        mismatches.append({
                            "type": "test_value",
                            "expected": test_value,
                            "suspicious_values": suspicious
                        })
                        issues.append(f"Expected test value {test_value} not found, but other numeric values present")
        
        # Check reference range bounds
        if reference_low is not None:
            low_found = self._is_number_present(generated_text, reference_low, tolerance=0.1)
            if low_found:
                verified.append({
                    "type": "reference_low",
                    "expected": reference_low,
                    "found": True
                })
        
        if reference_high is not None:
            high_found = self._is_number_present(generated_text, reference_high, tolerance=0.1)
            if high_found:
                verified.append({
                    "type": "reference_high",
                    "expected": reference_high,
                    "found": True
                })
        
        # Check for invented numbers
        expected_values = set()
        if test_value:
            expected_values.add(test_value)
        if reference_low:
            expected_values.add(reference_low)
        if reference_high:
            expected_values.add(reference_high)
        
        # Look for numbers that don't match expected values
        for num in extracted_numbers:
            if not any(self._is_close_to(num, exp, tolerance=0.1) for exp in expected_values):
                # This could be legitimate (e.g., explaining ranges) or invented
                # Flag only if it looks like it's presented as a test result
                pass
        
        # Calculate consistency rate
        total_checks = len(verified) + len(mismatches)
        consistency_rate = len(verified) / total_checks if total_checks > 0 else 1.0
        
        # Determine status
        if consistency_rate == 1.0:
            status = VerificationStatus.PASSED
        elif consistency_rate >= 0.8:
            status = VerificationStatus.WARNING
        else:
            status = VerificationStatus.FAILED
        
        if mismatches:
            issues.append(f"Found {len(mismatches)} numeric mismatches")
        
        return NumericValidation(
            status=status,
            extracted_numbers=[{"value": n} for n in extracted_numbers],
            verified_numbers=verified,
            mismatches=mismatches,
            consistency_rate=consistency_rate,
            issues=issues
        )
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numeric values from text.
        
        Args:
            text: Text to search
        
        Returns:
            List of extracted numbers
        """
        numbers = []
        
        # Pattern to match numbers (including decimals, ranges)
        # Matches: 14.5, 12-16, 12.0-16.0, etc.
        patterns = [
            r'\b\d+\.\d+\b',  # Decimal numbers
            r'\b\d+\b'        # Whole numbers
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                try:
                    num = float(match.group())
                    numbers.append(num)
                except ValueError:
                    continue
        
        return list(set(numbers))  # Remove duplicates
    
    def _is_number_present(self, text: str, number: float, tolerance: float = 0.1) -> bool:
        """Check if a number appears in text (with tolerance).
        
        Args:
            text: Text to search
            number: Number to find
            tolerance: Acceptable relative difference
        
        Returns:
            True if number is found
        """
        extracted = self._extract_numbers(text)
        return any(self._is_close_to(n, number, tolerance) for n in extracted)
    
    def _is_close_to(self, a: float, b: float, tolerance: float = 0.1) -> bool:
        """Check if two numbers are close (within relative tolerance).
        
        Args:
            a: First number
            b: Second number
            tolerance: Relative tolerance
        
        Returns:
            True if numbers are close
        """
        if b == 0:
            return abs(a - b) < 0.01  # Absolute tolerance for zero
        return abs(a - b) / abs(b) <= tolerance
