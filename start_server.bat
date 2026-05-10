@echo off
echo Starting Calendar HTTP Server...
echo.
echo Once started, the server will be at: http://localhost:8765
echo.
echo To create a meeting, visit:
echo http://localhost:8765/create?summary=Meeting&start=2026-05-11T14:00:00Z&end=2026-05-11T15:00:00Z
echo.
python "C:\Users\Milo\.claw\skills\google-calendar\run_http_server.py"
pause