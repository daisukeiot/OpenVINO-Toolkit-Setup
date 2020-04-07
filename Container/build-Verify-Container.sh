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

echo ''
echo 'Container Built'
echo 'Run Hello World to check available hardware'
echo "docker run --rm ${TARGET_TAG} /home/openvino/hello_world.sh"
echo ''