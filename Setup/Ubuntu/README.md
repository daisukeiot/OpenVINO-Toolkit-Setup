# Ubuntu Development Environment

Verified with :

- Ubuntu 18.04
- Python 3.7.5
- OpenVINO 2020.2.120

## Clone repo

```bash
sudo apt update && \
sudo apt-get install -y git && \
git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git && \
cd ./OpenVINO-Toolkit-Setup/Setup/Ubuntu
```

## OpenVINO Toolkit Setup

Run setup script to setup OS and install OpenVINO Toolkit with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Setup/Ubuntu && \
./setup.sh
```

## OpenVINO Toolkit Verification

The verification script will test :

- Model Downloader
- Model Optimizer
- OpenVINO inference on CPU, GPU, and MYRIAD

```bash
cd ~/OpenVINO-Toolkit-Setup/Setup/Ubuntu && \
./verification.sh
```

## Container Runtime Setup

If you are planning to run containerized OpenVINO application, install Docker or Moby :

Install Moby runtime with :

```bash
sudo apt-get install -y curl && \
curl https://packages.microsoft.com/config/ubuntu/18.04/multiarch/prod.list > ./microsoft-prod.list && \
sudo cp ./microsoft-prod.list /etc/apt/sources.list.d/ && \
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
sudo cp ./microsoft.gpg /etc/apt/trusted.gpg.d/ && \
sudo apt-get update && \
sudo apt-get install -y moby-engine && \
sudo apt-get install -y moby-cli && \
sudo usermod -aG docker $USER && \
rm ./microsoft* && \
sudo reboot now
```

If you plan to run IoT Edge, install IoT Edge runtime with :

```bash
sudo apt-get update && \
sudo apt-get install iotedge
```

### Reference

- [Install the Azure IoT Edge runtime on Debian-based Linux systems](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-linux)
