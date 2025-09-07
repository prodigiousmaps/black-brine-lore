@echo off
setlocal ENABLEDELAYEDEXPANSION
title Black Brine Rebuild

REM 1) Move to script directory (repo root)
cd /d "%~dp0"

REM 2) Check Python
where py >nul 2>&1
if errorlevel 1 (
  echo Python launcher not found. Install from https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

REM 3) Ensure deps
echo.
echo === Installing/Checking dependencies ===
py -3.13 -m pip install --quiet --upgrade pip
py -3.13 -m pip install --quiet pyyaml rapidfuzz

REM 4) Dry-run refactor (creates report + patches)
echo.
echo === Running refactor (dry run) ===
py -3.13 bb_refactor.py
if errorlevel 1 goto :error

REM 5) Open the report
if exist "docs\refactor_report.html" (
  echo Opening report...
  start "" "docs\refactor_report.html"
) else (
  echo Report not found at docs\refactor_report.html
)

REM 6) Ask to apply patches
choice /M "Apply patches to files now"
if errorlevel 2 (
  echo Skipping patch apply.
) else (
  echo.
  echo === Applying patches ===
  py -3.13 bb_refactor.py --apply
  if errorlevel 1 goto :error
)

REM 7) Rebuild graph
echo.
echo === Building graph.json ===
py -3.13 indexer.py
if errorlevel 1 goto :error

REM 8) Commit and push (optional prompt)
choice /M "Commit and push changes to GitHub"
if errorlevel 2 (
  echo Skipping git push.
  goto :done
)

REM Ensure git exists
where git >nul 2>&1
if errorlevel 1 (
  echo Git not found. Install Git for Windows.
  goto :done
)

git add -A
git commit -m "chore: refactor+index (one-click rebuild)" || echo Nothing to commit.
git pull --rebase
git push

:done
echo.
echo ✅ Rebuild complete.
pause
exit /b 0

:error
echo.
echo ❌ Something failed. Check the console output above.
pause
exit /b 1
