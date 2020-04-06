ARG OPENVINO_IMAGE

FROM ${OPENVINO_IMAGE}

#
# Run as root
#
USER root

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

RUN chmod a+x /home/openvino/*.sh && \
    usermod -aG sudo openvino && \
    echo "%sudo  ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd

USER openvino
WORKDIR /home/openvino

#
# Image Classification Sample
#
RUN cd /opt/intel/openvino/deployment_tools/demo && \
    ./demo_squeezenet_download_convert_run.sh

#
# Build Benchmark C++ Tool
#
RUN cd ${INSTALLDIR}/deployment_tools/tools/model_downloader && \
    ./downloader.py --name alexnet --output /home/openvino/openvino_models/ && \
    cd ${INSTALLDIR}/deployment_tools/model_optimizer/ && \
    ./mo.py --data_type=FP16 --input_model /home/openvino/openvino_models/public/alexnet/alexnet.caffemodel -o /home/openvino/openvino_models/ir/public/alexnet/FP16/ && \
    ./mo.py --data_type=FP32 --input_model /home/openvino/openvino_models/public/alexnet/alexnet.caffemodel -o /home/openvino/openvino_models/ir/public/alexnet/FP32/ && \
    cd /home/openvino/inference_engine_samples_build/benchmark_app && \
    make

# ENTRYPOINT ["/home/openvino/imageclassification.sh"]
ENTRYPOINT []
