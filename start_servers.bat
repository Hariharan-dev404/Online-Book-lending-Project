@echo off
echo ==============================================
echo   Starting PageLoft Servers
echo ==============================================

echo [1/2] Starting Django Backend API (Port 8000)...
start "Django Backend" cmd /k "cd backend && ..\venv\Scripts\python.exe manage.py runserver"

echo [2/2] Starting Frontend Web Server (Port 3000)...
start "Frontend Server" cmd /k "venv\Scripts\python.exe -m http.server 3000"

echo.
echo Both servers are now booting up in separate windows!
echo You can now open your browser to: http://localhost:3000
echo.
pause
