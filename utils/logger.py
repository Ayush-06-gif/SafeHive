"""
Session Logger — Manages scenario logging and state tracking.

1. Automatically creates a sessions/ directory.
2. Assigns a unique 8-character UUID to each session.
3. Logs every event with a timestamp.
4. Saves a complete session summary as JSON at the end.
"""

import json
import os
import uuid
from datetime import datetime, timezone


# Ensure sessions directory exists relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)


class SessionLogger:
    """Tracks and logs a single conversation simulation session."""

    def __init__(self, user_input: str):
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = self._get_timestamp()
        self.end_time = None
        self.user_input = user_input

        # Summary tracking fields
        self.final_status = "in_progress"
        self.vendors_tried = []
        self.vendors_blocked = []
        self.total_turns = 0
        self.threats_detected = 0

        # Detailed event logs
        self.logs = []

        self.log("USER_INPUT", {"input": user_input})

    def _get_timestamp(self) -> str:
        """Return ISO 8601 formatted UTC timestamp."""
        return datetime.now(timezone.utc).isoformat()

    def log(self, event_type: str, data: dict):
        """
        Log an event with a timestamp.

        Expected event_types:
        - USER_INPUT
        - VENDOR_SELECTED
        - TURN
        - BLOCKED
        - ALTERNATIVE_VENDOR
        - ORDER_COMPLETE
        - SESSION_END
        """
        event = {
            "timestamp": self._get_timestamp(),
            "event_type": event_type,
            "data": data,
        }
        self.logs.append(event)

        # Automatically update summary stats based on event types
        if event_type == "VENDOR_SELECTED" or event_type == "ALTERNATIVE_VENDOR":
            vendor = data.get("vendor_name")
            if vendor and vendor not in self.vendors_tried:
                self.vendors_tried.append(vendor)

        elif event_type == "BLOCKED":
            vendor = data.get("vendor_name")
            if vendor and vendor not in self.vendors_blocked:
                self.vendors_blocked.append(vendor)

        elif event_type == "TURN":
            self.total_turns += 1
            guard_result = data.get("guard_result", {})
            if not guard_result.get("safe", True):
                self.threats_detected += len(guard_result.get("threats", []))

    def save(self, final_status: str) -> dict:
        """
        Finalize the session, write to disk, and return the summary object.
        """
        self.end_time = self._get_timestamp()
        self.final_status = final_status
        
        self.log("SESSION_END", {"final_status": final_status})

        session_summary = {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "user_input": self.user_input,
            "final_status": self.final_status,
            "vendors_tried": self.vendors_tried,
            "vendors_blocked": self.vendors_blocked,
            "total_turns": self.total_turns,
            "threats_detected": self.threats_detected,
            "logs": self.logs,
        }

        # Save to file
        file_path = os.path.join(SESSIONS_DIR, f"{self.session_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session_summary, f, indent=2, ensure_ascii=False)

        return session_summary
