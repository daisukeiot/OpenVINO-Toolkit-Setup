if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify Container and Target Device"
    echo "  Example ./verify-container.sh myregistry/container:tag CPU"
    echo "======================================="
    exit
fi

#
# Build Container with verification script
# Built container but do not push to registry
#
TARGET_TAG=$1
TARGET_DEV=$2

if [ "${TARGET_DEV}" == "MYRIAD" ]
  then
    DOCKER_OPTION='--device-cgroup-rule='c 189:* rmw' -v /dev/bus/usb:/dev/bus/usb'
  else
    DOCKER_OPTION=""
fi

if [ "${TARGET_DEV}" == "GPU" ]
  then
    DOCKER_OPTION='--device /dev/dri'
  else
    DOCKER_OPTION=""
fi

echo ''
echo '    ____                              ________                _ _____            __  _           '
echo '   /  _/___ ___  ____ _____ ____     / ____/ /___ ___________(_) __(_)________ _/ /_(_)___  ____ '
echo '   / // __ `__ \/ __ `/ __ `/ _ \   / /   / / __ `/ ___/ ___/ / /_/ / ___/ __ `/ __/ / __ \/ __ \'
echo ' _/ // / / / / / /_/ / /_/ /  __/  / /___/ / /_/ (__  |__  ) / __/ / /__/ /_/ / /_/ / /_/ / / / /'
echo '/___/_/ /_/ /_/\__,_/\__, /\___/   \____/_/\__,_/____/____/_/_/ /_/\___/\__,_/\__/_/\____/_/ /_/ '
echo '                    /____/                                                                       '
echo '###################################################################################################'
echo "Running on ${TARGET_DEV}"
echo '###################################################################################################'

docker run -it --rm ${DOCKER_OPTION} ${TARGET_TAG} /bin/bash -c "cd /opt/intel/openvino/deployment_tools/demo && ./demo_squeezenet_download_convert_run.sh -d ${TARGET_DEV}"
