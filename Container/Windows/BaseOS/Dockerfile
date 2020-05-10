# escape=`

ARG OS_TYPE=servercore
ARG OS_VERSION=ltsc2019
FROM mcr.microsoft.com/${OS_TYPE}:${OS_VERSION}

#
# Local variables
#
ARG OS_TYPE=servercore
ARG PYTHON_VERSION=3.7.5
ARG PYTHON_DIR=C:\\python${PYTHON_VERSION}
ARG PYTHON_BIN=${PYTHON_DIR}\python.exe
ARG PYTHON_EXE_DOWNLOAD=https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe
ARG PYTHON_ZIP_DOWNLOAD=https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-embed-amd64.zip
ARG VS_BUILT_DOWNLOAD=https://aka.ms/vs/16/release/vs_buildtools.exe

#
# Set shell to Powershell
#
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'Continue'; $verbosePreference='Continue';"]

WORKDIR C:\OV.TEMP

#
# Install Python
#
RUN if ($ENV:OS_TYPE -eq 'nanoserver') { `
        echo "Nano Server Not Supported" ; `
        exit 1 `
    } else { `
        $response = Invoke-WebRequest `
            -Uri $ENV:PYTHON_EXE_DOWNLOAD `
            -OutFile 'C:\\OV.TEMP\\python3.exe' `
            -UseBasicParsing `
            -Verbose `
            -PassThru ; `
        if ($response.StatusCode -ne 200) { `
            Write-Host $('Download Error : ' + $response.StatusDescription) `
            exit 1 ; `
        } ; `
        Start-Process C:\OV.TEMP\python3.exe `
            -ArgumentList '/quiet', `
                        'InstallAllUsers=1', `
                        'PrependPath=1', `
                        'Include_test=0', `
                        'Include_launcher=0', `
                        'Include_tcltk=0', `
                        'Include_doc=0', `
                        'Shortcuts=0', `
                        "TargetDir=$ENV:PYTHON_DIR" `
            -Wait -PassThru -NoNewWindow `
    } 

# Install cmake using PIP
# Run --version to be sure (for debugging purpose)
RUN Start-Process $ENV:PYTHON_BIN -ArgumentList '--version' -Wait -PassThru -NoNewWindow ; `
    Start-Process $ENV:PYTHON_BIN -ArgumentList '-m pip install --upgrade pip' -Wait -PassThru -NoNewWindow ; `
    Start-Process $ENV:PYTHON_BIN -ArgumentList '-m pip install cmake' -Wait -PassThru -NoNewWindow

#
# Install VS Build Tools
#
ADD ${VS_BUILT_DOWNLOAD} .\vs_buildtools.exe
RUN Start-Process C:\OV.TEMP\vs_buildtools.exe `
        -ArgumentList @('--quiet', `
                        '--wait', `
                        '--norestart', `
                        '--nocache ', `
                        '--add Microsoft.VisualStudio.Workload.VCTools', `
                        '--add Microsoft.VisualStudio.Component.Windows10SDK.17763', `
                        '--add Microsoft.Component.MSBuild', `
                        '--remove Microsoft.VisualStudio.Component.Windows10SDK.18362', `
                        '--includeRecommended') `
        -Wait -PassThru -NoNewWindow 

WORKDIR C:\

# Clean Up
RUN Remove-Item -Force -Recurse -Path C:\OV.TEMP ; `
    Remove-Item -Force -Recurse -Path ${Env:TEMP}\*

ENV INTEL_OPENVINO_DIR 'C:\Program Files (x86)\IntelSWTools\openvino'
#
# Change Shell to CMD.EXE
#
SHELL ["cmd", "/S", "/C"]

CMD cmd.exe