"""
GenAI Feature: Patient Education Content Generator
Creates educational materials about health conditions
"""

from groq import Groq
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import json

load_dotenv()


class PatientEducationGenerator:
    """Generate educational content using GenAI"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
    
    def generate_educational_guide(
        self,
        condition: str,
        findings: List[Dict[str, Any]] = None,
        audience: str = "patient"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive educational content about a health condition.
        
        Pure GenAI - creates educational materials from scratch!
        """
        
        prompt = f"""You are a medical education AI. Create a comprehensive, easy-to-understand guide about: {condition}

AUDIENCE: {audience} (use simple language, avoid jargon)

GENERATE A COMPLETE EDUCATIONAL GUIDE with:

1. OVERVIEW
   - What is {condition}?
   - How common is it?
   - Who is at risk?

2. CAUSES & RISK FACTORS
   - What causes it?
   - Risk factors to know
   - Prevention tips

3. SYMPTOMS & SIGNS
   - Common symptoms
   - When to see a doctor
   - Warning signs

4. DIAGNOSIS
   - How is it diagnosed?
   - What tests are needed?
   - Understanding your results

5. TREATMENT OPTIONS
   - Medical treatments
   - Lifestyle changes
   - Home remedies
   - What to expect

6. LIVING WITH {condition}
   - Daily management tips
   - Diet recommendations
   - Exercise guidelines
   - Mental health support

7. FREQUENTLY ASKED QUESTIONS
   - Generate 10 common questions and answers

8. RESOURCES
   - When to seek help
   - Support groups
   - Further reading

BE CREATIVE! Write engaging, helpful content like a health blog post.
Use analogies, examples, and clear explanations.

Return as JSON:
{{
  "title": "Complete Guide to Understanding {condition}",
  "overview": {{
    "what_is_it": "...",
    "how_common": "...",
    "who_at_risk": "..."
  }},
  "causes": {{
    "main_causes": [...],
    "risk_factors": [...],
    "prevention_tips": [...]
  }},
  "symptoms": {{
    "common_symptoms": [...],
    "when_to_see_doctor": [...],
    "warning_signs": [...]
  }},
  "diagnosis": {{
    "how_diagnosed": "...",
    "tests_needed": [...],
    "understanding_results": "..."
  }},
  "treatment": {{
    "medical_options": [...],
    "lifestyle_changes": [...],
    "home_remedies": [...],
    "what_to_expect": "..."
  }},
  "living_with": {{
    "daily_tips": [...],
    "diet": [...],
    "exercise": [...],
    "mental_health": [...]
  }},
  "faq": [
    {{"question": "...", "answer": "..."}},
    ...
  ],
  "resources": {{
    "emergency_signs": [...],
    "support": [...],
    "further_reading": [...]
  }}
}}
"""
        
        for model in self.models:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a creative medical education writer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                
                result = self._parse_json(response.choices[0].message.content)
                result['generated_by'] = 'GenAI Education Generator'
                result['model'] = model
                result['condition'] = condition
                
                return result
                
            except Exception as e:
                print(f"Model {model} failed: {e}")
                continue
        
        raise Exception("All models failed")
    
    def generate_health_tips(
        self,
        findings: List[Dict[str, Any]],
        count: int = 10
    ) -> List[str]:
        """Generate daily health tips based on report"""
        
        findings_text = ", ".join([
            f"{f.get('test_name')}: {f.get('status')}"
            for f in findings
        ])
        
        prompt = f"""Generate {count} creative, actionable health tips for someone with these lab results:
{findings_text}

Make each tip:
- Specific and actionable
- Easy to implement
- Motivating and positive
- Based on medical findings

Return as JSON array of strings."""
        
        for model in self.models:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9,  # High creativity
                    max_tokens=800
                )
                
                content = response.choices[0].message.content
                return self._parse_json_array(content)
                
            except Exception as e:
                continue
        
        return []
    
    def _parse_json(self, text: str) -> dict:
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text.strip())
    
    def _parse_json_array(self, text: str) -> list:
        result = self._parse_json(text)
        if isinstance(result, dict):
            # Try to find array in dict
            for v in result.values():
                if isinstance(v, list):
                    return v
        return result if isinstance(result, list) else []
