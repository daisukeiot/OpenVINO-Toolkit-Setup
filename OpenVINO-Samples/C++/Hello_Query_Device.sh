#!/usr/bin/env bash
#
#https://docs.openvinotoolkit.org/latest/_inference_engine_samples_hello_query_device_README.html

target_image_path="$INTEL_OPENVINO_DIR/deployment_tools/demo/car.png"
#
# Run CMake
#
sample_name=hello_query_device
samples_path="${INTEL_OPENVINO_DIR}/deployment_tools/inference_engine/samples"
build_dir="$HOME/inference_engine_samples_build"

NUM_THREADS="-j2"

OS_PATH=$(uname -m)

if [ $OS_PATH == "x86_64" ]; then
  OS_PATH="intel64"
  NUM_THREADS="-j8"
fi

binaries_dir="${build_dir}/${OS_PATH}/Release"

if  ! [ -e "${build_dir}" ]; then
        mkdir -p $build_dir
fi

if ! [ -e "$build_dir/CMakeCache.txt" ]; then
    echo "Runningn CMake"
    cd $build_dir
    cmake -DCMAKE_BUILD_TYPE=Release $samples_path
fi

cd "${build_dir}"

make $NUM_THREADS $sample_name

cd "${binaries_dir}"

./$sample_name

