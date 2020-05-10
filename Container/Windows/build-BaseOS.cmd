@echo off
cls

if "%1" equ "" goto :HELP

if "%2" equ "" goto :HELP

if "%3" equ "" goto :HELP

SET SCRIPT_DIR=%~dp0
SET MY_REGISTRY=%1
SET OS_TYPE=%2
SET OS_VERSION=%3
SET PYTHON_VERSION=3.7.5

REM
REM Chagne x.y.z version to x.y
REM
for /f "tokens=1,2 delims=." %%i in ("%PYTHON_VERSION%") do SET PYTHON_VER_SHORT=%%i.%%j

SET TAG=%MY_REGISTRY%/openvino-container:%OS_TYPE%_%OS_VERSION%_cp%PYTHON_VER_SHORT%

docker inspect --type=image %TAG% > nul 2>&1

if %errorlevel% == 0 (
    echo Deleting image
    docker rmi -f %TAG%
)

REM
REM Server containers includes additional windows in Uri
REM docker pull mcr.microsoft.com/windows/servercore:tag
REM docker pull mcr.microsoft.com/windows:tag
REM
if "%OS_TYPE%" neq "windows" SET OS_TYPE=windows/%OS_TYPE%

echo.
echo     ____        _ __    __   _____ __             __ 
echo    / __ )__  __(_) /___/ /  / ___// /_____ ______/ /_
echo   / __  / / / / / / __  /   \__ \/ __/ __ `/ ___/ __/
echo  / /_/ / /_/ / / / /_/ /   ___/ / /_/ /_/ / /  / /_  
echo /_____/\__,_/_/_/\__,_/   /____/\__/\__,_/_/   \__/  
echo.
echo OS_TYPE    : %OS_TYPE%
echo OS_VERSION : %OS_VERSION%
echo TAG        : %TAG%
echo mcr.microsoft.com/%OS_TYPE%:%OS_VERSION%
REM
REM Build OS Base Image
REM
docker build --rm ^
    --isolation hyperv ^
    -f %SCRIPT_DIR%\BaseOS\Dockerfile ^
    --build-arg OS_TYPE=%OS_TYPE% ^
    --build-arg OS_VERSION=%OS_VERSION% ^
    --build-arg PYTHON_VERSION=%PYTHON_VERSION% -t %TAG% ^
    -m 4GB ^
    %SCRIPT_DIR% 

docker inspect --type=image %TAG% > nul 2>&1

if %errorlevel% == 1 (
    echo "Failed to create image"
    goto :EOF
)

echo ###############################################################################
echo  _       ___           __                  
echo ^| ^|     / (_)___  ____/ /___ _      _______
echo ^| ^| /^| / / / __ \/ __  / __ \ ^| /^| / / ___/
echo ^| ^|/ ^|/ / / / / / /_/ / /_/ / ^|/ ^|/ (__  ) 
echo ^|__/^|__/_/_/ /_/\__,_/\____/^|__/^|__/____/  
echo.                                            
echo Container built with OpenVINO Toolkit
echo Image Tag : %TAG%
echo. 

docker inspect --type=image %TAG% > nul 2>&1

if %errorlevel% == 1 (
    echo "Failed to create image"
    goto :EOF
)

echo ###############################################################################
echo CTLC+C to cancel docker push
echo ###############################################################################
timeout 10
echo Pushing Image : %TAG%
echo.
docker push %TAG%

goto :EOF

:HELP
echo =======================================
echo Please specify Windows Server Version and reistry
echo   Registry       : Your registry
echo   OS Type        : servercore or windows
echo   TAG            : ltsc2019, 1809, 1903
echo   Example ./%~nx0 myregistry servercore ltsc2019
echo =======================================
