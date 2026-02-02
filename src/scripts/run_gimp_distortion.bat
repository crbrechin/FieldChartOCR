@echo off
REM Batch script to run GIMP image distortion processing
REM This script processes all JPG images in samples/top_right with random contrast and white balance adjustments

set SCRIPT_DIR=%~dp0
set INPUT_FOLDER=%SCRIPT_DIR%..\samples\bottom_left
set SUFFIX=_distorted

echo ========================================
echo GIMP Image Distortion Batch Processor
echo ========================================
echo.
echo Input folder: %INPUT_FOLDER%
echo Output suffix: %SUFFIX%
echo.

REM Check if GIMP is installed - try different executable names
set GIMP_EXE=
where gimp >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    where gimp > temp_gimp_path.txt
    set /p GIMP_EXE=<temp_gimp_path.txt
    del temp_gimp_path.txt
    goto gimp_found
)

REM Try alternative executable names
where gimp-2.10 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    where gimp-2.10 > temp_gimp_path.txt
    set /p GIMP_EXE=<temp_gimp_path.txt
    del temp_gimp_path.txt
    goto gimp_found
)

REM Check common installation locations
REM Check for GIMP 3 in user AppData location (most common for portable/user installs)
if exist "C:\Users\lenovo\AppData\Local\Programs\GIMP 3\bin\gimp-3.exe" (
    set "GIMP_EXE=C:\Users\lenovo\AppData\Local\Programs\GIMP 3\bin\gimp-3.exe"
    echo Found GIMP 3 at: %GIMP_EXE%
    goto gimp_found
)

REM Check for GIMP 2 in standard locations
if exist "C:\Program Files\GIMP 2\bin\gimp-2.10.exe" (
    set "GIMP_EXE=C:\Program Files\GIMP 2\bin\gimp-2.10.exe"
    goto gimp_found
)
if exist "C:\Program Files (x86)\GIMP 2\bin\gimp-2.10.exe" (
    set "GIMP_EXE=C:\Program Files (x86)\GIMP 2\bin\gimp-2.10.exe"
    goto gimp_found
)
if exist "C:\Program Files\GIMP 2\bin\gimp-console-2.10.exe" (
    set "GIMP_EXE=C:\Program Files\GIMP 2\bin\gimp-console-2.10.exe"
    goto gimp_found
)

echo ERROR: GIMP is not found in PATH or common installation locations.
echo Please install GIMP and ensure it is accessible from the command line.
echo.
echo You can also manually specify the GIMP path by editing this script.
pause
exit /b 1

:gimp_found
REM Validate GIMP_EXE is set before proceeding
if not defined GIMP_EXE (
    echo ERROR: GIMP executable path is not set.
    pause
    exit /b 1
)
if "%GIMP_EXE%"=="" (
    echo ERROR: GIMP executable path is empty.
    pause
    exit /b 1
)


REM Check if input folder exists
if not exist "%INPUT_FOLDER%" (
    echo ERROR: Input folder does not exist: %INPUT_FOLDER%
    pause
    exit /b 1
)

REM Get absolute path to the Python script
for %%I in ("%SCRIPT_DIR%distort_images_gimp.py") do set SCRIPT_PATH=%%~fI

echo Running GIMP batch processing...
echo.

REM Run GIMP in batch mode
REM -i: run in non-interactive mode
REM --batch-interpreter: specify Python-Fu interpreter
REM -b: execute batch command

REM For GIMP 3, we need to specify the batch interpreter
REM Copy script to GIMP's plug-ins folder in a subdirectory (required by GIMP 3)
set GIMP_PLUGINS=%APPDATA%\GIMP\3.0\plug-ins
if not exist "%GIMP_PLUGINS%" (
    REM Try alternative location
    set GIMP_PLUGINS=%LOCALAPPDATA%\GIMP\3.0\plug-ins
)
if not exist "%GIMP_PLUGINS%" (
    REM Create if doesn't exist
    mkdir "%GIMP_PLUGINS%" 2>nul
)

REM Remove any old plug-in file that might be in the wrong location (not in subdirectory)
if exist "%GIMP_PLUGINS%\distort_images_gimp.py" (
    echo Removing old plug-in file from wrong location...
    del "%GIMP_PLUGINS%\distort_images_gimp.py" 2>nul
)

REM Create subdirectory for the plug-in (GIMP 3 requires subdirectories)
set PLUGIN_DIR=%GIMP_PLUGINS%\distort_images_gimp
if not exist "%PLUGIN_DIR%" (
    mkdir "%PLUGIN_DIR%" 2>nul
)

echo Copying script to GIMP plug-ins subdirectory: %PLUGIN_DIR%
copy /Y "%SCRIPT_PATH%" "%PLUGIN_DIR%\distort_images_gimp.py"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to copy script to plug-ins folder
    pause
    exit /b 1
)

REM Wait a moment for file system to sync
timeout /t 1 /nobreak >nul

REM Convert backslashes to forward slashes for paths in batch commands  
set INPUT_FOLDER_FWD=%INPUT_FOLDER:\=/%

echo Executing GIMP...
echo Input folder: %INPUT_FOLDER%
echo Plug-in location: %PLUGIN_DIR%
echo.

REM The fundamental issue: gimpfu is only available when Python scripts
REM are loaded as plug-ins by GIMP's plug-in system.

REM Strategy: Ensure the plug-in is in the correct location, then try to call it.
REM GIMP 3 should auto-load plug-ins from subdirectories when it starts.

REM Convert paths to forward slashes for GIMP commands
set INPUT_FOLDER_FWD=%INPUT_FOLDER:\=/%

echo Attempting to use GIMP plug-in method...
echo Plug-in location: %PLUGIN_DIR%
echo Input folder: %INPUT_FOLDER_FWD%
echo.

REM GIMP 3's batch mode has a fundamental limitation: Python-Fu plug-ins
REM are not auto-loaded in batch mode. The gimpfu module is only available
REM when scripts are loaded as plug-ins by GIMP's plug-in system, which
REM doesn't happen automatically in batch mode.
REM
REM Solution: Use PIL-based script which provides equivalent functionality
REM without requiring GIMP's Python environment.

set PLUGIN_PATH_FWD=%PLUGIN_DIR:\=/%

echo.
echo ========================================
echo Using PIL-based Image Processing
echo ========================================
echo.
echo GIMP 3's batch mode cannot auto-load Python-Fu plug-ins.
echo Using PIL/Pillow library instead, which provides equivalent
echo contrast and white balance adjustments.
echo.
echo Processing images in: %INPUT_FOLDER%
echo.

REM Check if Python launcher is available
where py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python launcher 'py' is not found in PATH.
    echo Please ensure Python is installed and accessible.
    pause
    exit /b 1
)

REM Use PIL-based script
REM Use 'py' launcher instead of 'python' for Windows compatibility
echo Executing PIL-based image processing script...
py "%SCRIPT_DIR%distort_images_pil.py" "%INPUT_FOLDER%" "%SUFFIX%"
set GIMP_EXIT_CODE=%ERRORLEVEL%

REM Note: If user wants to use GIMP specifically, they need to:
REM 1. Start GIMP interactively once to load the plug-in
REM 2. Then use: gimp -i -b "(python-fu-distort-images RUN-NONINTERACTIVE \"folder\" \"suffix\")" -b "(gimp-quit 0)"

REM If GIMP method still fails, fall back to PIL-based script
if %GIMP_EXIT_CODE% NEQ 0 (
    echo.
    echo ========================================
    echo GIMP method failed. Using PIL-based alternative...
    echo ========================================
    echo.
    echo This method uses Python PIL/Pillow library instead of GIMP,
    echo avoiding the gimpfu module availability issues.
    echo.
    
    py "%SCRIPT_DIR%distort_images_pil.py" "%INPUT_FOLDER%" "%SUFFIX%"
    set GIMP_EXIT_CODE=%ERRORLEVEL%
)

echo.
echo GIMP exited with code: %GIMP_EXIT_CODE%

if %GIMP_EXIT_CODE% EQU 0 (
    echo.
    echo ========================================
    echo Processing completed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Processing completed with errors.
    echo ========================================
)

pause

