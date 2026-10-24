"""
Medical terminology normalization for laboratory test names.

Provides mapping from common abbreviations and variations to standardized
test names, enabling consistent downstream processing and comparison.
"""

from typing import Optional, List, Tuple
import re
from difflib import SequenceMatcher


class TerminologyNormalizer:
    """Normalizes laboratory test names to standard terminology.
    
    Uses a curated mapping dictionary combined with fuzzy matching
    to handle variations in test naming across different laboratories.
    """
    
    # Comprehensive mapping of test name variations to standardized names
    # Format: {variant: (standard_name, category)}
    TERMINOLOGY_MAP = {
        # Hemoglobin
        "hemoglobin": ("Hemoglobin", "hematology"),
        "hb": ("Hemoglobin", "hematology"),
        "hgb": ("Hemoglobin", "hematology"),
        "haemoglobin": ("Hemoglobin", "hematology"),
        "hb%": ("Hemoglobin", "hematology"),
        
        # White Blood Cell Count
        "wbc": ("White Blood Cell Count", "hematology"),
        "white blood cell": ("White Blood Cell Count", "hematology"),
        "white blood cells": ("White Blood Cell Count", "hematology"),
        "white blood cell count": ("White Blood Cell Count", "hematology"),
        "leukocyte count": ("White Blood Cell Count", "hematology"),
        "leukocytes": ("White Blood Cell Count", "hematology"),
        "total wbc": ("White Blood Cell Count", "hematology"),
        "tc": ("White Blood Cell Count", "hematology"),
        
        # Red Blood Cell Count
        "rbc": ("Red Blood Cell Count", "hematology"),
        "red blood cell": ("Red Blood Cell Count", "hematology"),
        "red blood cells": ("Red Blood Cell Count", "hematology"),
        "erythrocyte count": ("Red Blood Cell Count", "hematology"),
        "total rbc": ("Red Blood Cell Count", "hematology"),
        
        # Platelet Count
        "platelet": ("Platelet Count", "hematology"),
        "platelets": ("Platelet Count", "hematology"),
        "plt": ("Platelet Count", "hematology"),
        "thrombocyte count": ("Platelet Count", "hematology"),
        
        # Hematocrit
        "hematocrit": ("Hematocrit", "hematology"),
        "hct": ("Hematocrit", "hematology"),
        "haematocrit": ("Hematocrit", "hematology"),
        "pcv": ("Hematocrit", "hematology"),
        "packed cell volume": ("Hematocrit", "hematology"),
        
        # MCV, MCH, MCHC
        "mcv": ("Mean Corpuscular Volume", "hematology"),
        "mean corpuscular volume": ("Mean Corpuscular Volume", "hematology"),
        "mch": ("Mean Corpuscular Hemoglobin", "hematology"),
        "mean corpuscular hemoglobin": ("Mean Corpuscular Hemoglobin", "hematology"),
        "mchc": ("Mean Corpuscular Hemoglobin Concentration", "hematology"),
        "mean corpuscular hemoglobin concentration": ("Mean Corpuscular Hemoglobin Concentration", "hematology"),
        
        # Blood Glucose
        "glucose": ("Blood Glucose", "chemistry"),
        "blood sugar": ("Blood Glucose", "chemistry"),
        "blood glucose": ("Blood Glucose", "chemistry"),
        "plasma glucose": ("Blood Glucose", "chemistry"),
        "fasting blood sugar": ("Fasting Blood Glucose", "chemistry"),
        "fbs": ("Fasting Blood Glucose", "chemistry"),
        "fasting glucose": ("Fasting Blood Glucose", "chemistry"),
        "random blood sugar": ("Random Blood Glucose", "chemistry"),
        "rbs": ("Random Blood Glucose", "chemistry"),
        "ppbs": ("Postprandial Blood Glucose", "chemistry"),
        "pp blood sugar": ("Postprandial Blood Glucose", "chemistry"),
        
        # HbA1c
        "hba1c": ("Hemoglobin A1c", "chemistry"),
        "glycated hemoglobin": ("Hemoglobin A1c", "chemistry"),
        "glycosylated hemoglobin": ("Hemoglobin A1c", "chemistry"),
        "a1c": ("Hemoglobin A1c", "chemistry"),
        
        # Lipid Panel
        "cholesterol": ("Total Cholesterol", "lipids"),
        "total cholesterol": ("Total Cholesterol", "lipids"),
        "triglycerides": ("Triglycerides", "lipids"),
        "tg": ("Triglycerides", "lipids"),
        "hdl": ("HDL Cholesterol", "lipids"),
        "hdl cholesterol": ("HDL Cholesterol", "lipids"),
        "high density lipoprotein": ("HDL Cholesterol", "lipids"),
        "ldl": ("LDL Cholesterol", "lipids"),
        "ldl cholesterol": ("LDL Cholesterol", "lipids"),
        "low density lipoprotein": ("LDL Cholesterol", "lipids"),
        "vldl": ("VLDL Cholesterol", "lipids"),
        "vldl cholesterol": ("VLDL Cholesterol", "lipids"),
        
        # Liver Function Tests
        "sgot": ("AST (SGOT)", "liver"),
        "ast": ("AST (SGOT)", "liver"),
        "aspartate aminotransferase": ("AST (SGOT)", "liver"),
        "sgpt": ("ALT (SGPT)", "liver"),
        "alt": ("ALT (SGPT)", "liver"),
        "alanine aminotransferase": ("ALT (SGPT)", "liver"),
        "alp": ("Alkaline Phosphatase", "liver"),
        "alkaline phosphatase": ("Alkaline Phosphatase", "liver"),
        "bilirubin": ("Total Bilirubin", "liver"),
        "total bilirubin": ("Total Bilirubin", "liver"),
        "direct bilirubin": ("Direct Bilirubin", "liver"),
        "indirect bilirubin": ("Indirect Bilirubin", "liver"),
        "total protein": ("Total Protein", "liver"),
        "albumin": ("Albumin", "liver"),
        "globulin": ("Globulin", "liver"),
        "a/g ratio": ("Albumin/Globulin Ratio", "liver"),
        "albumin globulin ratio": ("Albumin/Globulin Ratio", "liver"),
        
        # Kidney Function Tests
        "creatinine": ("Creatinine", "kidney"),
        "serum creatinine": ("Creatinine", "kidney"),
        "urea": ("Blood Urea", "kidney"),
        "blood urea": ("Blood Urea", "kidney"),
        "bun": ("Blood Urea Nitrogen", "kidney"),
        "blood urea nitrogen": ("Blood Urea Nitrogen", "kidney"),
        "uric acid": ("Uric Acid", "kidney"),
        
        # Thyroid Function Tests
        "tsh": ("TSH", "thyroid"),
        "thyroid stimulating hormone": ("TSH", "thyroid"),
        "t3": ("T3", "thyroid"),
        "triiodothyronine": ("T3", "thyroid"),
        "t4": ("T4", "thyroid"),
        "thyroxine": ("T4", "thyroid"),
        "free t3": ("Free T3", "thyroid"),
        "free t4": ("Free T4", "thyroid"),
        "ft3": ("Free T3", "thyroid"),
        "ft4": ("Free T4", "thyroid"),
        
        # Electrolytes
        "sodium": ("Sodium", "electrolytes"),
        "na": ("Sodium", "electrolytes"),
        "potassium": ("Potassium", "electrolytes"),
        "k": ("Potassium", "electrolytes"),
        "chloride": ("Chloride", "electrolytes"),
        "cl": ("Chloride", "electrolytes"),
        "calcium": ("Calcium", "electrolytes"),
        "ca": ("Calcium", "electrolytes"),
        "magnesium": ("Magnesium", "electrolytes"),
        "mg": ("Magnesium", "electrolytes"),
        "phosphorus": ("Phosphorus", "electrolytes"),
        
        # Vitamins
        "vitamin d": ("Vitamin D", "vitamins"),
        "vit d": ("Vitamin D", "vitamins"),
        "25-oh vitamin d": ("Vitamin D", "vitamins"),
        "vitamin b12": ("Vitamin B12", "vitamins"),
        "vit b12": ("Vitamin B12", "vitamins"),
        "cyanocobalamin": ("Vitamin B12", "vitamins"),
        "folate": ("Folate", "vitamins"),
        "folic acid": ("Folate", "vitamins"),
        
        # Cardiac Markers
        "troponin": ("Troponin", "cardiac"),
        "troponin i": ("Troponin I", "cardiac"),
        "troponin t": ("Troponin T", "cardiac"),
        "ck": ("Creatine Kinase", "cardiac"),
        "cpk": ("Creatine Kinase", "cardiac"),
        "ck-mb": ("CK-MB", "cardiac"),
        "ldh": ("Lactate Dehydrogenase", "cardiac"),
        
        # Inflammatory Markers
        "esr": ("ESR", "inflammatory"),
        "erythrocyte sedimentation rate": ("ESR", "inflammatory"),
        "crp": ("C-Reactive Protein", "inflammatory"),
        "c-reactive protein": ("C-Reactive Protein", "inflammatory"),
        
        # Iron Studies
        "iron": ("Serum Iron", "iron_studies"),
        "serum iron": ("Serum Iron", "iron_studies"),
        "ferritin": ("Ferritin", "iron_studies"),
        "tibc": ("TIBC", "iron_studies"),
        "total iron binding capacity": ("TIBC", "iron_studies"),
        "transferrin": ("Transferrin", "iron_studies"),
        "transferrin saturation": ("Transferrin Saturation", "iron_studies"),
        
        # Hormones
        "cortisol": ("Cortisol", "hormones"),
        "testosterone": ("Testosterone", "hormones"),
        "estrogen": ("Estrogen", "hormones"),
        "progesterone": ("Progesterone", "hormones"),
        "prolactin": ("Prolactin", "hormones"),
        "fsh": ("FSH", "hormones"),
        "lh": ("LH", "hormones"),
        
        # Coagulation
        "pt": ("Prothrombin Time", "coagulation"),
        "prothrombin time": ("Prothrombin Time", "coagulation"),
        "inr": ("INR", "coagulation"),
        "aptt": ("aPTT", "coagulation"),
        "ptt": ("PTT", "coagulation"),
        "activated partial thromboplastin time": ("aPTT", "coagulation"),
    }
    
    def __init__(self, fuzzy_threshold: float = 0.85):
        """Initialize the terminology normalizer.
        
        Args:
            fuzzy_threshold: Minimum similarity score (0-1) for fuzzy matching
        """
        self.fuzzy_threshold = fuzzy_threshold
        
        # Build reverse lookup for categories
        self.category_map = {}
        for variant, (standard, category) in self.TERMINOLOGY_MAP.items():
            if standard not in self.category_map:
                self.category_map[standard] = category
    
    def normalize(self, test_name: str) -> Tuple[Optional[str], Optional[str], float]:
        """Normalize a test name to standard terminology.
        
        Args:
            test_name: Original test name from the report
        
        Returns:
            Tuple of (normalized_name, category, confidence_score)
            Returns (None, None, 0.0) if no match found
        """
        if not test_name or not test_name.strip():
            return None, None, 0.0
        
        # Clean the input
        cleaned = self._clean_test_name(test_name)
        
        # Try exact match first
        if cleaned in self.TERMINOLOGY_MAP:
            standard, category = self.TERMINOLOGY_MAP[cleaned]
            return standard, category, 1.0
        
        # Try fuzzy matching
        best_match = None
        best_score = 0.0
        
        for variant, (standard, category) in self.TERMINOLOGY_MAP.items():
            score = self._similarity(cleaned, variant)
            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_match = (standard, category)
        
        if best_match:
            return best_match[0], best_match[1], best_score
        
        # No match found - return original with flag
        return None, None, 0.0
    
    def _clean_test_name(self, name: str) -> str:
        """Clean and normalize test name for matching."""
        # Convert to lowercase
        name = name.lower().strip()
        
        # Remove parenthetical content
        name = re.sub(r'\(.*?\)', '', name)
        
        # Remove common prefixes/suffixes ONLY if not part of the test name
        # Don't remove "blood" from "white blood cell"
        name = re.sub(r'\b(serum|plasma|total)\b', '', name)
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove special characters except /
        name = re.sub(r'[^\w\s/]', '', name)
        
        return name
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity score between two strings."""
        return SequenceMatcher(None, a, b).ratio()
    
    def get_category(self, normalized_name: str) -> Optional[str]:
        """Get the category for a normalized test name."""
        return self.category_map.get(normalized_name)
    
    def get_all_variations(self, standard_name: str) -> List[str]:
        """Get all known variations for a standard test name."""
        variations = []
        for variant, (standard, _) in self.TERMINOLOGY_MAP.items():
            if standard == standard_name:
                variations.append(variant)
        return variations
    
    def is_ambiguous(self, test_name: str) -> bool:
        """Check if a test name might be ambiguous.
        
        Returns True for abbreviations that could have multiple meanings.
        """
        cleaned = self._clean_test_name(test_name)
        
        # Single letters are often ambiguous without context
        if len(cleaned) == 1:
            return True
        
        # Check for very short abbreviations
        if len(cleaned) <= 2 and cleaned not in self.TERMINOLOGY_MAP:
            return True
        
        return False
    
    def suggest_alternatives(self, test_name: str, limit: int = 3) -> List[Tuple[str, str, float]]:
        """Suggest possible matches for an ambiguous test name.
        
        Args:
            test_name: Original test name
            limit: Maximum number of suggestions
        
        Returns:
            List of (normalized_name, category, confidence) tuples
        """
        cleaned = self._clean_test_name(test_name)
        matches = []
        
        for variant, (standard, category) in self.TERMINOLOGY_MAP.items():
            score = self._similarity(cleaned, variant)
            if score >= 0.5:  # Lower threshold for suggestions
                matches.append((standard, category, score))
        
        # Sort by score and deduplicate
        matches.sort(key=lambda x: x[2], reverse=True)
        seen = set()
        unique_matches = []
        for match in matches:
            if match[0] not in seen:
                unique_matches.append(match)
                seen.add(match[0])
                if len(unique_matches) >= limit:
                    break
        
        return unique_matches
