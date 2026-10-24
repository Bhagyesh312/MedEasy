"""
GenAI Feature: Personalized Exercise Plan Generator
Creates custom workout routines based on health conditions
"""

from groq import Groq
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import json

load_dotenv()


class ExercisePlanGenerator:
    """Generate personalized exercise plans using GenAI"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
    
    def generate_exercise_plan(
        self,
        findings: List[Dict[str, Any]],
        fitness_level: str = "beginner",
        goals: str = "general wellness",
        duration_weeks: int = 4
    ) -> Dict[str, Any]:
        """
        Generate a personalized exercise plan.
        
        This is GENERATIVE AI - creates novel workout routines!
        """
        
        findings_text = self._format_findings(findings)
        
        prompt = f"""You are a fitness AI coach. Generate a detailed {duration_weeks}-week personalized exercise plan.

PROFILE:
Medical Status: {findings_text}
Fitness Level: {fitness_level}
Goals: {goals}

GENERATE A COMPLETE {duration_weeks}-WEEK WORKOUT PLAN:

For each week, create:
- Monday to Sunday detailed workout schedule
- Exercise descriptions with sets, reps, duration
- Intensity levels
- Rest days and active recovery
- Progressive overload strategy

For each exercise, include:
- Name and type (cardio, strength, flexibility)
- How to perform it (detailed steps)
- Duration or reps/sets
- Why it helps the medical condition
- Modifications for beginners/advanced
- Safety tips

BE CREATIVE! Invent actual workout routines with variety.

Return as JSON:
{{
  "plan_title": "4-Week Wellness Program",
  "fitness_level": "{fitness_level}",
  "weekly_plans": [
    {{
      "week": 1,
      "theme": "Foundation Building",
      "daily_workouts": {{
        "monday": {{
          "focus": "Cardio & Core",
          "exercises": [
            {{
              "name": "Brisk Walking",
              "type": "cardio",
              "duration": "20 minutes",
              "intensity": "moderate",
              "how_to": "...",
              "benefits": "Improves cardiovascular health, helps with...",
              "modifications": {{...}}
            }}
          ],
          "total_duration": "45 minutes",
          "calories_burned": "200-250"
        }},
        "tuesday": {{...}},
        ...
      }}
    }}
  ],
  "equipment_needed": [...],
  "safety_guidelines": [...],
  "progress_tracking": {{...}},
  "nutrition_tips": [...]
}}
"""
        
        for model in self.models:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a creative fitness AI that designs personalized workout plans."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=4000
                )
                
                result = self._parse_json(response.choices[0].message.content)
                result['generated_by'] = 'GenAI Exercise Plan Generator'
                result['model'] = model
                
                return result
                
            except Exception as e:
                print(f"Model {model} failed: {e}")
                continue
        
        raise Exception("All models failed")
    
    def _format_findings(self, findings: List[Dict]) -> str:
        result = []
        for f in findings:
            status = f.get('status', 'Unknown')
            if status != 'Normal':
                result.append(f"{f.get('test_name')}: {status}")
        return ", ".join(result) if result else "Healthy"
    
    def _parse_json(self, text: str) -> dict:
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text.strip())
