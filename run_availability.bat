@echo off
echo Checking availability...
python "C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py" --action availability --time-min "2026-05-11T09:00:00Z" --time-max "2026-05-11T17:00:00Z"
pause