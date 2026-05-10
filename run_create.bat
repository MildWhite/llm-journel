@echo off
echo Creating Google Calendar event...
python "C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py" --action create --summary "Team Meeting" --start "2026-05-11T14:00:00Z" --end "2026-05-11T15:00:00Z" --description "Discuss the project"
pause