@echo off
cd /d "%~dp0"
echo Starting Image Processor (port 8001)...
start "Image Processor" cmd /k "cd /d %~dp0image_processor && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001"
timeout /t 3 /nobreak >nul
echo Starting web server and opening browser...
start "Web Server" cmd /k "cd /d %~dp0frontend\public && python -m http.server 8080"
timeout /t 2 /nobreak >nul
start http://localhost:8080/index-standalone.html
echo.
echo App opened in browser. Close the two terminal windows to stop the servers.
