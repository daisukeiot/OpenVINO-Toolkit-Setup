# Raspberry Pi Development Environment

Verified with :

- Raspbian Buster (2020-02-13-raspbian-buster-lite)
- Python 3.7.5

## Clone the repo

Clone to Raspberry Pi with :

```cmd
cd ~ && \
sudo apt-get update && \
sudo apt-get install -y git && \
git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git
```

## OpenVINO Toolkit Setup

Run setup script to setup OS and install OpenVINO Toolkit with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Setup/Raspbian && \
./setup.sh
```

> [!NOTE]  
> The script will change hostname to RP-OpenVINO

### OpenVINO Toolkit installation by Intel

Detailed instruction for OpenVINO Toolkit Setup

[Install OpenVINO™ toolkit for Raspbian OS](https://docs.openvinotoolkit.org/2020.2/_docs_install_guides_installing_openvino_raspbian.html)

## OpenVINO Toolkit Verification

Run Object Detection Sample with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Setup/Raspbian && \
./verification.sh
```

More info : [Build and Run Object Detection Sample](https://docs.openvinotoolkit.org/2020.2/_docs_install_guides_installing_openvino_raspbian.html#run-sample)

## Container Runtime Setup

If you are planning to run containerized OpenVINO application, install Docker or Moby :

### Raspberry Pi3 + Raspbian Stretch

Install Moby runtime with :

```bash
sudo apt-get install -y curl && \
curl https://packages.microsoft.com/config/debian/stretch/multiarch/prod.list > ./microsoft-prod.list && \
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

### Raspbian Buster

```bash
curl -sSL get.docker.com | sh && \
sudo usermod pi -aG docker && \
sudo reboot now
```

### Azure IoT Edge Configuration

If you plan to run IoT Edge, install IoT Edge runtime with :

```bash
sudo apt-get install -y libssl1.0.2 && \
curl https://packages.microsoft.com/config/debian/stretch/multiarch/prod.list > ./microsoft-prod.list && \
sudo cp ./microsoft-prod.list /etc/apt/sources.list.d/ && \
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
sudo cp ./microsoft.gpg /etc/apt/trusted.gpg.d/ && \
sudo apt-get update && \
sudo apt-get -y install iotedge && \
rm ./microsoft*
```

- [Install the Azure IoT Edge runtime on Debian-based Linux systems](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-linux#install-the-container-runtime)

## Next Step

