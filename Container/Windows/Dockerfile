# escape=`

ARG OS_VERSION=ltsc2019

FROM mcr.microsoft.com/windows/servercore:${OS_VERSION}

#
# Local variables
#
ARG PYTHON_VERSION=3.7.5
ARG PYTHON_DIR=C:\python${PYTHON_VERSION}
ARG PYTHON_BIN=${PYTHON_DIR}\python.exe
ARG PYTHON_DOWNLOAD=https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe
ARG VS_BUILT_DOWNLOAD=https://aka.ms/vs/16/release/vs_buildtools.exe
ARG OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16613/w_openvino_toolkit_p_2020.2.117.exe

#
# Set shell to Powershell
#
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'Continue'; $verbosePreference='Continue';"]

WORKDIR C:\OV.TEMP

#
# Install Python
#
ADD ${PYTHON_DOWNLOAD} .\python3.exe
ARG PARAMS="/quiet /log Python.log TargetDir=${PYTHON_DIR} InstallAllUsers=1 PrependPath=1 Include_test=0 Include_launcher=0 Include_tcltk=0 Include_doc=0 Shortcuts=0"
RUN Start-Process C:\OV.TEMP\python3.exe -ArgumentList $ENV:PARAMS -Wait -PassThru -NoNewWindow

# Install cmake using PIP
RUN Start-Process $ENV:PYTHON_BIN -ArgumentList '--version' ; `
    Start-Process $ENV:PYTHON_BIN -ArgumentList '-m pip install --upgrade pip' -Wait -PassThru -NoNewWindow ; `
    Start-Process $ENV:PYTHON_BIN -ArgumentList '-m pip install cmake' -Wait -PassThru -NoNewWindow

#
# Install VS Build Tools
#
ADD ${VS_BUILT_DOWNLOAD} .\vs_buildtools.exe
RUN Start-Process C:\OV.TEMP\vs_buildtools.exe `
    -ArgumentList '--quiet --wait --norestart --nocache `
                   --add Microsoft.VisualStudio.Workload.VCTools `
                   --add Microsoft.VisualStudio.Component.Windows10SDK.17763 `
                   --add Microsoft.Component.MSBuild `
                   --remove Microsoft.VisualStudio.Component.Windows10SDK.18362 `
                   --includeRecommended' `
    -Wait -PassThru -NoNewWindow 

#
# Install OpenVINO Toolkit
#
ADD ${OPENVINO_DOWNLOAD} .\w_openvino_toolkit.exe

#
# Do not install GPU and VPU
# Don't split this line.  Installer does not like spaces
#
ARG OPENVINO_COMPONENTS='OPENVINO_COMMON,icl_redist,INFERENCE_ENGINE,INFERENCE_ENGINE_CPU,INFERENCE_ENGINE_SDK,INFERENCE_ENGINE_SAMPLES,POT,OMZ_TOOLS,MODEL_OPTIMIZER,OMZ_DEV,OPENCV,OPENCV_RUNTIME,OPENCV_PYTHON,SETUPVARS'
#                         INFERENCE_ENGINE_GPU, `
#                         INFERENCE_ENGINE_VPU, `
#                         VPU_DRV'

ARG PARAMS="--s --r yes --l C:\OV.TEMP\openvino_log.txt --a install --eula=accept --ignore-cpu --components=${OPENVINO_COMPONENTS} --output=C:\OV.TEMP\openvino_out.txt"
RUN Start-Process C:\OV.TEMP\w_openvino_toolkit.exe `
        -ArgumentList $ENV:PARAMS `
        -Wait -PassThru -NoNewWindow

WORKDIR 'C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\model_optimizer\install_prerequisites'
RUN .\install_prerequisites.bat ; `
    Start-Process $ENV:PYTHON_BIN -ArgumentList '-m easy_install protobuf-3.6.1-py3.7-win-amd64.egg' -Wait -PassThru -NoNewWindow

WORKDIR C:\

# Clean Up
RUN Remove-Item -Path C:\OV.TEMP -recurse -force

ENV INTEL_OPENVINO_DIR 'C:\Program Files (x86)\IntelSWTools\openvino'
#
# Change Shell to CMD.EXE
#
SHELL ["cmd", "/S", "/C"]

CMD cmd.exe