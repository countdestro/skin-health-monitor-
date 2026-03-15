@echo off
echo Opening AI Skin Health Monitor...
echo.
echo Option 1 - Next.js app (if already running): http://localhost:3005
echo Option 2 - Simple page: run RUN_SIMPLE_SERVER.bat then open http://localhost:8080/index-standalone.html
echo.
start http://localhost:3005
timeout /t 2 >nul
start http://127.0.0.1:3005
echo.
echo If nothing opened, copy-paste into Chrome or Edge: http://127.0.0.1:3005
echo Or run RUN_SIMPLE_SERVER.bat for a simpler page that always works.
pause
