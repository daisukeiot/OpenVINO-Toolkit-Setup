#!/bin/bash

source /opt/intel/openvino/bin/setupvars.sh
cd /home/${USER}/inference_engine_samples_build/intel64/Release
echo ''
echo '###############################################################################'
echo "Running on ${TARGET}"
echo '###############################################################################'

./benchmark_app -d ${TARGET} -i ${INSTALLDIR}/deployment_tools/demo/car.png -m /home/${USER}/openvino_models/ir/public/alexnet/FP16/alexnet.xml