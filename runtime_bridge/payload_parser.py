import json

class PayloadParser:
    def parse(self, payload):
        # Extract JSON from [[ARCANE_REQUEST]] {"query": "...", "timestamp": ...}
        start = payload.find("[[ARCANE_REQUEST]]")
        if start == -1:
            return None
        json_str = payload[start + len("[[ARCANE_REQUEST]]"):].strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None