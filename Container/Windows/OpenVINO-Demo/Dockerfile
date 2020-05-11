# escape=`
#
# Pass variables with --build-arg option
# TAG_BASE  : Base OS Image
# 
ARG TAG_BASE=servercore:ltsc2019
#
# Image with OpenVINO Toolkit
#
FROM ${TAG_BASE}
ARG SETUPVAR="C:\Program` Files` (x86)\IntelSWTools\openvino\bin\setupvars.bat"

#
# Set shell to Powershell
#
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'Continue'; $verbosePreference='Continue';"]

#
# Install OpenVINO Dependencies
# Install dependencies for Model Downloader and Model Optimizer
#
RUN cd ${ENV:INTEL_OPENVINO_DIR} ; `
    ./bin/setupvars.bat -pyver ${ENV:PYTHON_VERSION} ; `
    cd deployment_tools/model_optimizer/install_prerequisites ; `
    ./install_prerequisites.bat ; `
    cd ${ENV:INTEL_OPENVINO_DIR} ; `
    python -m pip install -r ./deployment_tools/open_model_zoo/tools/downloader/requirements.in ; `
    python -m pip install -r ./inference_engine/samples/python/requirements.txt

WORKDIR ${INTEL_OPENVINO_DIR}/deployment_tools/demo

# Clean Up
RUN Remove-Item -Force -Recurse -Path ${ENV:TEMP}\*

SHELL ["cmd", "/S", "/C"]

ENTRYPOINT demo_squeezenet_download_convert_run.bat
