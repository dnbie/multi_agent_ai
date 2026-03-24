"""
Reminder Agent - Set reminders and schedule task notifications
Stores reminders in data/reminders.json and triggers desktop notifications
"""

import os
import re
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .base_agent import BaseAgent, AgentResult


REMINDERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reminders.json")


class ReminderAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Reminder Agent",
            description="Set, list and delete reminders with desktop notifications"
        )
        self._ensure_storage()

    def get_capabilities(self) -> List[str]:
        return [
            "Set reminder at a specific time",
            "List all pending reminders",
            "Delete a reminder by ID",
            "Desktop notification when reminder fires",
            "Persistent storage in data/reminders.json",
        ]

    def execute(self, task: str, **kwargs) -> AgentResult:
        self._start_execution(task)
        lower = task.lower()
        try:
            if any(k in lower for k in ["list", "show", "all", "pending", "what reminder"]):
                result = self._list_reminders()
            elif any(k in lower for k in ["delete", "remove", "cancel"]):
                rid = kwargs.get("reminder_id") or self._extract_id(task)
                result = self._delete_reminder(rid)
            else:
                message = kwargs.get("message") or self._extract_message(task)
                remind_time = kwargs.get("remind_time") or self._extract_time(task)
                result = self._set_reminder(message, remind_time, task)
        except Exception as e:
            result = self._create_result(False, f"Reminder error: {str(e)}", error=str(e))

        self._end_execution(result)
        return result

    # ── actions ───────────────────────────────────────────────────────────────

    def _set_reminder(self, message: str, remind_time: Optional[datetime], original_task: str) -> AgentResult:
        if not message:
            return self._create_result(False, "Please specify what to be reminded about.",
                                       error="No reminder message")
        if remind_time is None:
            return self._create_result(
                False,
                "Please specify a time. Example: 'Remind me to call John at 6 pm'",
                error="No time found"
            )

        reminders = self._load()
        new_id = str(len(reminders) + 1)
        entry = {
            "id": new_id,
            "message": message,
            "remind_at": remind_time.isoformat(),
            "original_task": original_task,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
        }
        reminders.append(entry)
        self._save(reminders)

        # Fire background watcher
        self._schedule_notification(message, remind_time, new_id)

        time_str = remind_time.strftime("%I:%M %p on %d %b %Y")
        return self._create_result(True, f"Reminder set: '{message}' at {time_str}", data={"reminder": entry})

    def _list_reminders(self) -> AgentResult:
        reminders = [r for r in self._load() if r.get("status") == "pending"]
        if not reminders:
            return self._create_result(True, "No pending reminders.", data={"reminders": []})

        lines = [f"ID {r['id']}: {r['message']} — {r['remind_at'][:16]}" for r in reminders]
        return self._create_result(True, f"{len(reminders)} pending reminder(s):\n" + "\n".join(lines),
                                   data={"reminders": reminders})

    def _delete_reminder(self, rid: Optional[str]) -> AgentResult:
        reminders = self._load()
        before = len(reminders)
        reminders = [r for r in reminders if r["id"] != str(rid)]
        if len(reminders) == before:
            return self._create_result(False, f"Reminder ID {rid} not found.", error="Not found")
        self._save(reminders)
        return self._create_result(True, f"Reminder {rid} deleted.", data={"deleted_id": rid})

    # ── notification ──────────────────────────────────────────────────────────

    def _schedule_notification(self, message: str, remind_time: datetime, rid: str):
        def _notify():
            delay = (remind_time - datetime.now()).total_seconds()
            if delay > 0:
                time.sleep(delay)
            # Mark as fired in storage
            reminders = self._load()
            for r in reminders:
                if r["id"] == rid:
                    r["status"] = "fired"
            self._save(reminders)
            # Try system notification; fall back to print
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, message, "Reminder", 0x40)
            except Exception:
                try:
                    from plyer import notification
                    notification.notify(title="Reminder", message=message, timeout=10)
                except Exception:
                    print(f"[REMINDER] {message}")

        t = threading.Thread(target=_notify, daemon=True)
        t.start()

    # ── parsing ───────────────────────────────────────────────────────────────

    def _extract_message(self, text: str) -> str:
        patterns = [
            r'remind(?:er)?\s+(?:me\s+)?(?:to\s+)?(.+?)\s+at\s+\d',
            r'remind(?:er)?\s+(?:me\s+)?(?:to\s+)?(.+?)\s+in\s+\d',
            r'remind(?:er)?\s+(?:me\s+)?(?:to\s+)?(.+)',
            r'set\s+reminder\s+(?:for\s+)?(.+)',
        ]
        lower = text.lower()
        for pat in patterns:
            m = re.search(pat, lower)
            if m:
                msg = m.group(1).strip().rstrip("?.,")
                # strip trailing time phrases
                msg = re.sub(r'\s+at\s+\d.*$', '', msg)
                msg = re.sub(r'\s+in\s+\d.*$', '', msg)
                if len(msg) > 2:
                    return msg
        return text

    def _extract_time(self, text: str) -> Optional[datetime]:
        now = datetime.now()
        lower = text.lower()

        # "in X minutes/hours"
        m = re.search(r'in\s+(\d+)\s+(minute|hour|second)', lower)
        if m:
            val = int(m.group(1))
            unit = m.group(2)
            delta = timedelta(minutes=val) if "min" in unit else (
                timedelta(hours=val) if "hour" in unit else timedelta(seconds=val))
            return now + delta

        # "at HH:MM am/pm" or "at H pm"
        m = re.search(r'at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', lower)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2)) if m.group(2) else 0
            period = m.group(3)
            if period == "pm" and hour < 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
            target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            return target

        # "tomorrow at ..."
        if "tomorrow" in lower:
            m = re.search(r'tomorrow\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', lower)
            if m:
                hour = int(m.group(1))
                minute = int(m.group(2)) if m.group(2) else 0
                period = m.group(3)
                if period == "pm" and hour < 12:
                    hour += 12
                target = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
                return target

        return None

    def _extract_id(self, text: str) -> Optional[str]:
        m = re.search(r'\b(\d+)\b', text)
        return m.group(1) if m else None

    # ── storage ───────────────────────────────────────────────────────────────

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(REMINDERS_PATH), exist_ok=True)
        if not os.path.exists(REMINDERS_PATH):
            self._save([])

    def _load(self) -> List[Dict]:
        try:
            with open(REMINDERS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self, reminders: List[Dict]):
        with open(REMINDERS_PATH, "w", encoding="utf-8") as f:
            json.dump(reminders, f, indent=2)
