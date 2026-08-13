import json
import os
from datetime import datetime


class HistoryStore:
    def __init__(self, log_file="logs/history.json"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self.entries = self._load_from_file()

    def _load_from_file(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[!] Could not load history: {e}")
        return []

    def add_entry(self, request_dict, response_dict=None):
        entry = {
            "id": len(self.entries) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "request": request_dict,
            "response": response_dict,
        }
        self.entries.append(entry)
        self._save_to_file()
        return entry

    def get_all(self):
        return self.entries

    def get_by_id(self, entry_id):
        for entry in self.entries:
            if entry["id"] == entry_id:
                return entry
        return None

    def clear(self):
        self.entries = []
        self._save_to_file()

    def _save_to_file(self):
        try:
            with open(self.log_file, "w") as f:
                json.dump(self.entries, f, indent=2)
        except Exception as e:
            print(f"[!] Could not save history: {e}")


history = HistoryStore()