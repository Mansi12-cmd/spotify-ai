@echo off

title Spotify AI

echo Starting Spotify AI...
echo.

cd /d "%~dp0"

docker compose up -d --build

if %errorlevel% neq 0 (
    echo.
    echo Failed to start Spotify AI.
    pause
    exit /b 1
)

echo.
echo Spotify AI is starting...
echo Waiting for services to initialize...

timeout /t 6 /nobreak >nul

echo Opening http://localhost:8501

start "" "http://localhost:8501"

echo.
echo Spotify AI is running.
pause