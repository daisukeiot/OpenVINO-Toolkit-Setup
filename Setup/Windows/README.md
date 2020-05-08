# Windows 10 Development Environment

Verified with :

- Windows 10 1809 LTSC
- Visual Studio 2019
- Python 3.7.5
- CMake
- OpenVINO 2020.2.117

## Clone the repo

1. [Install Git](https://git-scm.com/download/win)
1. Clone to the Windows 10 Development Environment

```cmd
cd \
git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git
```

## Install Tools and OpenVINO Toolkit

From Admin Console run Setup-DevEnv.ps1

```cmd
cd C:\Openvino-Toolkit-Setup\Setup\Windows
Powershell -NoProfile -ExecutionPolicy Bypass -File .\Setup-DevEnv.ps1
```

## Verification

1. Start a new CMD window
1. Run verification on CPU, GPU, and MYRIAD with :

```cmd
cd C:\Openvino-Toolkit-Setup\Setup\Windows
.\Verification.cmd
```

## Container

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