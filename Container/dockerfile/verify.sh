#!/bin/bash

cd /home/${USER}/inference_engine_samples_build/intel64/Release
echo ''
echo '###############################################################################'
echo "Running on ${TARGET}"
echo '###############################################################################'

./classification_sample_async -i /opt/intel/openvino/deployment_tools/demo/car.png -m /home/${USER}/openvino_models/ir/public/squeezenet1.1/FP16/squeezenet1.1.xml -d ${TARGET}