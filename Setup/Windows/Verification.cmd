@echo off
cd "C:\Program Files (x86)\IntelSWTools\openvino\bin\"
call setupvars.bat

cd "%INTEL_OPENVINO_DIR%\deployment_tools\demo"
call demo_squeezenet_download_convert_run.bat

cd %USERPROFILE%\Documents\Intel\OpenVINO\inference_engine_samples_build\intel64\Release
echo ''
echo '###############################################################################'
echo 'Running CPU'
echo '###############################################################################'
classification_sample_async -i "%INTEL_OPENVINO_DIR%\deployment_tools\demo\car.png" -m "%USERPROFILE%\Documents\Intel\OpenVINO\openvino_models\ir\public\squeezenet1.1\FP16\squeezenet1.1.xml" -d CPU  

echo ''
echo '###############################################################################'
echo 'Running GPU'
echo '###############################################################################'
classification_sample_async -i "%INTEL_OPENVINO_DIR%\deployment_tools\demo\car.png" -m "%USERPROFILE%\Documents\Intel\OpenVINO\openvino_models\ir\public\squeezenet1.1\FP16\squeezenet1.1.xml" -d GPU  

echo ''
echo '###############################################################################'
echo 'Running MYRIAD'
echo '###############################################################################'
classification_sample_async -i "%INTEL_OPENVINO_DIR%\deployment_tools\demo\car.png" -m "%USERPROFILE%\Documents\Intel\OpenVINO\openvino_models\ir\public\squeezenet1.1\FP16\squeezenet1.1.xml" -d MYRIAD  

