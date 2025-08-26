# functions/sensors_api.py
import os
import requests

# Backend base URL
BACKEND_BASE = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000/api")
TIMEOUT = 10

def _safe_get(url, params=None):
    """
    Safe GET request: return JSON, text, or error dict
    """
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            return r.text
    except Exception as e:
        return {"error": str(e), "url": url, "params": params}

# API functions
def get_hotels():
    return _safe_get(f"{BACKEND_BASE}/hotels/")

def get_floors(hotel_id: int):
    return _safe_get(f"{BACKEND_BASE}/hotels/{hotel_id}/floors/")

def get_rooms(floor_id: int):
    return _safe_get(f"{BACKEND_BASE}/floors/{floor_id}/rooms/")

def get_iaq_data(room_id: int):
    return _safe_get(f"{BACKEND_BASE}/rooms/{room_id}/data/iaq/")

def get_presence_data(room_id: int):
    return _safe_get(f"{BACKEND_BASE}/rooms/{room_id}/data/life_being/")
