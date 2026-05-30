from groq import Groq
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Fallback model chain — tries each in order if previous fails
MODELS = [
    "llama-3.3-70b-versatile",        # best free model on Groq
    "qwen/qwen3-32b",                  # fallback
    "meta-llama/llama-4-scout-17b-16e-instruct",  # lighter fallback
    "llama-3.1-8b-instant",           # last resort
]

SYSTEM_PROMPT = """You are a friendly and accurate medical report explainer.
You help patients understand their lab reports in plain, simple English.
You NEVER diagnose conditions. You NEVER recommend medications.
You always suggest consulting a doctor for values outside normal range."""

SYSTEM_PROMPT_HI = """आप एक मित्रवत और सटीक चिकित्सा रिपोर्ट व्याख्याकार हैं।
आप मरीजों को उनकी लैब रिपोर्ट सरल हिंदी में समझने में मदद करते हैं।
आप कभी भी बीमारी का निदान नहीं करते। आप कभी दवाइयां नहीं सुझाते।
सामान्य सीमा से बाहर मूल्यों के लिए हमेशा डॉक्टर से परामर्श करने का सुझाव दें।"""

SYSTEM_PROMPT_GU = """તમે એક મૈત્રીપૂર્ણ અને સચોટ તબીબી અહેવાલ સ્પષ્ટ કરનાર છો.
તમે દર્દીઓને તેમના લેબ રિપોર્ટ સરળ ગુજરાતીમાં સમજવામાં મદદ કરો છો.
તમે ક્યારેય રોગ નિદાન કરતા નથી. તમે ક્યારેય દવાઓ સૂચવતા નથી.
સામાન્ય સ્તરની બહારના મૂલ્યો માટે હંમેશા ડૉક્ટરની સલાહ લેવાનું સૂચન કરો."""

LANG_PROMPTS = {
    "en": SYSTEM_PROMPT,
    "hi": SYSTEM_PROMPT_HI,
    "gu": SYSTEM_PROMPT_GU,
}

LANG_INSTRUCTIONS = {
    "en": "Respond in English.",
    "hi": "सभी explanation और action हिंदी में लिखें।",
    "gu": "બધા explanation અને action ગુજરાતીમાં લખો.",
}


def _call_with_fallback(messages: list, retries=2) -> str:
    """Try each model in MODELS. Retry on rate limit. Raise if all fail."""
    last_error = None
    for model in MODELS:
        for attempt in range(retries):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=4096,
                )
                return response.choices[0].message.content
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "rate_limit" in err_str.lower():
                    if attempt == 0:
                        time.sleep(5)
                        continue
                    last_error = e
                    break  # try next model
                elif "503" in err_str or "unavailable" in err_str.lower():
                    if attempt == 0:
                        time.sleep(3)
                        continue
                    last_error = e
                    break
                elif "decommissioned" in err_str.lower() or "400" in err_str:
                    # Model removed — skip to next immediately, no retry
                    last_error = e
                    break
                else:
                    raise  # unexpected error — surface it
    raise Exception(f"All models failed. Last error: {last_error}")


def _parse_json(raw: str) -> list:
    """Clean markdown fences and parse JSON from model response."""
    raw = raw.strip()
    if raw.startswith("```"):
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("[") or part.startswith("{"):
                raw = part
                break
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    data = v
                    break
        if not isinstance(data, list):
            return []

        # Normalize each finding — fix flag, ensure strings
        normalized = []
        for item in data:
            status = str(item.get("status", "Unknown")).strip().capitalize()
            # flag can come back as bool, string "true"/"false", or status string
            raw_flag = item.get("flag", False)
            if isinstance(raw_flag, bool):
                flag = raw_flag
            elif isinstance(raw_flag, str):
                flag = raw_flag.lower() in ("true", "yes", "1", "high", "low", "critical")
            else:
                flag = bool(raw_flag)
            # Also infer flag from status if model got it wrong
            if status in ("High", "Low", "Critical"):
                flag = True
            elif status == "Normal":
                flag = False

            normalized.append({
                "test": str(item.get("test", "Unknown")),
                "value": str(item.get("value", "N/A")),
                "reference_range": str(item.get("reference_range", "Not specified")),
                "status": status,
                "explanation": str(item.get("explanation", "")),
                "action": str(item.get("action", "")),
                "flag": flag
            })
        return normalized
    except Exception:
        return []


def analyse_text_report(report_text: str, lang: str = "en") -> list:
    """Analyse extracted text from a digital PDF report."""
    report_text = report_text[:8000]
    sys_prompt = LANG_PROMPTS.get(lang, SYSTEM_PROMPT)
    lang_instr = LANG_INSTRUCTIONS.get(lang, "")

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"""Analyse this medical lab report and return ONLY a valid JSON array. {lang_instr}

Report:
{report_text}

Each item must have:
- "test": test name (string, keep in English)
- "value": result with unit (string)
- "reference_range": normal range from report, or "Not specified" (string)
- "status": one of "Normal", "High", "Low", "Critical", "Unknown" (always in English)
- "explanation": 2-3 sentences in the requested language explaining what this result means (string)
- "action": one sentence in the requested language on what the patient should do (string)
- "flag": true if needs attention, false if normal (boolean)

Return ONLY the JSON array. No markdown, no code blocks, no extra text."""}
    ]
    raw = _call_with_fallback(messages)
    return _parse_json(raw)


def analyse_scanned_report(pdf_path: str, lang: str = "en") -> list:
    from extractor import extract_text_plumber
    text = extract_text_plumber(pdf_path)
    if not text or len(text) < 50:
        return [{"test":"Unsupported Format","value":"N/A","reference_range":"N/A","status":"Unknown",
                 "explanation":"Scanned PDF — please use a digital PDF.","action":"Try a digital PDF.","flag":False}]
    return analyse_text_report(text, lang)


def generate_summary(findings: list, lang: str = "en") -> str:
    sys_prompt = LANG_PROMPTS.get(lang, SYSTEM_PROMPT)
    lang_instr = LANG_INSTRUCTIONS.get(lang, "")
    flagged = [f for f in findings if f.get("flag")]
    normal  = [f for f in findings if not f.get("flag")]
    flagged_str = "\n".join([f"- {f['test']}: {f['value']} ({f['status']})" for f in flagged]) or "None"
    normal_str  = "\n".join([f"- {f['test']}: {f['value']}" for f in normal]) or "None"

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"""Write a 3-4 sentence summary for a patient based on these lab results. {lang_instr}
Be reassuring but honest. End with a reminder to consult their doctor.

Flagged: {flagged_str}
Normal: {normal_str}

Write only the summary paragraph."""}
    ]
    return _call_with_fallback(messages).strip()


def generate_doctor_questions(findings: list, lang: str = "en") -> list:
    sys_prompt = LANG_PROMPTS.get(lang, SYSTEM_PROMPT)
    lang_instr = LANG_INSTRUCTIONS.get(lang, "")
    flagged = [f for f in findings if f.get("flag")]
    if not flagged:
        msgs = {"en": "Ask your doctor to confirm all values are within a healthy range for you.",
                "hi": "अपने डॉक्टर से पूछें कि क्या सभी मूल्य आपके लिए स्वस्थ सीमा में हैं।",
                "gu": "તમારા ડૉક્ટરને પૂછો કે શું બધા મૂલ્યો તમારા માટે સ્વસ્થ સ્તરમાં છે."}
        return [msgs.get(lang, msgs["en"])]

    flagged_str = "\n".join([f"- {f['test']}: {f['value']} ({f['status']})" for f in flagged])
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"""A patient has these abnormal lab values:
{flagged_str}

Generate 4-5 specific questions the patient should ask their doctor. {lang_instr}
Return ONLY a JSON array of strings. No other text."""}
    ]
    raw = _call_with_fallback(messages).strip()
    if raw.startswith("```"):
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("["):
                raw = part
                break
    try:
        return json.loads(raw)
    except Exception:
        return ["Please discuss your abnormal values with your doctor."]


def compare_reports(findings_a: list, findings_b: list, lang: str = "en") -> list:
    """Compare two sets of findings and return a list of changes."""
    sys_prompt = LANG_PROMPTS.get(lang, SYSTEM_PROMPT)
    lang_instr = LANG_INSTRUCTIONS.get(lang, "")

    def fmt(findings):
        return "\n".join([f"- {f['test']}: {f['value']} ({f['status']})" for f in findings])

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"""Compare these two medical lab reports and identify what changed. {lang_instr}

Report A (older):
{fmt(findings_a)}

Report B (newer):
{fmt(findings_b)}

Return ONLY a JSON array. Each item:
- "test": test name (string, in English)
- "old_value": value from Report A (string)
- "new_value": value from Report B (string)
- "old_status": status from A (string)
- "new_status": status from B (string)
- "change": "improved", "worsened", "stable", or "new" (string)
- "note": 1-2 sentence explanation of what this change means in the requested language (string)

Only include tests that appear in both reports or are new in B.
Return ONLY the JSON array."""}
    ]
    raw = _call_with_fallback(messages).strip()
    if raw.startswith("```"):
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("["):
                raw = part
                break
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []
