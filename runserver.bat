@echo off
REM Development Server Startup Script
REM This ensures the correct settings are loaded

echo.
echo ============================================
echo Starting Django Development Server
echo Using: coaching_system.settings.local
echo ============================================
echo.

REM Activate virtual environment
call env\Scripts\activate.bat

REM Load local environment variables
if exist .env.local (
    for /f "delims== tokens=1,2" %%a in (.env.local) do (
        set %%a=%%b
    )
)

REM Set Django settings explicitly
set DJANGO_SETTINGS_MODULE=coaching_system.settings.local

REM Start the server
python manage.py runserver

pause
