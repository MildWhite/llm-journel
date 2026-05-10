---
name: google-calendar
description: Schedule, list, update, and delete Google Calendar events. Check availability for meeting slots.
argument-hint: [schedule <event> | list events | check availability | create meeting | delete event]
allowed-tools: Bash
---

# Google Calendar Skill

## INSTRUCTIONS

Use the Bash tool to run Python commands directly. The script is at:
`C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py`

Credentials must be provided via environment variables.

## Available Actions

### Create event
```
python "C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py" --action create --summary "Meeting Title" --start "2026-05-15T14:00:00Z" --end "2026-05-15T15:00:00Z" --description "Optional description"
```

### List events
```
python "C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py" --action list --time-min "2026-05-15T00:00:00Z" --time-max "2026-05-15T23:59:59Z"
```

### Check availability
```
python "C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py" --action availability --time-min "2026-05-15T09:00:00Z" --time-max "2026-05-15T17:00:00Z"
```

### Update event
```
python "C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py" --action update --event-id EVENT_ID --summary "New Title"
```

### Delete event
```
python "C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py" --action delete --event-id EVENT_ID
```

## Time Calculation

For natural language like "tomorrow at 2pm":
- Tomorrow = 2026-05-11 (today is May 10, 2026)
- 2pm = 14:00 in 24-hour format
- Start: 2026-05-11T14:00:00Z
- End: 2026-05-11T15:00:00Z (1 hour default)

Just calculate reasonable times and proceed. The user can adjust if needed.

## Output format

All operations return JSON. Parse and present to user:
- create: Shows event ID and google calendar link
- list: Shows array of events with summary and start time
- availability: Shows busy time slots
- update: Shows updated event
- delete: Confirms deletion

## Credentials

Set these environment variables before running:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`

## Example Workflow

User: "Schedule meeting tomorrow at 2pm"

**STEP 1 - Use the Bash tool to run this exact command:**
```
python "C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py" --action create --summary "Project Discussion" --start "2026-05-11T14:00:00Z" --end "2026-05-11T15:00:00Z"
```

**STEP 2 - Parse the JSON output**
- Extract "id" from the response
- Extract "htmlLink" from the response

**STEP 3 - Present to user**
- "Created event! ID: xyz123"
- "View at: https://www.google.com/calendar/event?eid=..."
