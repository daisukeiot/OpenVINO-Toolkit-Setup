#!/bin/bash

if [ $# -eq 1 ]
  then
    TARGET=$1
fi

source /opt/intel/openvino/bin/setupvars.sh
cd /home/${USER}/inference_engine_samples_build/intel64/Release
echo ''
echo '    __  __     ____         ____            _         '
echo '   / / / /__  / / /___     / __ \___ _   __(_)_______ '
echo '  / /_/ / _ \/ / / __ \   / / / / _ \ | / / / ___/ _ \'
echo ' / __  /  __/ / / /_/ /  / /_/ /  __/ |/ / / /__/  __/'
echo '/_/ /_/\___/_/_/\____/  /_____/\___/|___/_/\___/\___/ '
echo ''
echo '###################################################################################################'
echo "Running on ${TARGET}"
echo '###################################################################################################'

cd ${INSTALLDIR}/inference_engine/samples/python_samples
pip3 install -r ./requirements.txt
python3 ./hello_query_device/hello_query_device.py
