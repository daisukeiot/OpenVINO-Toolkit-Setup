ARG OPENVINO_IMAGE

FROM ${OPENVINO_IMAGE}

#
# Run as root
#
USER root

ARG CONTAINER_OS
ENV INTEL_OPENVINO_DIR=/opt/intel/openvino

#
# Install sudo
#
RUN apt-get update && \
    apt-get install -y --no-install-recommends sudo && \
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

ENTRYPOINT []
