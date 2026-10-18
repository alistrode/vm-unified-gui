@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Workbench.ps1" %*
if errorlevel 1 (
  echo.
  echo Startup did not complete. The diagnostic message is shown above.
  pause
  exit /b 1
)
