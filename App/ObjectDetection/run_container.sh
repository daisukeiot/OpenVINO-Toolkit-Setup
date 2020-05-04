if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify the container image"
    echo "  Example "
    echo "./run_container.sh daisukeiot/openvino-container:ubuntu18.04_openvino2020.2.120_cp3.7_app"
    echo "======================================="
    exit
fi

docker run -it --rm --name python_app \
    --device-cgroup-rule='c 189:* rmw' \
    -v /dev/bus/usb:/dev/bus/usb \
    --device /dev/dri \
    -v ${HOME}/data:/home/openvino/data \
    -p 8080:8080 \
    $1