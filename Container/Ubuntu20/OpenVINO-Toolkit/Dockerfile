
#
# Ubuntu Version
#
ARG OS_VERSION=20.04
ARG TAG_BASE
FROM ${TAG_BASE} AS base
FROM ubuntu:${OS_VERSION}

#
# Run as root user
#
USER root
WORKDIR /tmp

ARG OPENVINO_VER=2021.4.752

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
ENV INTEL_OPENVINO_DIR=/opt/intel/openvino

#
# Create user `openvino`
#
RUN useradd -ms /bin/bash -G video,users openvino && \
    chown openvino -R /home/openvino

#
# Install libraries
#
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
        curl \
        tzdata \
        g++ \
        gcc \
        libc6-dev && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*

RUN apt-get update && \
    apt-get install -y gnupg && \
    curl https://apt.repos.intel.com/openvino/2021/GPG-PUB-KEY-INTEL-OPENVINO-2021 > ./intel-key && \
    apt-key add ./intel-key

RUN echo "deb https://apt.repos.intel.com/openvino/2021 all main" | tee /etc/apt/sources.list.d/intel-openvino-2021.list && \
    apt-get update && \
    apt-get install -y intel-openvino-dev-ubuntu20-${OPENVINO_VER} && \
    ln --symbolic /opt/intel/openvino_${OPENVINO_VER}/ /opt/intel/openvino

# Use `20.35.17767` for 10th generation Intel® Core™ processor (formerly Ice Lake) or 11th generation Intel® Core™ processor (formerly Tiger Lake)
ARG OPENCL_VER=19.41.14441
WORKDIR ${INTEL_OPENVINO_DIR}/install_dependencies
RUN ./install_openvino_dependencies.sh -y -c=opencv_req -c=python -c=cl_compiler
RUN ./install_NEO_OCL_driver.sh --no_numa -y -d ${OPENCL_VER} && \
    rm -rf /var/lib/apt/lists/*


# libusb for Compute Stick
COPY --from=base /opt/libusb-1.0.22 /opt/libusb-1.0.22
WORKDIR /opt/libusb-1.0.22/libusb

RUN apt-get update && \
    apt-get install -y --no-install-recommends udev && \
    /bin/mkdir -p '/usr/local/lib' && \
    /bin/bash ../libtool --mode=install /usr/bin/install -c libusb-1.0.la '/usr/local/lib' && \
    /bin/mkdir -p '/usr/local/include/libusb-1.0' && \
    /usr/bin/install -c -m 644 libusb.h '/usr/local/include/libusb-1.0' && \
    /bin/mkdir -p '/usr/local/lib/pkgconfig' && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/libusb-1.0.22/
RUN /usr/bin/install -c -m 644 libusb-1.0.pc '/usr/local/lib/pkgconfig' && \
    cp ${INTEL_OPENVINO_DIR}/deployment_tools/inference_engine/external/97-myriad-usbboot.rules /etc/udev/rules.d/ && \
    ldconfig

# Set up python
ENV PYTHON_VER python3.8
WORKDIR /tmp
RUN ${PYTHON_VER} -m pip install --no-cache-dir cmake && \
    ${PYTHON_VER} -m pip install --no-cache-dir -r ${INTEL_OPENVINO_DIR}/python/${PYTHON_VER}/requirements.txt

#
# Change user to openvino
#
USER openvino
WORKDIR ${INTEL_OPENVINO_DIR}
ENV DEBIAN_FRONTEND=noninteractive

CMD ["/bin/bash"]
