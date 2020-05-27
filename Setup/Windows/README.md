# Windows 10 Development Environment

Verified with :

- Windows 10 1809 LTSC
- Visual Studio 2019
- Python 3.7.5
- CMake
- OpenVINO 2020.2.117

## Clone the repo

1. [Install Git](https://git-scm.com/download/win) or your favorite GIT client app
1. Clone to the Windows 10 Development Environment

```cmd
cd C:\
git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git
cd \OpenVINO-Toolkit-Setup\Setup\Windows
```

## OpenVINO Toolkit Setup

Building samples require Visual Studio build tools.  The script installs :

- Visual Studio 2019
- Python 3.7.5
- CMake
- OptnVINO Toolkit

From Admin Console run Setup-DevEnv.ps1

```cmd
cd C:\Openvino-Toolkit-Setup\Setup\Windows
Powershell -NoProfile -ExecutionPolicy Bypass -File .\Setup-DevEnv.ps1
```

### Reference : OpenVINO Toolkit installation by Intel

Detailed instruction for OpenVINO Toolkit Setup

[Install Intel® Distribution of OpenVINO™ toolkit for Windows 10](https://docs.openvinotoolkit.org/2020.2/_docs_install_guides_installing_openvino_windows.html)

## OpenVINO Toolkit Verification

The verification script will test :

- Model Downloader
- Model Optimizer
- OpenVINO inference on CPU, GPU, and MYRIAD

```cmd
cd C:\Openvino-Toolkit-Setup\Setup\Windows
.\Verification.cmd
```

More info : [Use Verification Scripts to Verify Your Installation](https://docs.openvinotoolkit.org/2020.2/_docs_install_guides_installing_openvino_windows.html#Using-Demo-Scripts)

## Container Runtime Setup

If you are planning to run IoT Edge or containerized OpenVINO application, install Docker/Moby

1. Install Hyper-V with :  

    ```cmd
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

    ```

    > [!IMPORTANT]
    > Essential information required for user success  
    > If you see "RestartNeeded : True", restart PC to complete Hyper-V installation
    >  
    > ```bash
    > PS C:\> Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All  
    > Do you want to restart the computer to complete this operation now?  
    > [Y] Yes  [N] No  [?] Help (default is "Y"): n  
    >  
    > Path          :  
    > Online        : True  
    > RestartNeeded : True

1. Install Docker  

    - Option 1 : Install IoT Edge and Moby

    ```bash
    . {Invoke-WebRequest -useb https://aka.ms/iotedge-win} | Invoke-Expression; Deploy-IoTEdge
    ```

    - Option 2 : Install [Docker Desktop](https://hub.docker.com/editions/community/docker-ce-desktop-windows)

### Azure IoT Edge Configuration

- [Install the Azure IoT Edge runtime on Windows](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-windows)

## Next Step

[Run Object Detection Python App](../../README.md#running-object-detection-python-app)