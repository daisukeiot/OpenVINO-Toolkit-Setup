#!/bin/bash

if [ $# -eq 1 ]
  then
    TARGET=$1
fi

source /opt/intel/openvino/bin/setupvars.sh
cd /home/${USER}/inference_engine_samples_build/intel64/Release
echo ''
echo '    ____                  __                         __  '
echo '   / __ )___  ____  _____/ /_  ____ ___  ____ ______/ /__'
echo '  / __  / _ \/ __ \/ ___/ __ \/ __ `__ \/ __ `/ ___/ //_/'
echo ' / /_/ /  __/ / / / /__/ / / / / / / / / /_/ / /  / ,<   '
echo '/_____/\___/_/ /_/\___/_/ /_/_/ /_/ /_/\__,_/_/  /_/|_|  '
echo ''
echo '###############################################################################'
echo "Running on ${TARGET}"
echo '###############################################################################'

./benchmark_app -d ${TARGET} -i ${INSTALLDIR}/deployment_tools/demo/car.png -m /home/${USER}/openvino_models/ir/public/alexnet/FP16/alexnet.xml