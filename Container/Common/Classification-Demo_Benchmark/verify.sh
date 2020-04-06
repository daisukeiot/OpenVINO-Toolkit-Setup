#!/bin/bash

if [ $# -eq 1 ]
  then
    TARGET=$1
fi

source /opt/intel/openvino/bin/setupvars.sh
cd /home/${USER}/inference_engine_samples_build/intel64/Release
echo ''
echo '    ____                              ________                _ _____            __  _           '
echo '   /  _/___ ___  ____ _____ ____     / ____/ /___ ___________(_) __(_)________ _/ /_(_)___  ____ '
echo '   / // __ `__ \/ __ `/ __ `/ _ \   / /   / / __ `/ ___/ ___/ / /_/ / ___/ __ `/ __/ / __ \/ __ \'
echo ' _/ // / / / / / /_/ / /_/ /  __/  / /___/ / /_/ (__  |__  ) / __/ / /__/ /_/ / /_/ / /_/ / / / /'
echo '/___/_/ /_/ /_/\__,_/\__, /\___/   \____/_/\__,_/____/____/_/_/ /_/\___/\__,_/\__/_/\____/_/ /_/ '
echo '                    /____/                                                                       '
echo '###################################################################################################'
echo "Running on ${TARGET}"
echo '###################################################################################################'

./classification_sample_async -i ${INSTALLDIR}/deployment_tools/demo/car.png -m /home/${USER}/openvino_models/ir/public/squeezenet1.1/FP16/squeezenet1.1.xml -d ${TARGET}