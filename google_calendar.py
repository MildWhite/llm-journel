"""
Google Calendar Skill Implementation
Compatible with LLM frameworks that support skill/tools
"""

import re
import os
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union

def parse_natural_time(time_str: str, reference_time: Optional[datetime] = None) -> Dict[str, str]:
    """Parse natural language time to ISO 8601 format"""
    if reference_time is None:
        reference_time = datetime.now()

    dt = reference_time.replace(hour=9, minute=0, second=0, microsecond=0)
    time_str = time_str.lower().strip()
    duration = 60

    days_map = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }

    months_map = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }

    if "tomorrow" in time_str:
        dt = reference_time + timedelta(days=1)
    elif "today" in time_str:
        dt = reference_time
    elif "next week" in time_str:
        dt = reference_time + timedelta(days=7)
    elif "in " in time_str and "day" in time_str:
        match = re.search(r"in (\d+) day", time_str)
        if match:
            dt = reference_time + timedelta(days=int(match.group(1)))

    for day_name, day_num in days_map.items():
        if day_name in time_str:
            days_ahead = day_num - reference_time.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            if "next " + day_name in time_str:
                days_ahead += 7
            dt = reference_time + timedelta(days=days_ahead)
            break

    for month_name, month_num in months_map.items():
        if month_name in time_str:
            match = re.search(r"(\d{1,2})(?:st|nd|rd|th)?", time_str)
            if match:
                day = int(match.group(1))
                dt = dt.replace(month=month_num, day=day)
                if dt < reference_time:
                    dt = dt.replace(year=reference_time.year + 1)
            break

    match = re.search(r"(\d{1,2}):(\d{2})", time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        if "pm" in time_str and hour < 12:
            hour += 12
        elif "am" in time_str and hour == 12:
            hour = 0
        dt = dt.replace(hour=hour, minute=minute)
    else:
        hour = None
        if "9am" in time_str or "9 am" in time_str or "morning" in time_str:
            hour = 9
        elif "10am" in time_str or "10 am" in time_str:
            hour = 10
        elif "11am" in time_str or "11 am" in time_str:
            hour = 11
        elif "12pm" in time_str or "noon" in time_str:
            hour = 12
        elif "1pm" in time_str or "1 pm" in time_str or "afternoon" in time_str:
            hour = 13 if "1pm" in time_str or "1 pm" in time_str else 14
        elif "2pm" in time_str or "2 pm" in time_str:
            hour = 14
        elif "3pm" in time_str or "3 pm" in time_str:
            hour = 15
        elif "4pm" in time_str or "4 pm" in time_str:
            hour = 16
        elif "5pm" in time_str or "5 pm" in time_str or "evening" in time_str:
            hour = 17
        elif "6pm" in time_str or "6 pm" in time_str:
            hour = 18
        elif "7pm" in time_str or "7 pm" in time_str:
            hour = 19
        elif "8pm" in time_str or "8 pm" in time_str:
            hour = 20

        if hour is not None:
            dt = dt.replace(hour=hour, minute=0)

    if "30 min" in time_str or "30 minutes" in time_str or "half hour" in time_str:
        duration = 30
    elif "45 min" in time_str or "45 minutes" in time_str:
        duration = 45
    elif "1 hour" in time_str or "1hr" in time_str:
        duration = 60
    elif "2 hour" in time_str or "2hr" in time_str:
        duration = 120

    start_iso = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_iso = (dt + timedelta(minutes=duration)).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {"start": start_iso, "end": end_iso}

MOCK_MODE = False  # Set to False to test with real credentials


class MockResponse:
    def __init__(self, json_data: Dict, status_code: int = 200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error", response=self)


class GoogleCalendarSkill:
    """Skill for operating Google Calendar via API"""

    def __init__(self, credentials: Dict[str, str]):
        self.client_id = credentials.get("client_id")
        self.client_secret = credentials.get("client_secret")
        self.refresh_token = credentials.get("refresh_token")
        self.base_url = "https://www.googleapis.com/calendar/v3"
        self._access_token = None

    def _get_access_token(self) -> str:
        """Exchange refresh token for access token"""
        if MOCK_MODE:
            return "mock_access_token"

        if self._access_token:
            return self._access_token

        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }
        )
        response.raise_for_status()
        self._access_token = response.json()["access_token"]
        return self._access_token

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        if MOCK_MODE:
            return self._mock_response(method, endpoint, kwargs)

        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self._get_access_token()}"}
        response = requests.request(method, url, headers=headers, **kwargs)
        if response.status_code >= 400:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get("error", {}).get("message", "Unknown error")
            raise Exception(f"API Error {response.status_code}: {error_msg}")
        if response.status_code == 204 or not response.text:
            return {}
        return response.json()

    def _mock_response(self, method: str, endpoint: str, kwargs: Dict) -> Dict[str, Any]:
        if method == "POST" and "/events" in endpoint:
            event_id = f"mock_event_{datetime.now().timestamp()}"
            return {
                "id": event_id,
                "status": "confirmed",
                "htmlLink": f"https://calendar.google.com/event?eid={event_id}"
            }
        if method == "GET" and "/events" in endpoint:
            return {"items": [
                {"id": "1", "summary": "Mock Meeting", "start": {"dateTime": "2026-05-15T14:00:00Z"}},
                {"id": "2", "summary": "Mock Call", "start": {"dateTime": "2026-05-15T16:00:00Z"}}
            ]}
        if method == "POST" and "/freeBusy":
            return {"calendars": {"primary": {"busy": []}}}
        return {}

    def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """Create a new calendar event"""
        event = {
            "summary": summary,
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"}
        }
        if description:
            event["description"] = description
        if location:
            event["location"] = location
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        return self._request("POST", f"/calendars/{calendar_id}/events", json=event)

    def list_events(
        self,
        time_min: str,
        time_max: str,
        max_results: int = 50,
        calendar_id: str = "primary"
    ) -> List[Dict[str, Any]]:
        """List events in a time range"""
        params = {
            "timeMin": time_min,
            "timeMax": time_max,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime"
        }
        result = self._request("GET", f"/calendars/{calendar_id}/events", params=params)
        return result.get("items", [])

    def get_event(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """Get a specific event by ID"""
        return self._request("GET", f"/calendars/{calendar_id}/events/{event_id}")

    def update_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
        **updates
    ) -> Dict[str, Any]:
        """Update an existing event"""
        event = {}
        if "summary" in updates:
            event["summary"] = updates["summary"]
        if "description" in updates:
            event["description"] = updates["description"]
        if "location" in updates:
            event["location"] = updates["location"]
        if "start_time" in updates:
            event["start"] = {"dateTime": updates["start_time"], "timeZone": "UTC"}
        if "end_time" in updates:
            event["end"] = {"dateTime": updates["end_time"], "timeZone": "UTC"}

        return self._request("PATCH", f"/calendars/{calendar_id}/events/{event_id}", json=event)

    def delete_event(self, event_id: str, calendar_id: str = "primary") -> None:
        """Delete an event"""
        self._request("DELETE", f"/calendars/{calendar_id}/events/{event_id}")

    def check_availability(
        self,
        time_min: str,
        time_max: str,
        calendar_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Check free/busy times"""
        if calendar_ids is None:
            calendar_ids = ["primary"]

        body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [{"id": cid} for cid in calendar_ids]
        }
        return self._request("POST", "/freeBusy", json=body)


if __name__ == "__main__":
    import argparse
    import json

    credentials = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN")
    }

    if not all(credentials.values()):
        raise SystemExit(
            "Missing Google OAuth credentials. Set GOOGLE_CLIENT_ID, "
            "GOOGLE_CLIENT_SECRET, and GOOGLE_REFRESH_TOKEN."
        )

    calendar = GoogleCalendarSkill(credentials)
    parser = argparse.ArgumentParser(description="Google Calendar CLI")
    parser.add_argument("--action", choices=["create", "list", "update", "delete", "availability", "test"], required=True)
    parser.add_argument("--summary", help="Event title")
    parser.add_argument("--description", help="Event description")
    parser.add_argument("--start", help="Start time (ISO 8601)")
    parser.add_argument("--end", help="End time (ISO 8601)")
    parser.add_argument("--location", help="Event location")
    parser.add_argument("--attendees", help="Comma-separated emails")
    parser.add_argument("--event-id", help="Event ID for update/delete")
    parser.add_argument("--time-min", help="Time range start (ISO 8601)")
    parser.add_argument("--time-max", help="Time range end (ISO 8601)")
    args = parser.parse_args()

    if args.action == "test":
        print("=== Google Calendar Skill Test ===\n")
        event = calendar.create_event(summary="Test Event", start_time="2026-05-15T14:00:00Z", end_time="2026-05-15T15:00:00Z")
        print(f"Created: {event.get('id')}")
        events = calendar.list_events(time_min="2026-05-15T00:00:00Z", time_max="2026-05-15T23:59:59Z")
        print(f"Events: {len(events)}")
        print("Test passed!")
    elif args.action == "create":
        attendees = args.attendees.split(",") if args.attendees else None
        result = calendar.create_event(args.summary, args.start, args.end, args.description, args.location, attendees)
        print(json.dumps(result))
    elif args.action == "list":
        result = calendar.list_events(args.time_min, args.time_max)
        print(json.dumps(result))
    elif args.action == "update":
        result = calendar.update_event(args.event_id, summary=args.summary, description=args.description, location=args.location, start_time=args.start, end_time=args.end)
        print(json.dumps(result))
    elif args.action == "delete":
        calendar.delete_event(args.event_id)
        print(json.dumps({"status": "deleted", "event_id": args.event_id}))
    elif args.action == "availability":
        result = calendar.check_availability(args.time_min, args.time_max)
        print(json.dumps(result))
