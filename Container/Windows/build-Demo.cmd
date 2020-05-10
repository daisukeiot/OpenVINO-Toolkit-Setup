@echo off
if "%1" equ "" goto :HELP

set SCRIPT_DIR=%~dp0
cls

SET TAG_BASE=%1
SET TAG=%TAG_BASE%_demo

docker inspect --type=image %TAG% > nul 2>&1

if %errorlevel% == 0 (
    echo Deleting image
    docker rmi -f %TAG%
)

echo .
echo     ____        _ __    __   _____ __             __ 
echo    / __ )__  __(_) /___/ /  / ___// /_____ ______/ /_
echo   / __  / / / / / / __  /   \__ \/ __/ __ `/ ___/ __/
echo  / /_/ / /_/ / / / /_/ /   ___/ / /_/ /_/ / /  / /_  
echo /_____/\__,_/_/_/\__,_/   /____/\__/\__,_/_/   \__/  
echo .
echo .
echo Image Tag  : %TAG%
echo Base Image : %TAG_BASE%
echo .
REM
REM Install OpenVINO Toolkit to Ubuntu Base Image
REM
docker build --isolation hyperv --squash --rm -f %SCRIPT_DIR%\OpenVINO-Demo\Dockerfile -t %TAG% \
  --build-arg TAG_BASE=%TAG_BASE% \
  %SCRIPT_DIR%

REM
REM Check if the image exists or not
REM
docker inspect --type=image %TAG% > nul 2>&1

if %errorlevel% == 1 (
    echo "Failed to create image"
    goto :EOF
)

echo ###############################################################################
echo .
echo    ____                 _    _______   ______     ____                     
echo   / __ \____  ___  ____| |  / /  _/ | / / __ \   / __ \___  ____ ___  ____ 
echo  / / / / __ \/ _ \/ __ \ | / // //  |/ / / / /  / / / / _ \/ __ `__ \/ __ \
echo / /_/ / /_/ /  __/ / / / |/ // // /|  / /_/ /  / /_/ /  __/ / / / / / /_/ /
echo \____/ .___/\___/_/ /_/|___/___/_/ |_/\____/  /_____/\___/_/ /_/ /_/\____/ 
echo     /_/                                                                    
echo .
echo Image Tag : %TAG%
echo .
REM
REM Check if the image exists or not
REM
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
echo .
docker push %TAG%