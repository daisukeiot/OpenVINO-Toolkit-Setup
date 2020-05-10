@echo off

SET PYTHON_VERSION=3.7.5

call .\Windows\build-BaseOS.cmd %1 %2 %3

for /f "tokens=1,2 delims=." %%i in ("%PYTHON_VERSION%") do SET PYTHON_VER_SHORT=%%i.%%j

SET TAG=%MY_REGISTRY%/openvino-container:%OS_TYPE%_%OS_VERSION%_cp%PYTHON_VER_SHORT%

docker inspect --type=image %TAG% > nul 2>&1

if %errorlevel% == 0 (
    call .\Windows\build-OpenVINO-Toolkit.cmd %1 %TAG%
)
