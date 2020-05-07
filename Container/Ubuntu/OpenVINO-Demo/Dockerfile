#
# Pass variables with --build-arg option
# TAG_BASE  : Base OS Image
# 
ARG TAG_BASE=ubuntu:18.04
#
# Image with OpenVINO Toolkit
#
FROM ${TAG_BASE}

#
# Local variables
#
ARG INTEL_OPENVINO_DIR=/opt/intel/openvino
ARG PYTHON=python${PYTHON_VERSION}
#
# Switch to root to install dependencies
#
USER root
WORKDIR ${INTEL_OPENVINO_DIR}

#
# Install OpenVINO Dependencies
#
RUN alias python3="${PYTHON}" && \
    python3 --version && \
    cd install_dependencies && \
    ./install_openvino_dependencies.sh

#
# Install dependencies for Model Downloader and Model Optimizer
#
RUN ${PYTHON} -m pip install -r ${INTEL_OPENVINO_DIR}/deployment_tools/open_model_zoo/tools/downloader/requirements.in && \
    ${PYTHON} -m pip install -r ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer/requirements.txt && \
    ${PYTHON} -m pip install -r ${INTEL_OPENVINO_DIR}/inference_engine/samples/python/requirements.txt && \
    apt-get update && \
    apt install -y --no-install-recommends \
        python3-yaml \
        python3-requests && \
    rm -rf /var/lib/apt/lists/*

USER openvino
#
# Run Classification Sample on CPU/GPU/MYRIAD
#
WORKDIR ${INTEL_OPENVINO_DIR}/deployment_tools/demo
RUN echo ${INTEL_OPENVINO_DIR}/deployment_tools/demo/demo_squeezenet_download_convert_run.sh -d CPU > ~/cpu.sh && \
    echo ${INTEL_OPENVINO_DIR}/deployment_tools/demo/demo_squeezenet_download_convert_run.sh -d GPU > ~/gpu.sh && \
    echo ${INTEL_OPENVINO_DIR}/deployment_tools/demo/demo_squeezenet_download_convert_run.sh -d MYRIAD > ~/vpu.sh && \
    chmod a+x ~/*.sh
#
# Run hello query device sample as sanity check
#
WORKDIR ${INTEL_OPENVINO_DIR}/inference_engine/samples/python
RUN /bin/bash -c "source $INTEL_OPENVINO_DIR/bin/setupvars.sh -pyver ${PYTHON_VERSION} && \
    ${PYTHON} ./hello_query_device/hello_query_device.py"
    
WORKDIR ${INTEL_OPENVINO_DIR}

ENTRYPOINT []