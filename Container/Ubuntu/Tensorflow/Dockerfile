#
# Pass variables with --build-arg option
# TAG_TF         : A container with Tensorflow Package
# TAG_BASE       : Base Image to install Tensorflow
# PYTHON_VERSION : Python version to use to install Tensorflow
#
ARG TAG_TF=
ARG TAG_BASE=ubuntu:18.04

# Container image containing Tensorflow wheel package
FROM ${TAG_TF} as TensorFlow

FROM ${TAG_BASE}

#
# Local variables
#
ARG PYTHON_BIN=python${PYTHON_VERSION}

#
# Run as root to install Tensorflow Pacakge
#
USER root
WORKDIR /tmp

#
# Copy Tensorflow Wheel Package
#
COPY --from=TensorFlow /*.whl .

#
# Install Tensorflow Package
#
RUN ${PYTHON_BIN} -m pip install ./*.whl && \
    rm -rf /tmp/*

#
# Switch user to openvino and current directory to /home/openvino
#
USER openvino
WORKDIR /home/openvino