#
# Pass variables with --build-arg option
# TAG_BASE  : Base OS Image
# 
ARG TAG_BASE=ubuntu:18.04
#
# Use Base image built in the previous step
#
FROM ${TAG_BASE}

#
# Local variables
#
ARG PYTHON_VERSION=3.7
ARG PYTHON=python${PYTHON_VERSION}
ARG INTEL_OPENVINO_DIR=/opt/intel/openvino

USER root
WORKDIR ${INTEL_OPENVINO_DIR}

#
# Install OpenVINO Dependencies
#
RUN alias python3="${PYTHON}" && \
    cd install_dependencies && \
    ./install_openvino_dependencies.sh

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
# Run Classification Sample
#
WORKDIR ${INTEL_OPENVINO_DIR}/deployment_tools/demo
RUN ./demo_squeezenet_download_convert_run.sh -d CPU
#
# Run hello query device sample
#
WORKDIR ${INTEL_OPENVINO_DIR}/inference_engine/samples/python
RUN /bin/bash -c "source $INTEL_OPENVINO_DIR/bin/setupvars.sh -pyver ${PYTHON_VERSION} && \
    ${PYTHON} ./hello_query_device/hello_query_device.py"
    
WORKDIR ${INTEL_OPENVINO_DIR}

ENTRYPOINT []