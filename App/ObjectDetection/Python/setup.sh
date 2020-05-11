SCRIPT_DIR=$(cd $(dirname $0); pwd)

if [ ! -d "open_model_zoo" ]; then
  git clone https://github.com/opencv/open_model_zoo.git
fi

if [ -d ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer ]; then
  cd ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer
  sudo -H python3.7 -m pip install -r requirements.txt
  cd ${SCRIPT_DIR}
  sudo -H python3.7 -m pip install -r ./requirements.txt
fi