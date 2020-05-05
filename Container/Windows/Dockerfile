# escape=`

ARG OS_VERSION=ltsc2019

FROM mcr.microsoft.com/windows/servercore:${OS_VERSION}

ARG PYTHON_VERSION=3.7.5
ARG PYTHON_DIR=C:\python${PYTHON_VERSION}
ARG OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16613/w_openvino_toolkit_p_2020.2.117.exe

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'Continue'; $verbosePreference='Continue';"]

WORKDIR C:\TEMP

# Install Python
ADD https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe .\python3.exe
ENV Parameters "/quiet /log Python.log TargetDir=${PYTHON_DIR} InstallAllUsers=1 PrependPath=1 Include_test=0 Include_launcher=0 Include_tcltk=0 Include_doc=0 Shortcuts=0"
RUN Start-Process c:\TEMP\python3.exe -ArgumentList $ENV:Parameters -Wait
RUN Start-Process python.exe -ArgumentList '-m pip install cmake' -Wait

# # Download the Build Tools bootstrapper.
ADD https://aka.ms/vs/16/release/vs_buildtools.exe C:\TEMP\vs_buildtools.exe
RUN Start-Process c:\TEMP\vs_buildtools.exe -ArgumentList '--quiet --wait --norestart --nocache --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.Windows10SDK.17763 --remove Microsoft.VisualStudio.Component.Windows10SDK.18362' -Wait

# # Download the Build Tools bootstrapper.
# ADD https://aka.ms/vs/16/release/vs_buildtools.exe C:\TEMP\vs_buildtools.exe

# RUN C:\TEMP\vs_buildtools.exe --quiet --wait --norestart --nocache `
#     --add Microsoft.VisualStudio.Workload.VCTools `
#     --includeRecommended `
#  || IF "%ERRORLEVEL%"=="3010" EXIT 0

# SHELL ["cmd", "/S", "/C"]
ADD $OPENVINO_DOWNLOAD .\w_openvino_toolkit.exe
ARG OPENVINO_COMPONENTS='OPENVINO_COMMON,icl_redist,INFERENCE_ENGINE,INFERENCE_ENGINE_CPU,INFERENCE_ENGINE_GPU,INFERENCE_ENGINE_SDK,INFERENCE_ENGINE_SAMPLES,POT,OMZ_TOOLS,INFERENCE_ENGINE_VPU,VPU_DRV,MODEL_OPTIMIZER,OMZ_DEV,OPENCV,OPENCV_RUNTIME,OPENCV_PYTHON,SETUPVARS'
ENV Parameters "--s --r yes --l C:\Log\openvino_log.txt --a install --eula=accept --ignore-cpu --components=${OPENVINO_COMPONENTS} --output=C:\Log\openvino_out.txt"
RUN Write-Host $ENV:Parameters
RUN Start-Process C:\TEMP\w_openvino_toolkit.exe -ArgumentList $ENV:Parameters -Wait

SHELL ["cmd", "/S", "/C"]
RUN cd C:\Program Files (x86)\IntelSWTools\openvino\bin\ && `
    setupvars.bat && `
    cd C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\model_optimizer\install_prerequisites && `
    install_prerequisites.bat
 
# cleaning up the image
# RUN DEL /Q /F C:\TEMP
 
CMD cmd.exe