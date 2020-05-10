# escape=`

#
# Pass variables with --build-arg option
# BASE_IMAGE  : Base Image to install OpenVINO 
# 
ARG TAG_BASE=servercore:ltsc2019
FROM ${TAG_BASE}

#
# Variables that can be specified with --build-arg option
#
ARG PYTHON_VERSION=3.7
ARG OPENVINO_VER=2020.2.117
ARG OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16613/w_openvino_toolkit_p_2020.2.117.exe

ENV INTEL_OPENVINO_DIR 'C:\Program Files (x86)\IntelSWTools\openvino'

#
# Set shell to Powershell
#
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'Continue'; $verbosePreference='Continue';"]

WORKDIR C:\OV.TEMP

#
# Install OpenVINO Toolkit
#
ADD ${OPENVINO_DOWNLOAD} .\w_openvino_toolkit.exe

#
# Do not install GPU and VPU
# Don't split this line.  Installer does not like spaces
#
ARG OV_COMP='OPENVINO_COMMON,icl_redist,INFERENCE_ENGINE,INFERENCE_ENGINE_CPU,INFERENCE_ENGINE_SDK,INFERENCE_ENGINE_SAMPLES,POT,OMZ_TOOLS,MODEL_OPTIMIZER,OMZ_DEV,OPENCV,OPENCV_RUNTIME,OPENCV_PYTHON,SETUPVARS'
#                         INFERENCE_ENGINE_GPU, `
#                         INFERENCE_ENGINE_VPU, `
#                         VPU_DRV'

RUN Start-Process C:\OV.TEMP\w_openvino_toolkit.exe `
        -ArgumentList '--s', `
                      '--r yes', `
                      '--a install', `
                      '--eula=accept', `
                      '--ignore-cpu', `
                      "--components=$ENV:OV_COMP", `
                      '--output=C:\OV.TEMP\openvino_out.txt' `
        -Wait -PassThru -NoNewWindow

WORKDIR 'C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\model_optimizer\install_prerequisites'
RUN .\install_prerequisites.bat ; `
    Start-Process $ENV:PYTHON_BIN `
        -ArgumentList "-m easy_install protobuf-$ENV:PYTHON_VERSION-py3.7-win-amd64.egg" `
        -Wait -PassThru -NoNewWindow

WORKDIR C:\

# Clean Up
RUN Remove-Item -Force -Recurse -Path C:\OV.TEMP ; `
    Remove-Item -Force -Recurse -Path ${Env:TEMP}\*

#
# Change Shell to CMD.EXE
#
SHELL ["cmd", "/S", "/C"]

CMD cmd.exe