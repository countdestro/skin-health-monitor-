@echo off
cd /d "%~dp0frontend\public"
echo.
echo Serving simple test page at http://localhost:8080
echo Open in browser: http://localhost:8080/index-standalone.html
echo.
echo Press Ctrl+C to stop the server.
echo.
start http://localhost:8080/index-standalone.html
python -m http.server 8080
