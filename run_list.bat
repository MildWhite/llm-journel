@echo off
echo Listing today's events...
python "C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py" --action list --time-min "2026-05-10T00:00:00Z" --time-max "2026-05-10T23:59:59Z"
pause