#!/bin/bash

source /opt/intel/openvino/bin/setupvars.sh
cd "${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer/install_prerequisites"
. ./install_prerequisites.sh

cd /opt/intel/openvino/deployment_tools/demo
./demo_squeezenet_download_convert_run.sh

cd /home/${USER}/inference_engine_samples_build/intel64/Release
echo ''
echo '###############################################################################'
echo 'Running CPU'
echo '###############################################################################'

./classification_sample_async -i /opt/intel/openvino/deployment_tools/demo/car.png -m /home/${USER}/openvino_models/ir/public/squeezenet1.1/FP16/squeezenet1.1.xml -d CPU  

echo ''
echo '###############################################################################'
echo 'Running GPU'
echo '###############################################################################'
./classification_sample_async -i /opt/intel/openvino/deployment_tools/demo/car.png -m /home/${USER}/openvino_models/ir/public/squeezenet1.1/FP16/squeezenet1.1.xml -d GPU

echo ''
echo '###############################################################################'
echo 'Running MYRIAD'
echo '###############################################################################'
./classification_sample_async -i /opt/intel/openvino/deployment_tools/demo/car.png -m /home/${USER}/openvino_models/ir/public/squeezenet1.1/FP16/squeezenet1.1.xml -d MYRIAD
