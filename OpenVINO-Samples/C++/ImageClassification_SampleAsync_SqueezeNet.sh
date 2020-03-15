#!/usr/bin/env bash
#
#https://docs.openvinotoolkit.org/latest/_inference_engine_samples_classification_sample_async_README.html

target_image_path="$INTEL_OPENVINO_DIR/deployment_tools/demo/car.png"
#
# Run CMake
#
sample_name=classification_sample_async
model_name="squeezenet1.1"
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

#
# Download Model
#
optimizer_path="${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer"

#
# Install Model Optimizer dependencies
#
cd "$optimizer_path/install_prerequisites"
sudo ./install_prerequisites.sh

#
# Run Model Downloader
#
downloader_path="${INTEL_OPENVINO_DIR}/deployment_tools/open_model_zoo/tools/downloader"
model_path="$HOME/openvino_models/models"

if ! [ -e "${model_path}/public/${model_name}" ]; then
  cd $downloader_path
  "$downloader_path/downloader.py" --name "$model_name" --output_dir "${model_path}"
fi

#
# Run Model Optimizer
#
model_cache="$HOME/openvino_models/cache"
ir_path="$HOME/openvino_models/ir"
target_precision="FP16"

if ! [ -e "${ir_path}/public/${model_name}/$target_precision/${model_name}.xml" ]; then
    python3 "$downloader_path/converter.py" --mo "$optimizer_path/mo.py" --name "$model_name" -d "$model_path" -o "$ir_path" --precisions "$target_precision"
fi

cd "${binaries_dir}"

#
# Run Sample for FP16
#
target_device="CPU"
echo '#############################################################'
echo "${model_name} ${target_precision}" on ${target_device}
echo '#############################################################'
./$sample_name -d ${target_device} -i "$target_image_path" -m "${ir_path}/public/${model_name}/$target_precision/${model_name}.xml"

target_device="GPU"
echo '#############################################################'
echo "${model_name} ${target_precision}" on ${target_device}
echo '#############################################################'
./$sample_name -d ${target_device} -i "$target_image_path" -m "${ir_path}/public/${model_name}/$target_precision/${model_name}.xml"

target_device="MYRIAD"
echo '#############################################################'
echo "${model_name} ${target_precision}" on ${target_device}
echo '#############################################################'
./$sample_name -d ${target_device} -i "$target_image_path" -m "${ir_path}/public/${model_name}/$target_precision/${model_name}.xml"


#
# Run Sample for FP32
#
target_precision="FP32"

if ! [ -e "${ir_path}/public/${model_name}/$target_precision/${model_name}.xml" ]; then
    python3 "$downloader_path/converter.py" --mo "$optimizer_path/mo.py" --name "$model_name" -d "$model_path" -o "$ir_path" --precisions "$target_precision"
fi

cd "${binaries_dir}"

#
# Run Sample for FP16
#
target_device="CPU"
echo '#############################################################'
echo "${model_name} ${target_precision}" on ${target_device}
echo '#############################################################'
./$sample_name -d ${target_device} -i "$target_image_path" -m "${ir_path}/public/${model_name}/$target_precision/${model_name}.xml"

target_device="GPU"
echo '#############################################################'
echo "${model_name} ${target_precision}" on ${target_device}
echo '#############################################################'
./$sample_name -d ${target_device} -i "$target_image_path" -m "${ir_path}/public/${model_name}/$target_precision/${model_name}.xml"
