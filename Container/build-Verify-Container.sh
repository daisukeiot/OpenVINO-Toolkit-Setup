if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify Container"
    echo "  Example ./verify-container.sh myregistry/container:tag"
    echo "======================================="
    exit
fi

CONTAINER_OS=$(lsb_release -si)

#
# Build Container with verification script
# Built container but do not push to registry
#
SCRIPT_DIR=$(cd $(dirname $0); pwd)
TAG=$1
TARGET_TAG=$1_verify
docker build --squash --rm -f \
    ${SCRIPT_DIR}/Common/Classification-Demo_Benchmark/Dockerfile \
    -t ${TARGET_TAG} \
    --build-arg OPENVINO_IMAGE=${TAG} \
    --build-arg CONTAINER_OS=${CONTAINER_OS} \
    ${SCRIPT_DIR}/Common/Classification-Demo_Benchmark

docker run --rm --privileged -v /dev:/dev --network=host ${TARGET_TAG} /home/openvino/hello_device.sh

echo "============================================================================================================="
echo "Container built with Tag : "
echo ${TARGET_TAG}
echo "Run verification with :"
echo "docker run --rm --privileged -v /dev:/dev --network=host ${TARGET_TAG} /home/openvino/hello_device.sh"
echo "docker run --rm --privileged -v /dev:/dev --network=host ${TARGET_TAG} /home/openvino/imageclaasification.sh"
echo "docker run --rm --privileged -v /dev:/dev --network=host ${TARGET_TAG} /home/openvino/benchmark.sh"