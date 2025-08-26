# llm_service.py
import os
import json
import ast
from dotenv import load_dotenv
import google.generativeai as genai

# ----------------------
# Load .env from project root
# ----------------------
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(env_path)

# ----------------------
# Gemini API Key
# ----------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
assert GEMINI_API_KEY, "GEMINI_API_KEY not set in .env"

# Configure SDK
genai.configure(api_key=GEMINI_API_KEY)

# Model to use
MODEL_NAME = "gemini-1.5-flash"

# ----------------------
# System prompt to guide model output
# ----------------------
SYSTEM_PROMPT = """
You are an assistant that MUST output exactly one JSON object (no extra text).
The JSON object must have:
  - "action": string, one of: get_hotels, get_floors, get_rooms, get_iaq_data, get_presence_data, get_energy_summary
  - "parameters": object with keys required for the action.
If the user did not include required parameters, put them as null in parameters.
Return only the JSON object, nothing else.
Examples:
{"action":"get_iaq_data","parameters":{"room_id":103}}
{"action":"get_energy_summary","parameters":{"hotel_id":1,"subsystem":"ac","start_time":"2025-08-25T00:00","end_time":"2025-08-25T23:59","resolution":"1day"}}
"""

# ----------------------
# Helper: extract text from Gemini response
# ----------------------
def _extract_text_from_resp(resp):
    """
    Gemini API response text extract
    """
    if hasattr(resp, "text") and resp.text:
        return resp.text
    try:
        return resp.candidates[0].content[0].text
    except Exception:
        try:
            return resp.candidates[0].content.text
        except Exception:
            return str(resp)

# ----------------------
# Decide action based on user message
# ----------------------
def decide_action(user_message: str, max_attempts=2):
    """
    Sends SYSTEM_PROMPT + user_message to Gemini and expects JSON describing action + parameters.
    Returns dict: {"action": "...", "parameters": {...}}
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content([SYSTEM_PROMPT, user_message])
    except Exception as e:
        # Fallback for older/newer SDK versions
        try:
            resp = genai.generate_text(model=MODEL_NAME, prompt=SYSTEM_PROMPT + "\n\n" + user_message)
        except Exception as e2:
            raise RuntimeError(f"Failed to call Gemini: {e} / {e2}")

    text = _extract_text_from_resp(resp).strip()

    for attempt in range(max_attempts):
        # Try JSON parsing
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "action" in data:
                return data
        except json.JSONDecodeError:
            # Try ast.literal_eval for Python-style dicts
            try:
                data = ast.literal_eval(text)
                if isinstance(data, dict) and "action" in data:
                    return data
            except Exception:
                # Try extracting first { ... } block
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1 and end > start:
                    sub = text[start:end+1]
                    try:
                        data = json.loads(sub)
                        if isinstance(data, dict) and "action" in data:
                            return data
                    except Exception:
                        try:
                            data = ast.literal_eval(sub)
                            if isinstance(data, dict) and "action" in data:
                                return data
                        except Exception:
                            pass

        # Ask model again if parsing fails
        if attempt < max_attempts - 1:
            try:
                followup = "Return only the JSON object (no text). Previous response could not be parsed."
                resp = model.generate_content([SYSTEM_PROMPT, user_message, followup])
                text = _extract_text_from_resp(resp).strip()
                continue
            except Exception:
                break

    # Failed parsing after all attempts
    raise ValueError(f"Could not parse model output as JSON. Raw output:\n{text}")
