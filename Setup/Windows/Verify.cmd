@echo off
cd "C:\Program Files (x86)\IntelSWTools\openvino\bin\"
call setupvars.bat

cd "%INTEL_OPENVINO_DIR%\deployment_tools\demo"
call demo_squeezenet_download_convert_run.bat