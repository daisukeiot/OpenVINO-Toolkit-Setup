if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify Container"
    echo "  Example ./verify-container.sh myregistry/container:tag"
    echo "======================================="
    exit
fi

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
    ${SCRIPT_DIR}/Common/Classification-Demo_Benchmark