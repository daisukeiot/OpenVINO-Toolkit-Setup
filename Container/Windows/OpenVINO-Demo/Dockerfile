#
# Pass variables with --build-arg option
# TAG_BASE  : Base OS Image
# 
ARG TAG_BASE=servercore:ltsc2019
#
# Image with OpenVINO Toolkit
#
FROM ${TAG_BASE}
ENV INTEL_OPENVINO_DIR 'C:\Program Files (x86)\IntelSWTools\openvino'

#
# Set shell to Powershell
#
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'Continue'; $verbosePreference='Continue';"]

#
# Install OpenVINO Dependencies
# Install dependencies for Model Downloader and Model Optimizer
#
RUN $INTEL_OPENVINO_DIR\bin\setupvars.bat -pyver $ENV:PYTHON_VERSION ; `
    $ENV:INTEL_OPENVINO_DIR\install_dependencies\install_openvino_dependencies.bat ; `
    python -m pip install -r $ENV:INTEL_OPENVINO_DIR\deployment_tools\open_model_zoo\tools\downloader\requirements.in ; `
    python -m pip install -r $ENV:INTEL_OPENVINO_DIR\deployment_tools\model_optimizer\requirements.txt ; `
    python -m pip install -r $ENV:INTEL_OPENVINO_DIR\inference_engine\samples\python\requirements.txt

USER openvino

#
# Run Classification Sample on CPU\GPU\MYRIAD
#
RUN echo $ENV:INTEL_OPENVINO_DIR\bin\setupvars.bat -pyver $ENV:PYTHON_VERSION > ~\verify.cmd ; `
    echo $ENV:INTEL_OPENVINO_DIR\deployment_tools\demo\demo_squeezenet_download_convert_run.bat -d >> ~\verify.cmd

#
# Run hello query device sample as sanity check
#
RUN $INTEL_OPENVINO_DIR\bin\setupvars.bat -pyver $ENV:PYTHON_VERSION ; `
    python $ENV:INTEL_OPENVINO_DIR\inference_engine\samples\python\hello_query_device\hello_query_device.py
    
WORKDIR $ENV:INTEL_OPENVINO_DIR

ENTRYPOINT []