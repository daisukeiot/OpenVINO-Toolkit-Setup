@echo off
if "%1" equ "" goto :HELP

if "%2" equ "" goto :HELP

set SCRIPT_DIR=%~dp0
cls

SET MY_REGISTRY=%1
SET BASE_TAG=%2

REM
REM OpenVINO Toolkit ver 2020.2.120
REM
SET OPENVINO_VER=2020.2.117

SET TAG_BASE=%MY_REGISTRY%/openvino-container:%BASE_TAG%
SET TAG=%MY_REGISTRY%/openvino-container:%BASE_TAG%_ov%OPENVINO_VER%

docker inspect --type=image %TAG% > nul 2>&1

if %errorlevel% == 0 (
    echo Deleting image
    docker rmi -f %TAG%
)

echo.
echo     ____        _ __    __   _____ __             __ 
echo    / __ )__  __(_) /___/ /  / ___// /_____ ______/ /_
echo   / __  / / / / / / __  /   \__ \/ __/ __ `/ ___/ __/
echo  / /_/ / /_/ / / / /_/ /   ___/ / /_/ /_/ / /  / /_  
echo /_____/\__,_/_/_/\__,_/   /____/\__/\__,_/_/   \__/  
echo.
echo    ____                 _    _______   ______     ______            ____   _ __ 
echo   / __ \____  ___  ____^| ^|  / /  _/ ^| / / __ \   /_  __/___  ____  / / /__(_) /_
echo  / / / / __ \/ _ \/ __ \ ^| / // //  ^|/ / / / /    / / / __ \/ __ \/ / //_/ / __/
echo / /_/ / /_/ /  __/ / / / ^|/ // // /^|  / /_/ /    / / / /_/ / /_/ / / ,^< / / /_  
echo \____/ .___/\___/_/ /_/^|___/___/_/ ^|_/\____/    /_/  \____/\____/_/_/^|_/_/\__/  
echo     /_/                                                                         
echo.
echo Image Tag  : %TAG%
echo Base Image : %TAG_BASE%
echo OpenVINO   : %OPENVINO_VER%
echo.
REM
REM Install OpenVINO Toolkit to Windows Base Image
REM
docker build ^
    --isolation hyperv ^
    --squash ^
    --rm ^
    -f %SCRIPT_DIR%/OpenVINO-Toolkit/Dockerfile ^
    -t %TAG% ^
    --build-arg TAG_BASE=%TAG_BASE% ^
    %SCRIPT_DIR%

docker inspect --type=image %TAG% > nul 2>&1

if %errorlevel% == 1 (
    echo "Failed to create image"
    goto :EOF
)

echo ################################################################################
echo    ____                 _    _______   ______     ______            ____   _ __ 
echo   / __ \____  ___  ____^| ^|  / /  _/ ^| / / __ \   /_  __/___  ____  / / /__(_) /_
echo  / / / / __ \/ _ \/ __ \ ^| / // //  ^|/ / / / /    / / / __ \/ __ \/ / //_/ / __/
echo / /_/ / /_/ /  __/ / / / ^|/ // // /^|  / /_/ /    / / / /_/ / /_/ / / ,^< / / /_  
echo \____/ .___/\___/_/ /_/^|___/___/_/ ^|_/\____/    /_/  \____/\____/_/_/^|_/_/\__/  
echo     /_/                                                                         
echo.
echo OpenVINO Toolkit : %OPENVINO_VER%
echo Image Tag        : %TAG%
echo.

docker inspect --type=image %TAG% > nul 2>&1

if %errorlevel% == 1 (
    echo "Failed to create image"
    goto :EOF
)

echo ################################################################################
echo CTLC+C to cancel docker push
echo ################################################################################
timeout 10
echo Pushing Image : %TAG%
echo.
docker push %TAG%

goto :EOF

:HELP
echo =======================================
echo Please specify Windows Server Version and reistry
echo   Registry       : Your registry
echo   Base Tag       : Tag of image to install OpenVINO
echo   Example ./%~nx0 myregistry servercore_ltsc2019_cp3.7.5
echo =======================================
