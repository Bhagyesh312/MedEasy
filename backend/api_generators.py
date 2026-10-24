"""
Flask API endpoints for Generative AI features
Showcases creative content generation capabilities
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import traceback

from generators.diet_plan_generator import DietPlanGenerator
from generators.exercise_plan_generator import ExercisePlanGenerator
from generators.patient_education_generator import PatientEducationGenerator
from db import get_connection

# Create blueprint
gen_bp = Blueprint('generators', __name__, url_prefix='/api/generate')

# Initialize generators (lazy loading)
_diet_gen = None
_exercise_gen = None
_education_gen = None

def get_diet_generator():
    global _diet_gen
    if _diet_gen is None:
        _diet_gen = DietPlanGenerator()
    return _diet_gen

def get_exercise_generator():
    global _exercise_gen
    if _exercise_gen is None:
        _exercise_gen = ExercisePlanGenerator()
    return _exercise_gen

def get_education_generator():
    global _education_gen
    if _education_gen is None:
        _education_gen = PatientEducationGenerator()
    return _education_gen


def auth_required(f):
    """Simple auth decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # In production, verify JWT token
        return f(*args, **kwargs)
    return decorated


@gen_bp.route('/diet-plan', methods=['POST'])
@auth_required
def generate_diet_plan():
    """
    🎨 GENERATIVE AI: Create personalized diet plan
    
    Request:
    {
        "report_id": 123,
        "findings": [...],
        "patient_name": "John Doe",
        "dietary_preferences": "vegetarian",
        "duration_days": 7
    }
    
    Response:
    {
        "plan_title": "7-Day Recovery Diet Plan",
        "daily_plans": [...],
        "shopping_list": {...},
        "cooking_tips": [...],
        "generated_by": "GenAI"
    }
    """
    try:
        data = request.get_json()
        
        findings = data.get('findings', [])
        if not findings:
            return jsonify({'error': 'No findings provided'}), 400
        
        patient_name = data.get('patient_name', 'Patient')
        dietary_preferences = data.get('dietary_preferences', 'vegetarian')
        duration_days = data.get('duration_days', 7)
        
        # Generate diet plan using GenAI
        generator = get_diet_generator()
        plan = generator.generate_diet_plan(
            findings=findings,
            patient_name=patient_name,
            dietary_preferences=dietary_preferences,
            duration_days=duration_days
        )
        
        return jsonify({
            'success': True,
            'diet_plan': plan,
            'message': f'✨ Generated {duration_days}-day personalized diet plan using GenAI!'
        }), 200
        
    except Exception as e:
        print(f"Error generating diet plan: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate diet plan',
            'details': str(e)
        }), 500


@gen_bp.route('/exercise-plan', methods=['POST'])
@auth_required
def generate_exercise_plan():
    """
    🎨 GENERATIVE AI: Create personalized exercise routine
    
    Request:
    {
        "findings": [...],
        "fitness_level": "beginner",
        "goals": "improve cardiovascular health",
        "duration_weeks": 4
    }
    
    Response:
    {
        "plan_title": "4-Week Wellness Program",
        "weekly_plans": [...],
        "equipment_needed": [...],
        "safety_guidelines": [...]
    }
    """
    try:
        data = request.get_json()
        
        findings = data.get('findings', [])
        fitness_level = data.get('fitness_level', 'beginner')
        goals = data.get('goals', 'general wellness')
        duration_weeks = data.get('duration_weeks', 4)
        
        # Generate exercise plan using GenAI
        generator = get_exercise_generator()
        plan = generator.generate_exercise_plan(
            findings=findings,
            fitness_level=fitness_level,
            goals=goals,
            duration_weeks=duration_weeks
        )
        
        return jsonify({
            'success': True,
            'exercise_plan': plan,
            'message': f'✨ Generated {duration_weeks}-week personalized workout plan using GenAI!'
        }), 200
        
    except Exception as e:
        print(f"Error generating exercise plan: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate exercise plan',
            'details': str(e)
        }), 500


@gen_bp.route('/health-guide', methods=['POST'])
@auth_required
def generate_health_guide():
    """
    🎨 GENERATIVE AI: Create educational content about condition
    
    Request:
    {
        "condition": "anemia",
        "findings": [...],
        "audience": "patient"
    }
    
    Response:
    {
        "title": "Complete Guide to Understanding Anemia",
        "overview": {...},
        "causes": {...},
        "symptoms": {...},
        "treatment": {...},
        "faq": [...]
    }
    """
    try:
        data = request.get_json()
        
        condition = data.get('condition')
        if not condition:
            return jsonify({'error': 'Condition is required'}), 400
        
        findings = data.get('findings', [])
        audience = data.get('audience', 'patient')
        
        # Generate educational guide using GenAI
        generator = get_education_generator()
        guide = generator.generate_educational_guide(
            condition=condition,
            findings=findings,
            audience=audience
        )
        
        return jsonify({
            'success': True,
            'health_guide': guide,
            'message': f'✨ Generated comprehensive guide about {condition} using GenAI!'
        }), 200
        
    except Exception as e:
        print(f"Error generating health guide: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate health guide',
            'details': str(e)
        }), 500


@gen_bp.route('/health-tips', methods=['POST'])
@auth_required
def generate_health_tips():
    """
    🎨 GENERATIVE AI: Create daily health tips
    
    Request:
    {
        "findings": [...],
        "count": 10
    }
    
    Response:
    {
        "tips": [
            "Eat iron-rich foods like spinach...",
            "Take a 20-minute walk daily...",
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        findings = data.get('findings', [])
        count = data.get('count', 10)
        
        # Generate tips using GenAI
        generator = get_education_generator()
        tips = generator.generate_health_tips(findings=findings, count=count)
        
        return jsonify({
            'success': True,
            'tips': tips,
            'count': len(tips),
            'message': f'✨ Generated {len(tips)} personalized health tips using GenAI!'
        }), 200
        
    except Exception as e:
        print(f"Error generating tips: {e}")
        return jsonify({
            'error': 'Failed to generate tips',
            'details': str(e)
        }), 500


@gen_bp.route('/wellness-ideas', methods=['POST'])
@auth_required
def generate_wellness_ideas():
    """
    🎨 GENERATIVE AI: Creative wellness activity suggestions
    
    Pure creativity - generates novel ideas!
    """
    try:
        data = request.get_json()
        findings = data.get('findings', [])
        
        findings_text = ", ".join([
            f"{f.get('test_name')}: {f.get('status')}"
            for f in findings
        ])
        
        prompt = f"""You are a creative wellness coach AI. Generate 15 creative, fun wellness activities for someone with these lab results:
{findings_text}

Make each idea:
- Creative and engaging
- Easy to start
- Good for the condition
- Enjoyable, not a chore

Categories: Mental wellness, Physical activity, Social connection, Hobbies, Nutrition fun

Return as JSON:
{{
  "mental_wellness": ["idea 1", "idea 2", "idea 3"],
  "physical_activity": ["idea 1", "idea 2", "idea 3"],
  "social_connection": ["idea 1", "idea 2", "idea 3"],
  "hobbies": ["idea 1", "idea 2", "idea 3"],
  "nutrition_fun": ["idea 1", "idea 2", "idea 3"]
}}
"""
        
        from groq import Groq
        import json
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,  # Maximum creativity!
            max_tokens=1500
        )
        
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        
        ideas = json.loads(content.strip())
        
        return jsonify({
            'success': True,
            'wellness_ideas': ideas,
            'message': '✨ Generated creative wellness ideas using GenAI!'
        }), 200
        
    except Exception as e:
        print(f"Error generating ideas: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@gen_bp.route('/health', methods=['GET'])
def health_check():
    """Check if generator service is available"""
    return jsonify({
        'status': 'healthy',
        'generators_available': [
            'diet-plan',
            'exercise-plan',
            'health-guide',
            'health-tips',
            'wellness-ideas'
        ]
    }), 200
