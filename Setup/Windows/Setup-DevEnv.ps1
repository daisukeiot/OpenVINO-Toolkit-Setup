function Check-RegValue {
    Param(
        [parameter(Mandatory=$true)]
        [ValidateNotNullOrEmpty()]$Path,
        [parameter(Mandatory=$true)]
        [ValidateNotNullOrEmpty()]$Value
    )

    try {
        Get-ItemProperty -Path $Path | Select-Object -ExpandProperty $Value -ErrorAction Stop | Out-Null
            return $true
        }
    catch {
        return $false
    }
}

function UpdateEnvironment()
{
    if (Check-RegValue -Path "HKLM:System\CurrentControlSet\Control\Session Manager\Environment" -Value "INTEL_DEV_REDIST")
    {
        if ($ENV:INTEL_DEV_REDIST -eq $null)
        {
            $INTEL_DEV_REDIST = Get-ItemProperty -Path "HKLM:System\CurrentControlSet\Control\Session Manager\Environment" -Name 'INTEL_DEV_REDIST'
            $ENV:INTEL_DEV_REDIST = $INTEL_DEV_REDIST.INTEL_DEV_REDIST
        }
    }

    $Path_Sys = Get-ItemProperty -Path "HKLM:System\CurrentControlSet\Control\Session Manager\Environment" -Name 'Path'
    $Path_User = Get-ItemProperty -Path "HKCU:Environment" -Name 'Path'

    if (Check-RegValue -Path "HKLM:System\CurrentControlSet\Control\Session Manager\Environment" -Value "MIC_LD_LIBRARY_PATH")
    {
        if ($ENV:INTEL_DEV_REDIST -eq $null)
        {
            $MIC_LD_LIBRARY_PATH = Get-ItemProperty -Path "HKLM:System\CurrentControlSet\Control\Session Manager\Environment" -Name 'MIC_LD_LIBRARY_PATH'
            $ENV:MIC_LD_LIBRARY_PATH = $MIC_LD_LIBRARY_PATH.MIC_LD_LIBRARY_PATH
        }
    }

    $Path_Sys = Get-ItemProperty -Path "HKLM:System\CurrentControlSet\Control\Session Manager\Environment" -Name 'Path'
    $Path_User = Get-ItemProperty -Path "HKCU:Environment" -Name 'Path'
    
    $Path_New = $Path_Sys.Path + ';' + $Path_User.Path
    Write-Host "Current Path : " + $ENV:PATH
    Write-Host "New Path     : " + $Path_New
    $ENV:PATH= $Path_New
}

if (-not (Test-Path "C:\OV.Work"))
{
    New-Item "C:\OV.WORK" -itemtype directory | Out-Null
}


#######################################################################################
#
# Install Visual Studio 2019
#
#######################################################################################

$URL_VS = 'https://aka.ms/vs/16/release/vs_Community.exe'
$PATH_VS = 'C:\OV.Work\vs.exe'
$VS_WORKLOADs = ' --add Microsoft.VisualStudio.Workload.NativeDesktop' + `
                ' --add Microsoft.VisualStudio.Workload.Universal' + `
                ' --add Microsoft.VisualStudio.Component.Windows10SDK.17763' +
                ' --remove Microsoft.VisualStudio.Component.Windows81SDK' +
                ' --remove Microsoft.VisualStudio.Component.Windows10SDK.18362' +
                ' --includeRecommended'

Write-Host "Downloading Bootstrapper ..."

if (-not (Test-Path $PATH_VS))
{
    Invoke-WebRequest -Uri $URL_VS -OutFile $PATH_VS
}

$Arguments = ($VS_WORKLOADs, '--passive', '--norestart', '--wait', '--nocache')

Write-Host "Starting Visual Studio Install ..."
$process = Start-Process -FilePath $PATH_VS -ArgumentList $Arguments -Wait -PassThru -NoNewWindow
$exitCode = $process.ExitCode

if ($exitCode -eq 0 -or $exitCode -eq 3010)
{
    Write-Host 'Visual Studio 2019 installed successfully'
}
else
{
    Write-Host "Non zero exit code returned by the installation process : $exitCode."
    exit $exitCode
}

#######################################################################################
#
# Install Python
#
#######################################################################################
$PYTHON_VERSION="3.7.5"
$PYTHON_DIR="C:\Python${PYTHON_VERSION}"
$URL_Python = "https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe"
$PATH_Python = "C:\OV.Work\Python${PYTHON_VERSION}.exe"

Write-Host "Downloading Python ..."

if (-not (Test-Path $PATH_Python))
{
    Invoke-WebRequest -Uri $URL_Python -OutFile $PATH_Python
}

$Arguments = ('/passive', '/log', 'C:\OV.Work\Python.log', "TargetDir=$PYTHON_DIR", 'InstallAllUsers=1','PrependPath=1', 'Include_test=0', 'Include_launcher=0', 'Include_tcltk=0', 'Include_doc=0', 'Shortcuts=0')

Write-Host "Starting Python Install ..."
$process = Start-Process -FilePath $PATH_Python -ArgumentList $Arguments -Wait -PassThru -NoNewWindow
$exitCode = $process.ExitCode

if ($exitCode -eq 0)
{
    Write-Host "Python $PYTHON_VERSION installed successfully"
}
else
{
    Write-Host "Non zero exit code returned by the installation process : $exitCode."
    exit $exitCode
}

UpdateEnvironment
python.exe --version
python.exe -m pip install --upgrade pip

#######################################################################################
#
# Install CMake
#
#######################################################################################
$PYTHON_BIN = Join-Path -Path $PYTHON_DIR -ChildPath "python.exe"

if (-not (Test-Path $PYTHON_BIN))
{
    Write-Host "Could not find python.exe : $PYTHON_BIN"
    exit $exitCode
}

$process = Start-Process -FilePath $PYTHON_BIN -ArgumentList '-m pip install cmake' -Wait -PassThru -NoNewWindow

$exitCode = $process.ExitCode

if ($exitCode -eq 0)
{
    Write-Host "Cmake installed successfully"
}
else
{
    Write-Host "Non zero exit code returned by the installation process : $exitCode."
    exit $exitCode
}

#######################################################################################
#
# Install OpenVINO
#
#######################################################################################
$URL_OPENVINO = "http://registrationcenter-download.intel.com/akdlm/irc_nas/16613/w_openvino_toolkit_p_2020.2.117.exe"
$PATH_OPENVINO = "C:\OV.Work\openvino.exe"

Write-Host "Downloading OpenVINO ..."

if (-not (Test-Path $PATH_OPENVINO))
{
    Invoke-WebRequest -Uri $URL_OPENVINO -OutFile $PATH_OPENVINO
}

$OPENVINO_COMPONENTS = 'OPENVINO_COMMON,icl_redist,INFERENCE_ENGINE,INFERENCE_ENGINE_CPU,INFERENCE_ENGINE_GPU,INFERENCE_ENGINE_SDK,INFERENCE_ENGINE_SAMPLES,POT,OMZ_TOOLS,INFERENCE_ENGINE_VPU,VPU_DRV,MODEL_OPTIMIZER,OMZ_DEV,OPENCV,OPENCV_RUNTIME,OPENCV_PYTHON,SETUPVARS'
$Arguments = ('--s', '--r yes', '--l C:\OV.Work\openvino_log.txt', '--a install', '--eula=accept', "--components=${OPENVINO_COMPONENTS}", '--output=C:\OV.Work\openvino_out.txt')

Write-Host "Starting OpenVINO Toolkit ..."
$process = Start-Process -FilePath $PATH_OPENVINO -ArgumentList $Arguments -Wait -PassThru -NoNewWindow
$exitCode = $process.ExitCode

if ($exitCode -eq 0)
{
    Write-Host "OpenVINO installed successfully"
}
else
{
    Write-Host "Non zero exit code returned by the installation process : $exitCode."
    exit $exitCode
}

UpdateEnvironment

Set-Location "C:\Program Files (x86)\IntelSWTools\openvino\bin"

.\setupvars.bat

Set-Location "C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\model_optimizer\install_prerequisites"

.\install_prerequisites.bat
python.exe -m easy_install .\protobuf-3.6.1-py3.7-win-amd64.egg

Set-Location "C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\demo"

.\demo_squeezenet_download_convert_run.bat 