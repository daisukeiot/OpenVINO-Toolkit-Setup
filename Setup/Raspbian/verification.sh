SCRIPT_DIR=$(cd $(dirname $0); pwd)

cd ~/

if [ ! -d "build" ]; then
  mkdir build
fi

cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-march=armv7-a" /opt/intel/openvino/deployment_tools/inference_engine/samples/cpp
make -j2 object_detection_sample_ssd

if [ ! -f "face-detection-0100.xml" ]; then
    wget --no-check-certificate https://download.01.org/opencv/2020/openvinotoolkit/2020.2/open_model_zoo/models_bin/3/face-detection-0100/FP16/face-detection-0100.xml
fi

if [ ! -f "face-detection-0100.bin" ]; then
    wget --no-check-certificate https://download.01.org/opencv/2020/openvinotoolkit/2020.2/open_model_zoo/models_bin/3/face-detection-0100/FP16/face-detection-0100.bin
fi

if [ ! -f "face.jpg" ]; then
    wget --no-check-certificate https://github.com/intel-iot-devkit/inference-tutorials-generic/raw/openvino_toolkit_2019_r1_0/face_detection_tutorial/data/face.jpg
fi
./armv7l/Release/object_detection_sample_ssd -m ${SCRIPT_DIR}/face-detection-adas-0001.xml -d MYRIAD -i ${SCRIPT_DIR}/face.jpg