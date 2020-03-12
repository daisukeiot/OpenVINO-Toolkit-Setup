docker system prune -a -f
./build-BaseOS.sh $1
./build-OpenVINO-Toolkit.sh $1