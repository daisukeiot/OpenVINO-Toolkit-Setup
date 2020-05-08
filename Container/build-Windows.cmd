@echo off

if "%1" equ "" goto :HELP

if "%2" equ "" goto :HELP

if "%3" equ "" goto :HELP

set SCRIPT_DIR=%~dp0
set OS_TYPE=%1
set OS_VERSION=%2
set MY_REGISTRY=%3
set PYTHON_VERSION=3.7.5

set TAG=%MY_REGISTRY%/openvino-container:%OS_TYPE%_%OS_VERSION%_ov%OPENVINO_VER%_cp%PYTHON_VERSION%

echo ""
echo "    ____        _ __    __   _____ __             __ "
echo "   / __ )__  __(_) /___/ /  / ___// /_____ ______/ /_"
echo "  / __  / / / / / / __  /   \__ \/ __/ __ `/ ___/ __/"
echo " / /_/ / /_/ / / / /_/ /   ___/ / /_/ /_/ / /  / /_  "
echo "/_____/\__,_/_/_/\__,_/   /____/\__/\__,_/_/   \__/  "
echo ""

REM
REM Build Ubuntu Base Image
REM
docker build --rm --isolation hyperv -f %SCRIPT_DIR%\Windows\Dockerfile --build-arg OS_TYPE=%OS_TYPE% --build-arg OS_VERSION=%OS_VERSION% --build-arg PYTHON_VERSION=%PYTHON_VERSION% -t %TAG% -m 4GB %SCRIPT_DIR% 

echo "###############################################################################"
echo " _       ___           __                  "
echo "| |     / (_)___  ____/ /___ _      _______"
echo "| | /| / / / __ \/ __  / __ \ | /| / / ___/"
echo "| |/ |/ / / / / / /_/ / /_/ / |/ |/ (__  ) "
echo "|__/|__/_/_/ /_/\__,_/\____/|__/|__/____/  "
echo "                                           "
echo "Container built with OpenVINO Toolkit"
echo "Image Tag : %TAG%"
echo ""
echo "###############################################################################"
echo "CTLC+C to cancel docker push"
echo "###############################################################################"
timeout 10
docker push %TAG%

goto :EOF

:HELP
echo "======================================="
echo "Please specify Windows Server Version and reistry"
echo "  OS Type        : servercore or nanoserver"
echo "  TAG            : ltsc2019, 1809, 1903"
echo "  Registry       : Your registry"
echo "  Example ./%~nx0 ltsc2019 myregistry"
echo "======================================="
