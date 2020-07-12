# Ubuntu Development Environment

Verified with :

- Ubuntu 18.04
- Python 3.7.5
- OpenVINO 2020.3.194

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

> [!IMPORTANT]  
> Make sure your CPU supports AVX.  Tensorflow v1.15 or above is compiled with AVX support turned on.  
> If AVX is not available, install Tensorflow without AVX by following [this instruction](../UP2/README.md#tensorflow-without-avx).
> To check your CPU's capabilities, run :
>
> ```bash
> lscpu | grep avx
> Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid mpx rdseed adx smap clflushopt intel_pt xsaveopt xsavec xgetbv1 xsaves dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp md_clear flush_l1d
> ```

### Reference : OpenVINO Toolkit installation by Intel

Instruction for OpenVINO Toolkit Setup

[Install Intel® Distribution of OpenVINO™ toolkit for Linux](https://docs.openvinotoolkit.org/2020.2/_docs_install_guides_installing_openvino_linux.html)

## OpenVINO Toolkit Verification

The verification script will test :

- Model Downloader
- Model Optimizer
- OpenVINO inference on CPU, GPU, and MYRIAD

```bash
cd ~/OpenVINO-Toolkit-Setup/Setup/Ubuntu && \
./verification.sh
```

More info : [Run the Verification Scripts to Verify Installation](https://docs.openvinotoolkit.org/2020.2/_docs_install_guides_installing_openvino_linux.html#run-the-demos)

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

### Azure IoT Edge Configuration

- [Install the Azure IoT Edge runtime on Debian-based Linux systems](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-linux)

## Next Step

[Run Object Detection Python App](../../README.md#running-object-detection-python-app)