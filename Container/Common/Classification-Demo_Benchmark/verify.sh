#!/bin/bash

if [ $# -eq 1 ]
  then
    TARGET=$1
fi

source /opt/intel/openvino/bin/setupvars.sh
cd /home/${USER}/inference_engine_samples_build/intel64/Release
echo ''
echo '###############################################################################'
echo "Running on ${TARGET}"
echo '###############################################################################'

./classification_sample_async -i ${INSTALLDIR}/deployment_tools/demo/car.png -m /home/${USER}/openvino_models/ir/public/squeezenet1.1/FP16/squeezenet1.1.xml -d ${TARGET}