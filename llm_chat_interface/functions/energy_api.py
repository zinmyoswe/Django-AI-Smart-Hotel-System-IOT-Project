# functions/energy_api.py
import os
import requests

# Backend base URL
BACKEND_BASE = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000/api")
TIMEOUT = 20  # request timeout

def get_energy_summary(hotel_id: int, subsystem: str = None, start_time: str = None,
                       end_time: str = None, resolution: str = "1hour"):
    """
    Hotel energy summary fetch function
    Returns dict with 'type' and 'content'
    """
    url = f"{BACKEND_BASE}/hotels/{hotel_id}/energy_summary/"
    params = {"resolution": resolution}
    if subsystem:
        params["subsystem"] = subsystem
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time

    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "")

        # CSV detection
        if "csv" in content_type or ("datetime" in r.text and "," in r.text):
            return {"type": "csv", "content": r.text}

        # JSON detection
        try:
            return {"type": "json", "content": r.json()}
        except ValueError:
            # fallback to plain text
            return {"type": "text", "content": r.text}

    except Exception as e:
        return {"type": "error", "content": str(e)}
