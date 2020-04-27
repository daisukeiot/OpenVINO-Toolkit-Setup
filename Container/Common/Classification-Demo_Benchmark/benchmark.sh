#!/bin/bash

TARGET=CPU

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

cd ${INTEL_OPENVINO_DIR}/deployment_tools/tools/model_downloader
python3 -mpip install --user -r ./requirements.in
python3 ./downloader.py --name alexnet --output /home/$USER/openvino_models/
cd ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer/install_prerequisites
./install_prerequisites.sh
python3 ./mo.py --data_type=FP16 --input_model /home/$USER/openvino_models/public/alexnet/alexnet.caffemodel -o /home/$USER/openvino_models/ir/public/alexnet/FP16/
python3 ./mo.py --data_type=FP32 --input_model /home/$USER/openvino_models/public/alexnet/alexnet.caffemodel -o /home/$USER/openvino_models/ir/public/alexnet/FP32/
cd ${INTEL_OPENVINO_DIR}/rence_engine/samples/cpp
./build_samples.sh
cd /home/$USER/inference_engine_samples_build/benchmark_app
make
./benchmark_app -d ${TARGET} -i ${INSTALLDIR}/deployment_tools/demo/car.png -m /home/${USER}/openvino_models/ir/public/alexnet/FP16/alexnet.xml