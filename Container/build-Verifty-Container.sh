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
TAG=$1
TARGET_TAG=$1_verify
docker build --squash --rm -f ./Common/Classification-Demo_Benchmark/Dockerfile -t ${TARGET_TAG} --build-arg OPENVINO_IMAGE=${TAG} ./Common/Classification-Demo_Benchmark

docker run --rm -it ${TARGET_TAG} /bin/bash /home/openvino/verify.sh
docker run --rm -it ${TARGET_TAG} /bin/bash /home/openvino/benchmark.sh
