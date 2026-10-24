# Medical Datasets Integration for MedEasy AI 2.0

This folder contains integrations for external medical datasets to enhance the project.

---

## 📚 Available Datasets

### 1. **LOINC Database** - Lab Test Standards
- **File:** `integrate_loinc.py`
- **Source:** https://loinc.org
- **Size:** 90,000+ lab test codes
- **License:** Free (requires registration)
- **Setup:**
  1. Register at https://loinc.org/downloads/
  2. Download `Loinc.csv`
  3. Run: `python integrate_loinc.py`

### 2. **RxNorm** - Medication Database
- **File:** `integrate_rxnorm.py`
- **Source:** https://rxnav.nlm.nih.gov/
- **Size:** 400,000+ medications
- **License:** Public domain (U.S. NLM)
- **Setup:**
  - Uses REST API (no download needed)
  - Run: `python integrate_rxnorm.py`

### 3. **USDA FoodData Central** - Nutrition Database
- **File:** `integrate_usda_food.py`
- **Source:** https://fdc.nal.usda.gov/
- **Size:** 350,000+ foods
- **License:** Public domain (USDA)
- **Setup:**
  1. Get API key: https://fdc.nal.usda.gov/api-key-signup.html
  2. Add to `.env`: `USDA_API_KEY=your_key_here`
  3. Run: `python integrate_usda_food.py`

### 4. **WHO Reference Ranges** - International Standards
- **File:** `who_reference_ranges.json`
- **Source:** WHO Guidelines (manually curated)
- **Size:** 10+ common tests
- **License:** Public domain
- **Usage:** Already included, ready to use

### 5. **Medical Conditions Database**
- **File:** `medical_conditions.json`
- **Source:** Medical literature (manually curated)
- **Size:** 7 common conditions
- **License:** Open for educational use
- **Usage:** Already included, ready to use

---

## 🚀 Quick Start

### Option 1: Use Static Datasets Only (No External APIs)
```bash
# WHO reference ranges and conditions are ready
# Just load them in your code:
import json

with open('data/who_reference_ranges.json') as f:
    who_ranges = json.load(f)

with open('data/medical_conditions.json') as f:
    conditions = json.load(f)
```

### Option 2: Integrate External Databases
```bash
cd backend/data

# 1. LOINC (requires CSV download)
python integrate_loinc.py

# 2. RxNorm (API-based, instant)
python integrate_rxnorm.py

# 3. USDA Food (requires API key)
python integrate_usda_food.py
```

---

## 📊 Database Schema Extensions

These scripts will create new tables in your PostgreSQL database:

```sql
-- Created by integrate_loinc.py
loinc_tests (
    loinc_code, component, property, system,
    class, common_name, units, reference_range_low, 
    reference_range_high
)

-- Created by integrate_rxnorm.py
medications (
    rxcui, drug_name, generic_name, drug_class,
    indication, common_uses, related_conditions
)

-- Created by integrate_usda_food.py
food_nutrition (
    fdc_id, food_name, food_category,
    protein_g, carbs_g, fat_g, calories_kcal,
    iron_mg, calcium_mg, vitamin_b12_mcg,
    vitamin_d_mcg, vitamin_c_mg, fiber_g,
    is_vegetarian, is_vegan
)
```

---

## 🎯 How These Datasets Improve Your Project

### Current Limitation → Solution

**1. Test Name Variations**
- **Current:** Manual 200-entry dictionary
- **With LOINC:** 90,000+ standardized codes
- **Benefit:** Handle ANY lab report from ANY lab

**2. Medication Suggestions**
- **Current:** None
- **With RxNorm:** "Low iron? Try Ferrous Sulfate"
- **Benefit:** Actionable recommendations

**3. Diet Plan Nutrition**
- **Current:** AI generates generic meal ideas
- **With USDA:** "Spinach (100g) = 2.7mg iron, 23 calories"
- **Benefit:** Scientifically accurate nutrition

**4. Reference Ranges**
- **Current:** Extracted from PDF (unreliable)
- **With WHO:** International gold standards
- **Benefit:** Consistent interpretations

**5. Condition Diagnosis**
- **Current:** AI guesses based on LLM training
- **With Conditions DB:** "Low Hb + Low B12 + High MCV = Megaloblastic Anemia"
- **Benefit:** Pattern-based diagnosis

---

## 💡 Integration Priority

**Start with these (easiest first):**

1. ✅ **WHO Reference Ranges** - Already done, just use it
2. ✅ **Medical Conditions** - Already done, just use it
3. 🔵 **RxNorm** - Easy (API-based, no download)
4. 🟡 **USDA Food** - Medium (API key needed)
5. 🟠 **LOINC** - Hard (large CSV, requires registration)

---

## 📝 Example: Using WHO Reference Ranges

```python
# In your analyser.py or analyser_v2.py

import json

# Load WHO ranges
with open('data/who_reference_ranges.json') as f:
    who_ranges = json.load(f)

def check_anemia(hemoglobin_value, gender):
    """Check if hemoglobin indicates anemia using WHO standards."""
    hb_data = who_ranges['hemoglobin']
    
    if gender == 'male':
        ref_range = hb_data['who_reference_ranges']['adult_male']
    else:
        ref_range = hb_data['who_reference_ranges']['adult_female']
    
    if hemoglobin_value < ref_range['low']:
        # Check severity
        anemia_thresholds = hb_data['anemia_thresholds']
        if hemoglobin_value < anemia_thresholds['severe']['high']:
            return 'severe_anemia'
        elif hemoglobin_value < anemia_thresholds['moderate']['high']:
            return 'moderate_anemia'
        else:
            return 'mild_anemia'
    else:
        return 'normal'

# Usage
result = check_anemia(10.5, 'female')  # → 'mild_anemia'
```

---

## 📝 Example: Using Medical Conditions

```python
# In your generators/diet_plan_generator.py

import json

# Load conditions
with open('data/medical_conditions.json') as f:
    conditions = json.load(f)

def get_dietary_advice(condition_name):
    """Get dietary recommendations for a condition."""
    condition = conditions.get(condition_name)
    
    if condition:
        return {
            'foods': condition['dietary_recommendations'],
            'symptoms': condition['symptoms'],
            'supplements': condition.get('supplements', [])
        }
    return None

# Usage
advice = get_dietary_advice('iron_deficiency_anemia')
# Returns iron-rich foods, symptoms, supplements
```

---

## 🔐 Environment Variables Needed

Add to your `backend/.env`:

```bash
# USDA Food Database (optional)
USDA_API_KEY=your_api_key_here

# Your existing variables
GROQ_API_KEY=...
DB_HOST=localhost
...
```

---

## 📊 Dataset Comparison

| Dataset | Size | Type | Setup | API Key | Cost |
|---------|------|------|-------|---------|------|
| **WHO Ranges** | 10 tests | JSON file | ✅ Done | ❌ No | Free |
| **Medical Conditions** | 7 conditions | JSON file | ✅ Done | ❌ No | Free |
| **RxNorm** | 400K drugs | REST API | 5 min | ❌ No | Free |
| **USDA Food** | 350K foods | REST API | 10 min | ✅ Yes | Free |
| **LOINC** | 90K tests | CSV file | 30 min | ❌ No | Free |

---

## 🎓 Learning Resources

- **LOINC:** https://loinc.org/get-started/
- **RxNorm:** https://www.nlm.nih.gov/research/umls/rxnorm/docs/index.html
- **USDA FoodData:** https://fdc.nal.usda.gov/api-guide.html
- **WHO Guidelines:** https://www.who.int/health-topics/

---

## ⚠️ Important Notes

1. **LOINC Registration:** Required but free for non-commercial use
2. **USDA Rate Limits:** 1000 requests/hour on free tier
3. **Data Updates:** USDA/RxNorm update regularly, re-run scripts periodically
4. **Privacy:** These are reference databases, no patient data
5. **Licensing:** All sources are public domain or freely licensed for educational use

---

**Last Updated:** 2026-10-11  
**Version:** 2.0.0
