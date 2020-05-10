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
ARG PYTHON_BIN=python${PYTHON_VERSION}

#
# Switch to root to install dependencies
#
USER root

#
# Switch shell
#
SHELL ["/bin/bash", "-c"] 

#
# Install OpenVINO Dependencies
# Install dependencies for Model Downloader and Model Optimizer
#
RUN source $INTEL_OPENVINO_DIR/bin/setupvars.sh -pyver ${PYTHON_VERSION} && \
    ${INTEL_OPENVINO_DIR}/install_dependencies/install_openvino_dependencies.sh && \
    python3 -m pip install -r ${INTEL_OPENVINO_DIR}/deployment_tools/open_model_zoo/tools/downloader/requirements.in && \
    python3 -m pip install -r ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer/requirements.txt && \
    ${PYTHON_BIN} -m pip install -r ${INTEL_OPENVINO_DIR}/inference_engine/samples/python/requirements.txt

USER openvino

#
# Run Classification Sample on CPU/GPU/MYRIAD
#
RUN echo ${INTEL_OPENVINO_DIR}/deployment_tools/demo/demo_squeezenet_download_convert_run.sh > ~/verify.sh && \
    chmod a+x ~/verify.sh

#
# Run hello query device sample as sanity check
#
RUN source $INTEL_OPENVINO_DIR/bin/setupvars.sh -pyver ${PYTHON_VERSION} && \
    ${PYTHON_BIN} ${INTEL_OPENVINO_DIR}/inference_engine/samples/python/hello_query_device/hello_query_device.py
    
WORKDIR /home/openvino

ENTRYPOINT ["~/verify.sh"]