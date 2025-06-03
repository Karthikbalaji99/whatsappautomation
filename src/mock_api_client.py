import os
import time
import logging
import requests
from typing import List, Dict

MOCK_API_BASE = os.getenv("MOCK_API_BASE", "http://localhost:8000") 

class MockAPIClient:
    def __init__(self):
        self.base_url = MOCK_API_BASE.rstrip("/")
        try:
            # Quick check of server: expect 404 for invalid ID 
            resp = requests.get(f"{self.base_url}/mock/status/invalid_id", timeout=2)
            self.is_connected = (resp.status_code == 404)
        except Exception as e:
            logging.error(f"Failed to reach mock API server: {e}")
            self.is_connected = False

    def send_message(self, to_phone: str, message: str) -> Dict:
 
        try:
            to_str = str(to_phone)
            if not to_str.startswith("+"):
                to_str = "+" + to_str # I did this check because during the initial testing, the phone numbers were not in the correct format

            payload = {"to": to_str, "body": message}
            print("DEBUG: JSON payload →", payload)
            r = requests.post(f"{self.base_url}/mock/send", json=payload, timeout=5)
            r.raise_for_status()
            data = r.json()
            return {
                "status": data.get("status", "queued"),
                "message_id": data.get("message_id"),
                "error": None
            }
        except requests.exceptions.HTTPError as e:
            if r.status_code == 422:
                logging.error(f"Malformed payload for {to_phone}: {r.text}")
                return {"status": "invalid_payload", "message_id": None, "error": r.text}
            logging.error(f"MockAPI HTTP error sending to {to_phone}: {e}")
            return {"status": "failed", "message_id": None, "error": str(e)}
        except Exception as e:
            logging.error(f"MockAPI error sending to {to_phone}: {e}")
            return {"status": "failed", "message_id": None, "error": str(e)}

    def get_message_status(self, message_id: str) -> str:
        try:
            r = requests.get(f"{self.base_url}/mock/status/{message_id}", timeout=5)
            r.raise_for_status()
            return r.json().get("status", "unknown")
        except Exception as e:
            logging.error(f"MockAPI error fetching status {message_id}: {e}")
            return "unknown"

    def get_reply(self, message_id: str) -> Dict:
        try:
            r = requests.get(f"{self.base_url}/mock/reply/{message_id}", timeout=5)
            r.raise_for_status()
            data = r.json()
            return {"reply": data.get("reply"), "timestamp": data.get("timestamp")}
        except Exception as e:
            logging.error(f"MockAPI error fetching reply {message_id}: {e}")
            return {"reply": None, "timestamp": None}

    def send_bulk_messages(self, leads_data: List[Dict], message_templates: Dict) -> List[Dict]:
        results = []
        for lead in leads_data:
            try:
                templates = message_templates.get(lead["interest_area"], message_templates.get("default", []))
                import random
                selected = random.choice(templates)
                personalized = selected.format(name=lead["name"])
                res = self.send_message(lead["phone"], personalized)
                res.update({
                    "name": lead["name"],
                    "phone": lead["phone"],
                    "message": personalized,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                results.append(res)
                time.sleep(0.5)
            except Exception as e:
                logging.error(f"Error preparing lead {lead['name']}: {e}")
                results.append({
                    "name": lead["name"],
                    "phone": lead["phone"],
                    "message": "",
                    "status": "failed",
                    "message_id": None,
                    "error": str(e),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
        return results
