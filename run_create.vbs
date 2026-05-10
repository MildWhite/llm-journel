Set WshShell = CreateObject("WScript.Shell")
Set objShell = CreateObject("Shell.Application")

' Run the python command
WshShell.Run "python ""C:\Users\Milo\.claw\skills\google-calendar\google_calendar.py"" --action create --summary ""Team Meeting"" --start ""2026-05-11T14:00:00Z"" --end ""2026-05-11T15:00:00Z"" --description ""Discuss the project""", 0, True

WScript.Echo "Meeting scheduled!"