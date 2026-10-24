"""
USDA FoodData Central Integration

For accurate nutrition data in diet plan generation.
Get API key (free): https://fdc.nal.usda.gov/api-key-signup.html
"""

import requests
import psycopg2
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()


class USDAFoodIntegrator:
    """Integrate USDA Food Database for nutrition data."""
    
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("USDA_API_KEY")
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
    
    def create_food_table(self):
        """Create food nutrition database table."""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS food_nutrition (
                    fdc_id INTEGER PRIMARY KEY,
                    food_name VARCHAR(255) NOT NULL,
                    food_category VARCHAR(100),
                    protein_g DECIMAL(10,2),
                    carbs_g DECIMAL(10,2),
                    fat_g DECIMAL(10,2),
                    calories_kcal INTEGER,
                    iron_mg DECIMAL(10,2),
                    calcium_mg DECIMAL(10,2),
                    vitamin_b12_mcg DECIMAL(10,2),
                    vitamin_d_mcg DECIMAL(10,2),
                    vitamin_c_mg DECIMAL(10,2),
                    fiber_g DECIMAL(10,2),
                    sodium_mg DECIMAL(10,2),
                    potassium_mg DECIMAL(10,2),
                    is_vegetarian BOOLEAN DEFAULT FALSE,
                    is_vegan BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_food_name 
                ON food_nutrition(food_name);
                
                CREATE INDEX IF NOT EXISTS idx_food_vegetarian 
                ON food_nutrition(is_vegetarian);
                
                -- Iron-rich foods
                CREATE INDEX IF NOT EXISTS idx_food_iron 
                ON food_nutrition(iron_mg DESC);
            """)
            self.conn.commit()
    
    def search_food(self, food_name: str) -> List[Dict]:
        """Search USDA food database."""
        url = f"{self.BASE_URL}/foods/search"
        params = {
            'api_key': self.api_key,
            'query': food_name,
            'pageSize': 10
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            foods = data.get('foods', [])
            
            results = []
            for food in foods:
                nutrients = {}
                for nutrient in food.get('foodNutrients', []):
                    name = nutrient.get('nutrientName', '')
                    value = nutrient.get('value', 0)
                    
                    if 'Protein' in name:
                        nutrients['protein_g'] = value
                    elif 'Carbohydrate' in name:
                        nutrients['carbs_g'] = value
                    elif 'Total lipid' in name or 'Fat' in name:
                        nutrients['fat_g'] = value
                    elif 'Energy' in name:
                        nutrients['calories_kcal'] = value
                    elif 'Iron' in name:
                        nutrients['iron_mg'] = value
                    elif 'Calcium' in name:
                        nutrients['calcium_mg'] = value
                    elif 'Vitamin B-12' in name:
                        nutrients['vitamin_b12_mcg'] = value
                    elif 'Vitamin D' in name:
                        nutrients['vitamin_d_mcg'] = value
                    elif 'Vitamin C' in name:
                        nutrients['vitamin_c_mg'] = value
                
                results.append({
                    'fdc_id': food.get('fdcId'),
                    'name': food.get('description'),
                    'category': food.get('foodCategory', ''),
                    'nutrients': nutrients
                })
            
            return results
        return []
    
    def get_iron_rich_foods(self, vegetarian: bool = True) -> List[Dict]:
        """Get top iron-rich foods from database."""
        with self.conn.cursor() as cur:
            if vegetarian:
                cur.execute("""
                    SELECT food_name, iron_mg, protein_g, calories_kcal
                    FROM food_nutrition
                    WHERE is_vegetarian = TRUE 
                      AND iron_mg > 0
                    ORDER BY iron_mg DESC
                    LIMIT 20
                """)
            else:
                cur.execute("""
                    SELECT food_name, iron_mg, protein_g, calories_kcal
                    FROM food_nutrition
                    WHERE iron_mg > 0
                    ORDER BY iron_mg DESC
                    LIMIT 20
                """)
            
            results = []
            for row in cur.fetchall():
                results.append({
                    'food': row[0],
                    'iron_mg': float(row[1]),
                    'protein_g': float(row[2]) if row[2] else 0,
                    'calories': int(row[3]) if row[3] else 0
                })
            return results
    
    def save_food_to_db(self, food_data: Dict):
        """Save food nutrition data to database."""
        with self.conn.cursor() as cur:
            nutrients = food_data.get('nutrients', {})
            cur.execute("""
                INSERT INTO food_nutrition 
                (fdc_id, food_name, food_category, protein_g, carbs_g, 
                 fat_g, calories_kcal, iron_mg, calcium_mg, vitamin_b12_mcg, 
                 vitamin_d_mcg, vitamin_c_mg)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (fdc_id) DO NOTHING
            """, (
                food_data['fdc_id'],
                food_data['name'],
                food_data['category'],
                nutrients.get('protein_g'),
                nutrients.get('carbs_g'),
                nutrients.get('fat_g'),
                nutrients.get('calories_kcal'),
                nutrients.get('iron_mg'),
                nutrients.get('calcium_mg'),
                nutrients.get('vitamin_b12_mcg'),
                nutrients.get('vitamin_d_mcg'),
                nutrients.get('vitamin_c_mg')
            ))
            self.conn.commit()
    
    def close(self):
        self.conn.close()


# Example usage
if __name__ == "__main__":
    # Get free API key from: https://fdc.nal.usda.gov/api-key-signup.html
    integrator = USDAFoodIntegrator(api_key="YOUR_API_KEY_HERE")
    
    # Create table
    integrator.create_food_table()
    
    # Search for spinach
    foods = integrator.search_food("spinach")
    for food in foods[:3]:
        print(f"\n{food['name']}")
        print(f"Iron: {food['nutrients'].get('iron_mg', 'N/A')} mg")
        print(f"Protein: {food['nutrients'].get('protein_g', 'N/A')} g")
        
        # Save to database
        integrator.save_food_to_db(food)
    
    # Get iron-rich vegetarian foods
    print("\n\nTop 5 Iron-Rich Vegetarian Foods:")
    iron_foods = integrator.get_iron_rich_foods(vegetarian=True)
    for food in iron_foods[:5]:
        print(f"- {food['food']}: {food['iron_mg']} mg iron")
    
    integrator.close()
