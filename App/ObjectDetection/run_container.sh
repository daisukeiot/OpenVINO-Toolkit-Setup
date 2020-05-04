if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify the container image"
    echo "  Example "
    echo "./run_container.sh daisukeiot/openvino-container:ubuntu18.04_openvino2020.2.120_cp3.7_app"
    echo "======================================="
    exit
fi

docker run -it --rm \
    -device-cgroup-rule='c 189:* rmw' \
    -v /dev/bus/usb:/dev/bus/usb \
    -v ${HOME}/data:/home/openvino/data \
    --device /dev/dri \
    -p 8080:8080 \
    $1