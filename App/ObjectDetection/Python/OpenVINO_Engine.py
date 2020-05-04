import sys
import logging
import os
import json
from openvino.inference_engine import IECore, IENetwork
from OpenVINO_Config import Engine_State, Model_Flag, OpenVINO_Model_Data
from OpenVINO_Core import OpenVINO_Core
import subprocess
from pathlib import Path
import yaml
import cv2
import time

class OpenVINO_Util(object):

    def __init__(self):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

    def __enter__(self):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

    def get_supported_devices(self):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        ie = IECore()

        # for device in ie.available_devices:
        #     logging.info('>> Device : {0}'.format(device))

        return ie.available_devices

    def get_device_name(self, device):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        value = ""
        ie = IECore()

        metrics = ie.get_metric(device, "SUPPORTED_METRICS")

        if 'FULL_DEVICE_NAME' in metrics:
            value = ie.get_metric(device, 'FULL_DEVICE_NAME')

        return value

class OpenVINO_Engine(object):

    def __init__(self, videoProcessor):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self._debug = True

        self.videoProcessor = videoProcessor
        self.signature = 'OpenVINO'
        self.engineState = Engine_State.Unknown

        self._inference_Core = None

        self._target_device = 'MYRIAD'
        self._precision = 'FP32'
        self._confidence = 0.8

        self.current_model_data = None

        # list of models from Open Model Zoo
        self.modelList = []

        # set path for OpenVINO Toolkit from INTEL_OPENVINO_DIR environment variable (/opt/intel/openvino)
        self.openvino_dir = None

        # location to download public model files
        self.model_dir = None

        # location to save IR files
        self.ir_dir = None

        self.useModelsJson = True

    def __enter__(self):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        
        self.initialize_engine()

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.engineState = Engine_State.Unknown

    def initialize_engine(self):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        # check if OpenVINO Toolkit is installed for model downloader and model optimizer
        if os.environ['INTEL_OPENVINO_DIR'] is not None:
            openvino_path = Path(os.environ['INTEL_OPENVINO_DIR']).resolve()
            self.openvino_dir = openvino_path

            if openvino_path.exists():
                self.openvino_path = openvino_path
                self.engineState |= Engine_State.Has_OpenVINO_Tool

        data_dir = Path(Path.home() / 'data')
        if not data_dir.exists():
            # create model folder
            data_dir.mkdir(mode=0o777)
            data_dir.chmod(0o777)

        # make sure model folder exists
        self.model_dir = Path(data_dir / 'model')

        if not self.model_dir.exists():
            # create model folder
            self.model_dir.mkdir(mode=0o777)
            self.model_dir.chmod(0o777)

        # make sure ir folder exists
        self.ir_dir = Path(data_dir / 'ir')

        if not self.ir_dir.exists():
            # create ir folder
            self.ir_dir.mkdir(mode=0o777) 
            self.ir_dir.chmod(0o777)

        if self.isFlagSet(Engine_State.Has_OpenVINO_Tool) and not self.useModelsJson:
            if self._debug:
                logging.info('>> Creating Model List')

            # create list of models from the toolkit
            p_model = (Path(self.openvino_path / 'deployment_tools' / 'open_model_zoo' / 'models').resolve())

            self.modelList.clear()

            if p_model.exists():
                # iterate through model.yml files
                for yaml_file in sorted(p_model.glob('**/model.yml')):
                    model_framework = ""
                    model_file = ""
                    model_archive_format = ""
                    model_folder = yaml_file.parent.relative_to(p_model)
                    model_flag = Model_Flag.Uninitialized
                    # open model.yml file
                    with yaml_file.open('rb') as f:
                        yaml_content = yaml.load(f)
                        model_framework = yaml_content['framework']
                        model_postprocs = yaml_content.get('postprocessing')
                        model_files = yaml_content.get('files')

                        if model_files:
                            for item in model_files:
                                if model_framework == 'caffe':
                                    if '.caffemodel' in item['name']:
                                        model_file = item['name']
                                elif model_framework == 'tf':
                                    if '.pb' in item['name']:
                                        model_file = item['name']
                                elif model_framework == 'dtdl':
                                    if '.bin' in item['name']:
                                        model_file = item['name']

                        if model_postprocs:
                            for model_postproc in model_postprocs:
                                if model_postproc['$type'] == 'unpack_archive':
                                    model_flag = Model_Flag.HasPostProc
                                    model_file = model_postproc['file']
                                    model_archive_format = model_postproc['format']

                        model_data = OpenVINO_Model_Data(modelName = model_folder.name, 
                                                         folderName = str(model_folder), 
                                                         framework = model_framework, 
                                                         task_type = yaml_content['task_type'], 
                                                         model_file = model_file, 
                                                         archive_format = model_archive_format,
                                                         flag = model_flag)

                        model_data.dump_model_data()
                        self.modelList.append(model_data)
        else:
            # process Json file for models

            models_json_file = Path(Path('./').resolve() / 'models.json')

            if models_json_file.exists():

                with models_json_file.open() as json_file:

                    json_data = json.load(json_file)

                    for model in json_data['Models']:
                        isSupported = False

                        # Yolo v3 has 3 outputs
                        if model['outputs']['count'] > 3:
                            continue

                        for output_blob in model['outputs']['blobs']:
                            if output_blob.get('output_type') is None:
                                continue

                            # We understand Detection Output (Object Detection)
                            if output_blob['output_type'] == 'DetectionOutput':

                                if model['inputs']['count'] == 1:
                                    # most of models are only 1 input
                                    isSupported = True

                                elif model['inputs']['count'] == 2:
                                    # faster RCNN has 2 inputs

                                    data_found = False
                                    info_found = False

                                    # look for image_info and image_tensor inputs
                                    for input_blob in model['inputs']['blobs']:
                                        if input_blob['input_name'] == 'image_info':
                                            info_found = True
                                        elif input_blob['input_name'] == 'image_tensor':
                                            data_found = True

                                    if data_found == True and info_found == True:
                                        isSupported = True

                            elif output_blob['output_type'] == 'RegionYolo':
                                isSupported = True

                        if isSupported == True:
                            model_data = OpenVINO_Model_Data(modelName = model['name'], 
                                                            folderName = model['path'],
                                                            framework = model['framework'],
                                                            task_type = "", 
                                                            model_file = model['name'],
                                                            archive_format = "",
                                                            flag = Model_Flag.Uninitialized)

                            self.modelList.append(model_data)

        if self.openvino_dir.exists() and self.model_dir.exists() and self.ir_dir.exists() and len(self.modelList) > 0:

            logging.info('OpenVINO Engine initialized')

            self._inference_Core = OpenVINO_Core()

            self.signature = self._inference_Core.get_signature()

            self.engineState |= Engine_State.Initialized
        else:
            logging.error('OpenVINO Engine initialization failed')

#
# Helper functions / macros
#
    def setFlag(self, flag):
        self.engineState |= flag

    def clearFlag(self, flag):
        self.engineState |= ~flag

    def isFlagSet(self, flag):
        return ((self.engineState & flag) == flag)

    def get_devices(self):
        return self._inference_Core.devices

    def get_model_list(self):
        return self.modelList

    def remove_dir(self, path_to_remove):
        for f in path_to_remove.glob('**/*'):
            if f.is_file():
                f.unlink()
            else:
                self.remove_dir(f)

        path_to_remove.rmdir()

# Set target hardware to run inference on
#
    def set_target_device(self, target):
        if self._debug:
            logging.info('>> {0}:{1}() : {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, target))

        json_data = json.loads(target)

        target_device = json_data["set_target_device"]

        if target_device in self._inference_Core.devices:
            self._target_device = target_device
            return self.get_target_device()
        else:
            logging.error('{} is not in the supported device'.format(target_device))
            return '{{\"{}\":\"{} not in the supported device\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name, target_device)
#
# Return target hardware inference is running
#
    def get_target_device(self):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self._target_device in self._inference_Core.devices:
            return '{{\"{}\":\"{}\"}}'.format(sys._getframe().f_code.co_name, self._target_device)
        else:
            device = self._inference_Core.devices[0]
            if device == 'CPU':
                precision = 'FP32'
            else:
                precision = 'FP16'
            return '{{\"{}\":\"{}\",\"get_precision\":\"{}\"}}'.format(sys._getframe().f_code.co_name, device, precision)

#
# Set precision (FP16, FP32)
#
    def set_precision(self, target):
        if self._debug:
            logging.info('>> {0}:{1}() : {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, target))

        json_data = json.loads(target)

        self._precision = json_data["set_precision"]
        return self.get_precision()

#
# Return current precision (FP16, FP32)
#
    def get_precision(self):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return '{{\"{}\":\"{}\"}}'.format(sys._getframe().f_code.co_name, self._precision)

#
# Set confidence level threshold
#
    def set_confidence_level(self, confidenceLevel):
        if self._debug:
            logging.info('>> {0}:{1}() : {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, confidenceLevel))

        self._confidence = (confidenceLevel / 100)

        return self.get_confidence_level()
#
# return confidence level threshold
#
    def get_confidence_level(self):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return '{{\"{}\":\"{}\"}}'.format(sys._getframe().f_code.co_name, (self._confidence * 100))

#
# Remove a model folder
#
    def remove_model_dir(self, model_data):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        logging.info('>> Model dir {}'.format(model_data.model_dir))

        if not model_data.framework == 'dldt' and model_data.model_dir != None:
            self.remove_dir(model_data.model_dir)
            model_data.model_dir = None

#
# Search XML and BIN files
# Look for ./ir/<Intel or Public>/<Model Name>/<FP16 or FP32>/<Model Name>.bin/.xml
#
    def search_ir_dir(self, model_data):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        # look for XML file
        model_xml_file = []
        for xml_file in self.ir_dir.glob('**/{}.{}'.format(model_data.modelName, 'xml')):
            model_xml_file.append(xml_file)

        # look for BIN file
        model_bin_file = []
        for bin_file in self.ir_dir.glob('**/{}.{}'.format(model_data.modelName, 'bin')):
            model_bin_file.append(bin_file)

        if len(model_bin_file) == 0 or len(model_xml_file) == 0:
            logging.info('IR files not found {} {}'.format(model_data.modelName, model_data.framework))
        else:
            logging.info('IR files found {} {}'.format(model_data.modelName, model_data.framework))
            FP16_dir = None
            FP32_dir = None

            for xml_file in model_xml_file:
                if 'FP16' == str(xml_file.parent.stem):
                    FP16_dir = xml_file.parent
                elif 'FP32' == str(xml_file.parent.stem):
                    FP32_dir = xml_file.parent

            # sanity check
            assert (Path(FP16_dir / '{}.bin'.format(model_data.modelName)).exists()), "FP16 BIN file missing"
            assert (Path(FP16_dir / '{}.xml'.format(model_data.modelName)).exists()), "FP16 XML file missing"
            assert (Path(FP32_dir / '{}.bin'.format(model_data.modelName)).exists()), "FP32 BIN file missing"
            assert (Path(FP32_dir / '{}.xml'.format(model_data.modelName)).exists()), "FP32 XML file missing"

            model_data.ir_dir = dict({'FP16':FP16_dir, 'FP32':FP32_dir})

            model_data.setFlag(Model_Flag.Downloaded | Model_Flag.Converted) 

        return model_data

#
# Search a folder with a given model name
# For public model, look for ./model/public/<Model Name>
# For Intel model, look for ./ir/Intel/<Model Name>
#
    def search_model_dir(self, model_data):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        model_folder_name = ""

        if model_data.framework == 'dldt':
            return self.search_ir_dir(model_data)
        else:
            p_download_dir = self.model_dir
            model_folder_name = model_data.model_file

            if model_data.archive_format == "gztar":
                # remove .gz.tar
                model_folder_name = Path(model_folder_name).stem               
                model_folder_name = Path(model_folder_name).stem               

            elif model_data.archive_format == "tar" or model_data.archive_format == "zip":
                # remote .zip or .tar
                model_folder_name = Path(model_folder_name).stem               

        # look for a folder in download folder
        model_dir = None
        tmp = '**/{}'.format(model_folder_name)

        # for download_dir in p_download_dir.glob('**/{}'.format(model_folder_name)):
        for download_dir in p_download_dir.glob(tmp):
            #assert(model_dir is None, "Multiple folders found")
            model_dir = download_dir

        # make sure the folder exists
        if model_dir is not None:
            logging.info('>> Downloaded model found {}'.format(str(model_dir)))
            if not model_data.framework == 'dldt':
                model_data.model_dir = model_dir
            else:
                model_data.ir_dir = model_dir

            model_data.flag |= Model_Flag.Downloaded
            model_dir.chmod(0o777)

        return model_data

#
# Search a folder with a given model name
# For public model, look for ./model/public/<Model Name>
# For Intel model, look for ./ir/Intel/<Model Name>
# If model is already downloaded, look for ./ir folder
#
    def search_model(self, model_data):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        assert isinstance(model_data, OpenVINO_Model_Data), "Invalid Model Data"

        if model_data.framework == 'dldt' or model_data.isFlagSet(Model_Flag.Downloaded):
            return self.search_ir_dir(model_data)
        else:
            return self.search_model_dir(model_data)

#
# Download Model using model downloader
# Saves model files into ./model folder
# If the model is Intel model (IR) then into ./ir folder
#
    def download_model(self, model_data):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        assert isinstance(model_data, OpenVINO_Model_Data), "Invalid Model Data"

        logging.info('Model Name       : {}'.format(model_data.modelName))
        logging.info('  Framework Type : {}'.format(model_data.framework))
        logging.info('    Archive Type : {}'.format(model_data.archive_format))
        logging.info('    Archive File : {}'.format(model_data.model_file))

        model_data.errorMsg = ""

        # check if we already have IR files
        model_data = self.search_ir_dir(model_data)

        if not model_data.isFlagSet(Model_Flag.Converted):
            # check if the model is already downloaded
            model_data = self.search_model(model_data)

        if model_data.isFlagSet(Model_Flag.Downloaded):
            if model_data.framework == 'dldt':
                logging.info('   Model Folder found {}'.format(str(model_data.ir_dir)))
            else:
                logging.info('   Model Folder found {}'.format(str(model_data.model_dir)))
        else:
            logging.info('>> {0}:{1}() Model Folder not found'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

            if not self.isFlagSet(Engine_State.Has_OpenVINO_Tool):
                model_data.errorMsg = 'OpenVINO Toolkit not installed'
                logging.warning('>> {0}:{1}() : {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, model_data.errorMsg))
                return model_data

            # p_downloader =  (Path(self.openvino_path / 'deployment_tools' / 'tools' / 'model_downloader' / 'downloader.py').resolve())
            p_downloader =  Path(Path('./').resolve() / 'open_model_zoo/tools/downloader/downloader.py').resolve()

            if not p_downloader.exists():
                model_data.errorMsg = 'Model Downloader not installed'
                logging.warning('>> {0}:{1}() : {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, model_data.errorMsg))
                return model_data

            # setup download logfile
            logfile = Path(self.model_dir / 'download.json')

            if logfile.exists():
                logfile.unlink()

            # download target folder
            if model_data.framework == 'dldt':
                p_target_dir = self.ir_dir
            else:
                p_target_dir = self.model_dir

            # download
            downloader_cmd = 'python3.7 {} --name {} --output_dir {} --progress_format json > {}'.format(str(p_downloader), model_data.modelName, str(p_target_dir), str(logfile))
            if self._debug:
                logging.info(downloader_cmd)                

            logging.info('>> Download {}'.format(model_data.modelName))
            os.system(downloader_cmd)
            logging.info('<< Download {}'.format(model_data.modelName))

            # Log file looks like this
            # {"$type": "model_download_begin", "model": "action-recognition-0001-decoder", "num_files": 4}
            # {"$type": "model_file_download_begin", "model": "action-recognition-0001-decoder", "model_file": "FP32/action-recognition-0001-decoder.xml", "size": 104114}
            # {"$type": "model_file_download_progress", "model": "action-recognition-0001-decoder", "model_file": "FP32/action-recognition-0001-decoder.xml", "size": 104114}
            # {"$type": "model_file_download_end", "model": "action-recognition-0001-decoder", "model_file": "FP32/action-recognition-0001-decoder.xml", "successful": true}
            #     :
            # {"$type": "model_file_download_end", "model": "action-recognition-0001-decoder", "model_file": "FP16/action-recognition-0001-decoder.bin", "successful": true}
            # {"$type": "model_download_end", "model": "action-recognition-0001-decoder", "successful": true}
            
            num_files = 0
            file_count = 0
            download_result = False

            with logfile.open('r') as f:
                for line in f:
                    line_json = json.loads(line)

                    if line_json.get('$type'):
                        if line_json['$type'] == 'model_download_begin':
                            num_files = line_json['num_files']

                        if line_json['$type'] == 'model_download_end':
                            download_result = line_json['successful']

                        if line_json['$type'] == 'model_file_download_end':
                            if line_json['successful'] == True:
                                file_count += 1
                            else:
                                logging.error('File {} fail'.format(line_json['model_file']))

                            # # check if download was success
                            # if download_result != True:
                            #     download_success = False
                            #     logging.error('Download failed {}'.format(str(download_file_name)))
                            # else:
                            #     logging.info('Download success {}'.format(str(download_file_name)))

            if num_files == file_count and download_result is True:
                # check folder.  This will set Downloaded flag if a folder is found
                self.search_model_dir(model_data)
            else:
                model_data.errorMsg = "Model download failed"

        return model_data

#
# Convert Model using Model Optimizer
# IR files are saved into ./ir folder
#
    def convert_model(self, model_data):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        assert isinstance(model_data, OpenVINO_Model_Data), "Invalid Model Data"

        model_data.errorMsg = ""

        if not model_data.isFlagSet(Model_Flag.Downloaded):
            logging.warning('>> {0}:{1}() Model {2} not downloaded'.format(self.__class__.__name__, sys._getframe().f_code.co_name, model_data.modelName))
            return model_data

        if model_data.framework == 'dldt':
            logging.warning('>> {0}:{1}() DLDT Model {2} does not need conversion'.format(self.__class__.__name__, sys._getframe().f_code.co_name, model_data.modelName))
            return model_data

        # check model/ir folder
        model_data = self.search_model(model_data)

        if model_data.isFlagSet(Model_Flag.Converted):
            logging.info('>> {0}:{1}() Found IR Files for {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, model_data.modelName))
        else:
            logging.info('>> {0}:{1}() Converting {2} from {3}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, model_data.modelName, str(model_data.model_dir)))

            # p_converter = (Path(self.openvino_path / 'deployment_tools' / 'tools' / 'model_downloader' / 'converter.py').resolve())
            p_converter = Path(Path('./').resolve() / 'open_model_zoo/tools/downloader/converter.py').resolve()

            if (p_converter.exists()):

                converter_cmd = 'python3.7 {} --download_dir {} --output_dir {} --name {} --python {}'.format(
                    str(p_converter),
                    str(self.model_dir),
                    str(self.ir_dir),
                    model_data.modelName,
                    '/usr/bin/python3.7')

                if self._debug:
                    logging.info(converter_cmd)

                logging.info('>> Convert {}'.format(model_data.modelName))
                os.system(converter_cmd)
                logging.info('<< Convert {}'.format(model_data.modelName))

                model_data = self.search_ir_dir(model_data)

        return model_data

#
# Load model files (BIN and XML) into target hardware
#
    def load_model(self, model_data):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        assert isinstance(model_data, OpenVINO_Model_Data), "Invalid Model Data"

        model_data.errorMsg = ""

        model_data = self.search_model(model_data)

        if model_data.ir_dir is None:
            logging.warning("IR Folder empty.")
            model_data.clearFlag(Model_Flag.Downloaded)
            return model_data
        else:
            logging.info('   IR Folder :')
            logging.info('   FP16      : {}'.format(str(model_data.ir_dir['FP16'])))
            logging.info('   FP32      : {}'.format(model_data.ir_dir['FP32']))

            if 'MYRIAD' in self._target_device:
                self._precision = 'FP16'

            xml_file = Path(model_data.ir_dir[(self._precision)] / '{}.xml'.format(model_data.modelName))
            bin_file = Path(model_data.ir_dir[(self._precision)] / '{}.bin'.format(model_data.modelName))

            if xml_file.exists() and bin_file.exists():

                logging.info('Loading {} from {}'.format(model_data.modelName, str(model_data.ir_dir[(self._precision)])))
                logging.info('   XML : {}'.format(str(xml_file)))
                logging.info('   BIN : {}'.format(str(bin_file)))

                flag = self._inference_Core.load_model(xml_file = str(xml_file), bin_file = str(bin_file), device = self._target_device, precision = self._precision)

                model_data.setFlag(flag)

                if model_data.isFlagSet(Model_Flag.Unsupported):
                    model_data.errorMsg = '{} is not supported (yet)'.format(model_data.modelName)

            else:
                if not xml_file.exists():
                    logging.error('{} missing'.format(str(xml_file)))

                if not bin_file.exists():
                    logging.error('{} missing'.format(str(bin_file)))

        return model_data

    #
    # returns OpenVINO_Model_Data
    # receives {"SetAiModel" : "Model Name"}
    #
    def get_ai_model_data(self, model):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        json_data = json.loads(model)

        model_data = None

        # look for model data
        for i in range(0, len(self.modelList)):
            if self.modelList[i].modelName == json_data["set_ai_model"]:
                model_data = self.modelList[i]
                break

        return model_data

#
# Run inference
#
    def inference(self, frame):
        # if self._debug:
        #     logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self._inference_Core is None:
            logging.warning("IE Network Empty")
        else:
            return self._inference_Core.run_inference(frame, self._confidence)

