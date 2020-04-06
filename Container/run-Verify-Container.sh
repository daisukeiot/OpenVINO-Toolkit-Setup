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

echo '    ____                  __                         __  '
echo '   / __ )___  ____  _____/ /_  ____ ___  ____ ______/ /__'
echo '  / __  / _ \/ __ \/ ___/ __ \/ __ `__ \/ __ `/ ___/ //_/'
echo ' / /_/ /  __/ / / / /__/ / / / / / / / / /_/ / /  / ,<   '
echo '/_____/\___/_/ /_/\___/_/ /_/_/ /_/ /_/\__,_/_/  /_/|_|  '
echo '                                                         '
echo ''
echo 'Running Benchmark Tool on ${TARGET_DEV}'
docker run --rm -it --privileged ${TARGET_TAG} /bin/bash -c "/home/openvino/imageclassification.sh ${TARGET_DEV}"
docker run --rm -it --privileged ${TARGET_TAG} /bin/bash -c "/home/openvino/benchmark.sh ${TARGET_DEV}"
