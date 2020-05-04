# Object Detection app

## Environment

- Ubuntu 18.04
- Python 3.7
- OpenVINO 2020.2.120

## Ubuntu Setup

Install Python3.7 and make it default with :

```bash
sudo apt-get update && \
# install Python3.7 for AsyncIO
sudo apt-get install -y curl python3-pip python3.7 python3.7-dev && \
# install pip for python3.7
PATH=$PATH:$HOME/.local/bin && \
echo PATH=$PATH:$HOME/.local/bin >> ~/.bashrc && \
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
python3.7 get-pip.py && \
rm get-pip.py && \
/home/wcbiot/.local/bin
cd /usr/lib/python3/dist-packages && \
sudo ln -s apt_pkg.cpython-{36m,37m}-x86_64-linux-gnu.so
```

## OpenVINO Setup

Install 2020.2.120 with following commands :

```bash
# Temporary make Python3.7 to be default so OpenVINO scripts will install libraries for Python3.7
alias python='python3.7' && \
# echo alias python='python3.7'  >> ~/.bashrc && \
export OPENVINO_VER=2020.2.120
export OPENVINO_PKG=l_openvino_toolkit_p_${OPENVINO_VER}
export OPENVINO_INSTALL=/opt/intel/openvino_${OPENVINO_VER}
export OPENVINO_DIR=/opt/intel/openvino
export OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16612/l_openvino_toolkit_p_2020.2.120.tgz

# install numpy
python3.7 -m pip install 'numpy==1.16' --force-reinstall

# downlaod and install OpenVINO toolkit
mkdir /tmp/openvino
cd /tmp/openvino && \
curl -LOJ "${OPENVINO_DOWNLOAD}" && \
tar -xzf ./*.tgz && \
cd ${OPENVINO_PKG} && \
./install.sh --list_components && \
sed -i 's/decline/accept/g' silent.cfg && \
sudo ./install.sh -s silent.cfg && \
cd ~ && \
rm -rf /tmp/openvino && \

# install all dependencies
cd ${OPENVINO_DIR}/install_dependencies && \
sudo -E ${OPENVINO_DIR}/install_dependencies/_install_all_dependencies.sh && \
sudo usermod -a -G video $USER && \
sudo usermod -a -G users $USER && \
sudo cp /opt/intel/openvino/inference_engine/external/97-myriad-usbboot.rules /etc/udev/rules.d/ && \
sudo udevadm control --reload-rules && \
sudo udevadm trigger && \
sudo ldconfig && \
echo "source ${OPENVINO_DIR}/bin/setupvars.sh" >> ~/.bashrc && \
source /opt/intel/openvino/bin/setupvars.sh && \

# install pre-req for model optimizer
cd ${OPENVINO_DIR}/deployment_tools/model_optimizer/install_prerequisites && \
sudo ./install_prerequisites.sh && \
cd ~
```

## App Setup

Clone this repo and run /App/ObjectDetectino/Python/setup.sh

```bash
cd ~ && \
git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git && \
cd OpenVINO-Toolkit-Setup/App/ObjectDetection/Python && \
./setup.sh

```

## Using App

Start the app with :  

```bash
cd ~/OpenVINO-Toolkit-Setup/App/ObjectDetection/Python
python3.7 ./main.py
```

> [!IMPORTANT]
> To access Movidius USB stick, you must run the app as a super user (sudo)  
>
> Because of environment settings, enter super user with sudo -s then run python3

- Access the UI from a browser `http://<IP Address of the device>:8080`

![Browser](media/Browser_UI.png)

### Video Playback

For video :

- `Play` and `Pause`
- Playback Mode  

  - Sync Playback Mode  

    Plays at the frame rate of the source video

  - Performance Mode

    Plays video as fast as the system can

For camera :

- Change resolution  
  Currently the app supports following resolutions (*camera must support selected resolution)

  - VGA  (640x480)
  - XGA  (1024x748)
  - HD   (1280x720)
  - WXGA (1280x800)
  - FHD  (1920x1080)

### AI Inference

You can start and stop AI Inference.  Selecting `play` button will :  

- Look for the model locally, if not found, download from internet
- Converts model to IR if necessary
- Loads model to selected HW

### Target HW

Currently you can only select 1 target hardware

### Precision

Only FP16 and FP32

## Run in container

Please see [this](../README.md)

## To do list

- Add Yolo support  
    Done : 4.23.2020 (ver 1.1)
- Add tooltips to buttons
    Done : 4.27.2020 (ver 1.2)
- Add Async Inference
- Containerization
- Add IoT Hub device app/IoT Edge support
- HETERO support
- Improve status line display/logging
    Done : 4.27.2020 (ver 1.2)
- Handle camera error
    Done : 4.27.2020 (ver 1.2)

## Release Notes

### Version 1 (April 21, 2020)

- Supports most of Object Detection models from [Open Model Zoo](https://github.com/opencv/open_model_zoo)  
- Supports USB Webcam and Youtube Video as video source

### Version 1.1 (April 23, 2020)

- Added Yolo support

### Version 1.2 (April 27, 2020)

- Added tooltips to UI components
- Bug fixes

