"""
RxNorm Drug Database Integration

For suggesting medications based on lab results
(e.g., iron supplements for low hemoglobin)
"""

import requests
import psycopg2
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class RxNormIntegrator:
    """Integrate RxNorm for medication suggestions."""
    
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
    
    def create_medication_table(self):
        """Create medications reference table."""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS medications (
                    rxcui VARCHAR(20) PRIMARY KEY,
                    drug_name VARCHAR(255) NOT NULL,
                    generic_name VARCHAR(255),
                    drug_class VARCHAR(100),
                    indication TEXT,
                    common_uses TEXT[],
                    related_conditions TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_medication_name 
                ON medications(drug_name);
                
                CREATE INDEX IF NOT EXISTS idx_medication_class 
                ON medications(drug_class);
            """)
            self.conn.commit()
    
    def search_drug(self, drug_name: str) -> List[Dict]:
        """Search RxNorm API for drug information."""
        url = f"{self.BASE_URL}/drugs.json?name={drug_name}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            drugs = data.get('drugGroup', {}).get('conceptGroup', [])
            
            results = []
            for group in drugs:
                for drug in group.get('conceptProperties', []):
                    results.append({
                        'rxcui': drug.get('rxcui'),
                        'name': drug.get('name'),
                        'synonym': drug.get('synonym', '')
                    })
            return results
        return []
    
    def get_drug_interactions(self, rxcui: str) -> List[str]:
        """Get drug interactions for a medication."""
        url = f"{self.BASE_URL}/interaction/interaction.json?rxcui={rxcui}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            interactions = []
            
            groups = data.get('interactionTypeGroup', [])
            for group in groups:
                for interaction in group.get('interactionType', []):
                    for pair in interaction.get('interactionPair', []):
                        interactions.append(pair.get('description', ''))
            
            return interactions
        return []
    
    def suggest_supplements(self, deficiency: str) -> List[Dict]:
        """Suggest supplements based on deficiency.
        
        Args:
            deficiency: e.g., "iron", "vitamin b12", "vitamin d"
        """
        supplement_map = {
            "iron": ["Ferrous sulfate", "Ferrous gluconate", "Iron supplement"],
            "vitamin b12": ["Cyanocobalamin", "Methylcobalamin", "B12 supplement"],
            "vitamin d": ["Cholecalciferol", "Vitamin D3", "Ergocalciferol"],
            "calcium": ["Calcium carbonate", "Calcium citrate"],
            "magnesium": ["Magnesium oxide", "Magnesium citrate"],
            "potassium": ["Potassium chloride", "Potassium citrate"]
        }
        
        supplements = supplement_map.get(deficiency.lower(), [])
        results = []
        
        for supp in supplements:
            drug_info = self.search_drug(supp)
            if drug_info:
                results.append({
                    'supplement': supp,
                    'rxcui': drug_info[0].get('rxcui'),
                    'name': drug_info[0].get('name')
                })
        
        return results
    
    def close(self):
        self.conn.close()


# Example usage
if __name__ == "__main__":
    integrator = RxNormIntegrator()
    
    # Create table
    integrator.create_medication_table()
    
    # Search for iron supplements
    iron_supps = integrator.suggest_supplements("iron")
    for supp in iron_supps:
        print(f"Supplement: {supp['name']} (RxCUI: {supp['rxcui']})")
    
    # Check interactions
    if iron_supps:
        interactions = integrator.get_drug_interactions(iron_supps[0]['rxcui'])
        print(f"\nInteractions: {len(interactions)} found")
    
    integrator.close()
