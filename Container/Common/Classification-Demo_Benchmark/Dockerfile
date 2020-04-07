ARG OPENVINO_IMAGE

FROM ${OPENVINO_IMAGE}

#
# Run as root
#
USER root

ENV INTEL_OPENVINO_DIR=/opt/intel/openvino

#
# Install sudo
#
RUN apt-get update && \
    apt install -y --no-install-recommends sudo && \
    rm -rf /var/lib/apt/lists/*

# RUN adduser --home /home/openvino --disabled-password --gecos '' openvino && \
#    usermod -aG sudo openvino && \
#    echo "%sudo  ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd && \
#    usermod -aG video openvino

COPY ./imageclassification.sh /home/openvino/imageclassification.sh
COPY ./benchmark.sh /home/openvino/benchmark.sh
COPY ./hello_device.sh /home/openvino/hello_device.sh

RUN chmod a+x /home/openvino/*.sh && \
    usermod -aG sudo openvino && \
    echo "%sudo  ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd

RUN cd ${INTEL_OPENVINO_DIR}/install_dependencies && \
    ./install_NCS_udev_rules.sh

USER openvino
WORKDIR /home/openvino

# Image Classification Sample
#
RUN cd ${INTEL_OPENVINO_DIR}/deployment_tools/demo && \
    ./demo_squeezenet_download_convert_run.sh

#
# Build Benchmark C++ Tool
#
RUN cd ${INTEL_OPENVINO_DIR}/deployment_tools/tools/model_downloader && \
    ./downloader.py --name alexnet --output /home/$USER/openvino_models/ && \
    cd ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer/ && \
    ./mo.py --data_type=FP16 --input_model /home/$USER/openvino_models/public/alexnet/alexnet.caffemodel -o /home/$USER/openvino_models/ir/public/alexnet/FP16/ && \
    ./mo.py --data_type=FP32 --input_model /home/$USER/openvino_models/public/alexnet/alexnet.caffemodel -o /home/$USER/openvino_models/ir/public/alexnet/FP32/ && \
    cd /home/$USER/inference_engine_samples_build/benchmark_app && \
    make

RUN cd ${INTEL_OPENVINO_DIR}/bin && \
    ./setupvars.sh && \
    cd ${INTEL_OPENVINO_DIR}/inference_engine/samples/python_samples/hello_query_device && \
    python3 ./hello_query_device.py

# ENTRYPOINT ["/home/openvino/imageclassification.sh"]
ENTRYPOINT []
