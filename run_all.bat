@echo off
setlocal enabledelayedexpansion

echo =======================================
echo   Running ALL Experiments + Analysis
echo =======================================

:: Create timestamped run folder
for /f "tokens=1-5 delims=/: " %%a in ("%date% %time%") do (
    set ts=%%a-%%b-%%c_%%d-%%e
)

set RUN_DIR=logs\runs\run_!ts!
mkdir "!RUN_DIR!"

echo Run folder created: !RUN_DIR!
echo.

:: Loop through all config files
for %%f in (config_*.json) do (
    set "name=%%~nf"
    echo ---------------------------------------
    echo Running %%f

    :: Create log file for this experiment
    set LOGFILE=!RUN_DIR!\!name!.log

    :: Run experiment and save output
    python attacker.py --config %%f > "!LOGFILE!" 2>&1

    echo Finished %%f
)

echo ---------------------------------------
echo Running analysis...
python analyze.py "!RUN_DIR!"

echo.
echo =======================================
echo    All experiments completed!
echo    Analysis finished!
echo.
echo    PDF report saved at:
echo       !RUN_DIR!\analysis_report.pdf
echo.
echo    Graphs and logs saved in:
echo       !RUN_DIR!
echo =======================================
echo.

echo Moving attempts*.log files into run folder (if any)...

if exist "attempts*.log" (
    move /Y "attempts*.log" "!RUN_DIR!\">nul
    echo attempts*.log files moved to !RUN_DIR!.
) else (
    echo No attempts*.log files found in project root.
)

pause





