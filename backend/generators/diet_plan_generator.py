"""
GenAI Feature: Personalized Diet Plan Generator
Creates custom meal plans based on medical report findings
"""

from groq import Groq
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import json

load_dotenv()


class DietPlanGenerator:
    """Generate personalized diet plans using GenAI"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
    
    def generate_diet_plan(
        self,
        findings: List[Dict[str, Any]],
        patient_name: str = None,
        dietary_preferences: str = "vegetarian",
        duration_days: int = 7
    ) -> Dict[str, Any]:
        """
        Generate a personalized diet plan based on medical findings.
        
        This is PURE GENERATIVE AI - creates novel meal plans from scratch!
        """
        
        # Build detailed prompt
        findings_text = self._format_findings(findings)
        
        # Simpler, more reliable two-step approach
        prompt = f"""Create a detailed {duration_days}-day {dietary_preferences} diet plan for a patient with: {findings_text}

For EACH of the {duration_days} days, provide:
- Day theme
- Breakfast (meal name, 2-3 specific items, portion, why it helps)
- Mid-morning snack (item, why it helps)
- Lunch (meal name, 2-3 specific items, portion, why it helps)
- Evening snack (item, why it helps)  
- Dinner (meal name, 2-3 specific items, portion, why it helps)

At the end, provide:
- Shopping list (categorized: vegetables, fruits, grains, proteins, dairy, others)
- 3-4 cooking tips
- Foods to avoid

Be specific with actual meal names and ingredients. Make it practical and easy to follow."""
        
        # Generate with LLM
        for model in self.models:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a creative nutrition expert who designs personalized meal plans."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=3000
                )
                
                content = response.choices[0].message.content
                
                # Convert text response to structured JSON
                result = self._structure_diet_plan(content, duration_days)
                
                # Add metadata
                result['generated_by'] = 'GenAI Diet Plan Generator'
                result['model'] = model
                result['patient_name'] = patient_name
                result['dietary_preferences'] = dietary_preferences
                result['plan_title'] = f"{duration_days}-Day Personalized Recovery Diet"
                
                print(f"✅ Diet plan generated successfully with {model}")
                return result
                
            except Exception as e:
                print(f"Model {model} failed: {e}")
                continue
        
        raise Exception("All models failed to generate diet plan")
    
    def _format_findings(self, findings: List[Dict]) -> str:
        """Format findings for prompt"""
        result = []
        for f in findings:
            status = f.get('status', 'Unknown')
            if status != 'Normal':
                result.append(f"{f.get('test_name')}: {f.get('value')} {f.get('unit')} ({status})")
        return ", ".join(result) if result else "Generally healthy"
    
    def _structure_diet_plan(self, text: str, num_days: int) -> dict:
        """Convert AI text response to structured JSON"""
        import re
        
        # Create a simple structure that will always work
        result = {
            "daily_plans": [],
            "shopping_list": {
                "vegetables": [],
                "fruits": [],
                "grains": [],
                "proteins": [],
                "dairy": [],
                "others": []
            },
            "cooking_tips": [],
            "foods_to_avoid": [],
            "raw_content": text  # Include full AI response as fallback
        }
        
        # Try to extract structured info, but don't fail if we can't
        lines = text.split('\n')
        current_day = None
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to detect day headers
            day_match = re.search(r'(?:Day|DAY)\s*(\d+)', line, re.IGNORECASE)
            if day_match:
                day_num = int(day_match.group(1))
                if 1 <= day_num <= num_days:
                    current_day = {
                        "day": day_num,
                        "theme": line,
                        "breakfast": {"meal": "Loading...", "items": [], "portions": "", "benefits": ""},
                        "mid_morning": {"meal": "Loading...", "items": [], "benefits": ""},
                        "lunch": {"meal": "Loading...", "items": [], "portions": "", "benefits": ""},
                        "evening_snack": {"meal": "Loading...", "items": [], "benefits": ""},
                        "dinner": {"meal": "Loading...", "items": [], "portions": "", "benefits": ""}
                    }
                    result["daily_plans"].append(current_day)
            
            # Detect meal sections
            if re.search(r'breakfast', line, re.IGNORECASE):
                current_section = 'breakfast'
            elif re.search(r'mid.?morning|snack', line, re.IGNORECASE) and current_section != 'evening_snack':
                current_section = 'mid_morning'
            elif re.search(r'lunch', line, re.IGNORECASE):
                current_section = 'lunch'
            elif re.search(r'evening|afternoon', line, re.IGNORECASE):
                current_section = 'evening_snack'
            elif re.search(r'dinner', line, re.IGNORECASE):
                current_section = 'dinner'
            elif re.search(r'shopping|grocery', line, re.IGNORECASE):
                current_section = 'shopping'
            elif re.search(r'cooking|tips', line, re.IGNORECASE):
                current_section = 'cooking'
            elif re.search(r'avoid', line, re.IGNORECASE):
                current_section = 'avoid'
        
        # If we didn't extract any days, create a default structure with the raw content
        if not result["daily_plans"]:
            for day_num in range(1, num_days + 1):
                result["daily_plans"].append({
                    "day": day_num,
                    "theme": f"Day {day_num}",
                    "breakfast": {"meal": "See full plan below", "items": [], "portions": "", "benefits": ""},
                    "mid_morning": {"meal": "See full plan below", "items": [], "benefits": ""},
                    "lunch": {"meal": "See full plan below", "items": [], "portions": "", "benefits": ""},
                    "evening_snack": {"meal": "See full plan below", "items": [], "benefits": ""},
                    "dinner": {"meal": "See full plan below", "items": [], "portions": "", "benefits": ""}
                })
        
        return result
    
    def _parse_json(self, text: str) -> dict:
        """Extract JSON from response"""
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        text = text.strip()
        
        # Try to fix incomplete JSON - add closing braces if missing
        if text.count('{') > text.count('}'):
            text += '}' * (text.count('{') - text.count('}'))
        if text.count('[') > text.count(']'):
            text += ']' * (text.count('[') - text.count(']'))
        
        return json.loads(text)
