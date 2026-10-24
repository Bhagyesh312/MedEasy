"""
Quick test to verify USDA API key is working
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv('.env')

def test_usda_api():
    api_key = os.getenv('USDA_API_KEY')
    
    if not api_key:
        print("❌ USDA_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-5:]}")
    print("\nTesting USDA API with 'spinach' query...\n")
    
    url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
    params = {
        'api_key': api_key,
        'query': 'spinach',
        'pageSize': 3
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            foods = data.get('foods', [])
            
            print(f"✅ API Working! Found {len(foods)} results:\n")
            
            for i, food in enumerate(foods[:3], 1):
                desc = food.get('description', 'Unknown')
                print(f"{i}. {desc}")
                
                # Show first 3 nutrients
                nutrients = food.get('foodNutrients', [])
                for nutrient in nutrients[:3]:
                    name = nutrient.get('nutrientName', '')
                    value = nutrient.get('value', 0)
                    unit = nutrient.get('unitName', '')
                    if name and value:
                        print(f"   • {name}: {value} {unit}")
                print()
            
            return True
        else:
            print(f"❌ API Error: Status {response.status_code}")
            print(response.text[:200])
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_usda_api()
    if success:
        print("\n🎉 USDA API is ready to use in your project!")
    else:
        print("\n⚠️ There was an issue with the USDA API")
