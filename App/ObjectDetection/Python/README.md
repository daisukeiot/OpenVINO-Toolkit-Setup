# Object Detection app

## Environment

- Ubuntu 18.04
- Python 3.7
- OpenVINO 2020.3.194

## Ubuntu Setup

OpenVINO toolkit must be installed on the device.  

Follow [this](../../../Setup/Ubuntu/README.md) instruction to setup Ubuntu System

Follow [this](../../../Setup/Raspbian/README.md) instruction to setup Raspberry Pi

> [!IMPORTANT]  
> Raspberry Pi requires Movidius to run inference

## App Setup

Clone this repo and run /App/ObjectDetectino/Python/setup.sh

```bash
cd ~ && \
git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git && \
cd OpenVINO-Toolkit-Setup/App/ObjectDetection/Python && \
./setup.sh

```

## Running App

Start the app with :  

```bash
cd ~/OpenVINO-Toolkit-Setup/App/ObjectDetection/Python
python3.7 ./main.py
```

- Access the UI from a browser `http://<IP Address of the device>:8080`

![Browser](media/Browser_UI.png)

## Video Playback

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

## AI Inference

You can start and stop AI Inference.  

Select Model, Hardware, and Precision to run inference on then click "Configure" button

- Use toggle switch to turn on/off AI inference  
- Look for the model locally, if not found, download from internet
- Converts model to IR if necessary
- Loads model to selected HW

## Target HW

Currently you can only select 1 target hardware

## Precision

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

### Version 1.3 (May 7, 2020)

- Added Async Inference

### Version 1.4 (May 27, 2020)

- Added Open Pose model
