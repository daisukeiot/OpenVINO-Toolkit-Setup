#!/bin/bash

cd /home/${USER}/inference_engine_samples_build/intel64/Release
echo ''
echo '###############################################################################'
echo "Running on ${TARGET}"
echo '###############################################################################'

./benchmark_app -d ${TARGET} -i ${INSTALLDIR}/deployment_tools/demo/car.png -m /home/${USER}/ir/public/alexnet/FP16/alexnet/FP16/alexnet.xml