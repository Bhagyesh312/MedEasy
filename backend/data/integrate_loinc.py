"""
LOINC Database Integration for MedEasy AI 2.0

Download LOINC database from https://loinc.org/downloads/
and integrate standardized lab test codes.
"""

import pandas as pd
import psycopg2
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()


class LOINCIntegrator:
    """Integrate LOINC database for standardized lab test codes."""
    
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
    
    def create_loinc_table(self):
        """Create LOINC reference table in PostgreSQL."""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS loinc_tests (
                    loinc_code VARCHAR(20) PRIMARY KEY,
                    component VARCHAR(255),
                    property VARCHAR(100),
                    time_aspect VARCHAR(50),
                    system VARCHAR(100),
                    scale_type VARCHAR(50),
                    method_type VARCHAR(100),
                    class VARCHAR(50),
                    common_name TEXT,
                    units TEXT,
                    reference_range_low DECIMAL(10,2),
                    reference_range_high DECIMAL(10,2),
                    synonyms TEXT[],
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_loinc_component 
                ON loinc_tests(component);
                
                CREATE INDEX IF NOT EXISTS idx_loinc_class 
                ON loinc_tests(class);
            """)
            self.conn.commit()
    
    def load_loinc_csv(self, csv_path: str):
        """Load LOINC data from CSV file.
        
        Download LOINC database from https://loinc.org/downloads/
        File: Loinc.csv (after registration, it's free)
        """
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Filter for laboratory tests only
        lab_tests = df[df['CLASS'] == 'LABORATORY'].copy()
        
        # Common lab test categories
        common_categories = [
            'HEM/BC',    # Hematology
            'CHEM',      # Chemistry
            'SERO',      # Serology
            'MICRO',     # Microbiology
            'ABXBACT',   # Antibiotic susceptibility
        ]
        
        lab_tests = lab_tests[lab_tests['CLASS'].isin(common_categories)]
        
        print(f"Loading {len(lab_tests)} LOINC lab tests...")
        
        with self.conn.cursor() as cur:
            for _, row in lab_tests.iterrows():
                try:
                    cur.execute("""
                        INSERT INTO loinc_tests 
                        (loinc_code, component, property, time_aspect, system, 
                         scale_type, method_type, class, common_name, description)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (loinc_code) DO NOTHING
                    """, (
                        row.get('LOINC_NUM'),
                        row.get('COMPONENT'),
                        row.get('PROPERTY'),
                        row.get('TIME_ASPCT'),
                        row.get('SYSTEM'),
                        row.get('SCALE_TYP'),
                        row.get('METHOD_TYP'),
                        row.get('CLASS'),
                        row.get('SHORTNAME'),
                        row.get('LONG_COMMON_NAME')
                    ))
                except Exception as e:
                    print(f"Error inserting {row.get('LOINC_NUM')}: {e}")
            
            self.conn.commit()
        
        print("✅ LOINC data loaded successfully!")
    
    def search_test(self, test_name: str) -> List[Dict]:
        """Search for a test in LOINC database."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT loinc_code, component, common_name, class, 
                       reference_range_low, reference_range_high
                FROM loinc_tests
                WHERE component ILIKE %s 
                   OR common_name ILIKE %s
                LIMIT 10
            """, (f"%{test_name}%", f"%{test_name}%"))
            
            results = []
            for row in cur.fetchall():
                results.append({
                    "loinc_code": row[0],
                    "component": row[1],
                    "common_name": row[2],
                    "class": row[3],
                    "ref_range": f"{row[4]}-{row[5]}" if row[4] and row[5] else "N/A"
                })
            return results
    
    def close(self):
        self.conn.close()


# Example usage
if __name__ == "__main__":
    integrator = LOINCIntegrator()
    
    # Step 1: Create table
    integrator.create_loinc_table()
    
    # Step 2: Load LOINC data (download CSV first from loinc.org)
    # integrator.load_loinc_csv("path/to/Loinc.csv")
    
    # Step 3: Search for tests
    results = integrator.search_test("hemoglobin")
    for r in results:
        print(f"LOINC: {r['loinc_code']} - {r['common_name']}")
    
    integrator.close()
