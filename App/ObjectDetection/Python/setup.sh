SCRIPT_DIR=$(cd $(dirname $0); pwd)

if [ ! -d "open_model_zoo" ]; then
  if [ -f /etc/lsb-release ]; then
    # Ubuntu
    git clone https://github.com/opencv/open_model_zoo.git
  elif [ -f /usr/bin/lsb_release ]; then
    # Raspbian?
    model=$(cat /proc/cpuinfo | grep  "Model" | cut -d ":" -f2 | cut -d " " -f2)
    if [ "$model" = "Raspberry" ]; then
      wget --no-check-certificate https://github.com/opencv/open_model_zoo/archive/2019_R3.1.tar.gz -O open_model_zoo.tar.gz
      mkdir open_model_zoo && tar -xf open_model_zoo.tar.gz -C open_model_zoo --strip-components 1
      rm open_model_zoo.tar.gz
    fi
  fi
fi

if [ -d ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer ]; then
  cd ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer
  sudo -H python3.7 -m pip install -r requirements.txt
  cd ${SCRIPT_DIR}
  sudo -H python3.7 -m pip install -r ./requirements.txt
fi