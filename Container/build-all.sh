if [ $# -eq 0 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version"
    echo "18.04 or 16.04"
    echo "======================================="
    exit
fi
./build-BaseOS.sh $1
./build-OpenVINO-Toolkit.sh $1