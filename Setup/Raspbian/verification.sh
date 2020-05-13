SAMPLE_DIR=/home/$(whoami)/build
echo ${SAMPLE_DIR}
cd ~/

if [ ! -d "${SAMPLE_DIR}" ]; then
  mkdir ${SAMPLE_DIR}
fi

cd ${SAMPLE_DIR}
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-march=armv7-a" /opt/intel/openvino/deployment_tools/inference_engine/samples/cpp
make -j2 object_detection_sample_ssd

if [ -f "face-detection-adas-0001.xml" ]; then
    rm face-detection-adas-0001.xml
fi

if [ -f "face-detection-adas-0001.bin" ]; then
    rm face-detection-adas-0001.bin
fi

if [ -f "face.jpg" ]; then
    rm face.jpg
fi

wget --no-check-certificate https://github.com/intel-iot-devkit/inference-tutorials-generic/raw/openvino_toolkit_2019_r1_0/face_detection_tutorial/data/face.jpg

# IRv10 does not work https://github.com/openvinotoolkit/openvino/issues/411
# wget --no-check-certificate https://download.01.org/opencv/2019/open_model_zoo/R4/20191230_170000_models_bin/face-detection-retail-0004/FP16/face-detection-retail-0004.bin
# wget --no-check-certificate https://download.01.org/opencv/2019/open_model_zoo/R4/20191230_170000_models_bin/face-detection-retail-0004/FP16/face-detection-retail-0004.xml

# use IRv7
wget --no-check-certificate https://download.01.org/opencv/2019/open_model_zoo/R4/20191121_190000_models_bin/face-detection-retail-0004/FP16/face-detection-retail-0004.bin
wget --no-check-certificate https://download.01.org/opencv/2019/open_model_zoo/R4/20191121_190000_models_bin/face-detection-retail-0004/FP16/face-detection-retail-0004.xml

./armv7l/Release/object_detection_sample_ssd -m ${SAMPLE_DIR}/face-detection-retail-0004.xml -d MYRIAD -i ${SAMPLE_DIR}/face.jpg
