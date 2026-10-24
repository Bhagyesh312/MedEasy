"""
Medical NLP Pipeline for MedEasy AI 2.0

This package provides structured medical entity extraction,
terminology normalization, and validation for laboratory reports.
"""

from .schemas import (
    ReferenceRange,
    TestExtraction,
    ReportExtraction,
    ExtractionMetadata,
    ExtractionStatus,
    AbnormalityType
)
from .extractor import MedicalEntityExtractor
from .terminology import TerminologyNormalizer

__all__ = [
    'ReferenceRange',
    'TestExtraction',
    'ReportExtraction',
    'ExtractionMetadata',
    'ExtractionStatus',
    'AbnormalityType',
    'MedicalEntityExtractor',
    'TerminologyNormalizer',
]
