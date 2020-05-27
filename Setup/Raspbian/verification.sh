if [ "$(id -u)" != "0" ]; then
  SAMPLE_DIR=/home/$(whoami)/build
else
  SAMPLE_DIR=/home/openvino/build
fi

echo ${SAMPLE_DIR}

if [ ! -d "${SAMPLE_DIR}" ]; then
  mkdir ${SAMPLE_DIR}
fi

cd ${SAMPLE_DIR}

if [ -d /opt/intel/openvino/deployment_tools/inference_engine/samples/cpp ]; then
  SAMPLE_SRC=/opt/intel/openvino/deployment_tools/inference_engine/samples/cpp
else
  SAMPLE_SRC=/opt/intel/openvino/deployment_tools/inference_engine/samples
fi
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-march=armv7-a" ${SAMPLE_SRC}
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

# IRv10 does not work https://github.com/openvinotoolkit/openvino/issues/411
# wget --no-check-certificate https://download.01.org/opencv/2019/open_model_zoo/R4/20191230_170000_models_bin/face-detection-retail-0004/FP16/face-detection-retail-0004.bin
# wget --no-check-certificate https://download.01.org/opencv/2019/open_model_zoo/R4/20191230_170000_models_bin/face-detection-retail-0004/FP16/face-detection-retail-0004.xml

# use IRv7
wget --no-check-certificate https://download.01.org/opencv/2019/open_model_zoo/R4/20191121_190000_models_bin/face-detection-retail-0004/FP16/face-detection-retail-0004.bin
wget --no-check-certificate https://download.01.org/opencv/2019/open_model_zoo/R4/20191121_190000_models_bin/face-detection-retail-0004/FP16/face-detection-retail-0004.xml
wget --no-check-certificate https://github.com/intel-iot-devkit/inference-tutorials-generic/raw/openvino_toolkit_2019_r1_0/face_detection_tutorial/data/face.jpg

sudo -E ./armv7l/Release/object_detection_sample_ssd -m ${SAMPLE_DIR}/face-detection-retail-0004.xml -d MYRIAD -i ${SAMPLE_DIR}/face.jpg

if [ -d ${INTEL_OPENVINO_DIR}/deployment_tools/inference_engine/samples/python_samples ]; then
  PYTHON_SRC=${INTEL_OPENVINO_DIR}/deployment_tools/inference_engine/samples/python_samples
else
  PYTHON_SRC=${INTEL_OPENVINO_DIR}/deployment_tools/inference_engine/samples/python
fi

python3.7 ${PYTHON_SRC}/hello_query_device/hello_query_device.py
