import os
import sys
import logging
import traceback
from openvino.inference_engine import IECore, IENetwork
from OpenVINO_Config import Model_Flag, Output_Format, BLOB_DATA
from pathlib import Path

from Process_Object_Detection import OBJECT_DETECTION, OBJECT_DETECTION_INFERENCE_DATA
from Process_Yolo import YOLO_DETECTION, YOLO_DETECTION_INFERENCE_DATA
from Process_Faster_RCNN import FASTER_RCNN_DETECTION, FASTER_RCNN_DETECTION_DETECTION_INFERENCE_DATA
from Process_HumanPose import HUMANPOSE_DETECTION, HUMANPOSE_INFERENCE_DATA

class OpenVINO_Core:

    def __init__(self):

        self.ieCore = IECore()

        self.ver_major = 0
        self.ver_minor = 0
        self.ver_build = 0
        self.model_format = Output_Format.Unknown

        devices = []
        for device in self.ieCore.available_devices:
            if 'MYRIAD' in device:
                if not 'MYRIAD' in devices:
                    devices.append('MYRIAD')
            else:
                if not device in devices:
                    devices.append(device)

        self.devices = devices

        self.inference_processor = None

    def get_signature(self):
        """
        return Signature string to display in UI
        """

        if len(self.ieCore.available_devices) > 0:

            device = self.ieCore.available_devices[0]
            version = self.ieCore.get_versions(device)

            if os.getenv('OPENVINO_OBJECT_DETECTION_PYTHON'):
                signature = 'OpenVINO {}.{}.{} in Container'.format(version[device].major,version[device].minor, version[device].build_number)
            else:
                signature = 'OpenVINO {}.{}.{}'.format(version[device].major,version[device].minor, version[device].build_number)
        else:
            signature = 'OpenVINO No Hardware Found'

        return signature

    def dump_blob(self, blob):

        blob_key   = blob.name
        blob_layer = self.ieNet.layers[blob_key]
        print('Key          {}'.format(blob_key))
        print('  Layer      {}'.format(blob_layer.name))
        print('  Layer Type {}'.format(blob_layer.type))
        print('  Blob Shape {}'.format(blob.shape))

    def check_detection_output(self, blob):

        """
        Object Detection Model
        make sure output shape is [1,1,N,7]
        """
        shape = blob.shape
        num_class = 0
        if shape[0] == 1 and shape[1] == 1 and shape[3] == 7:
            outputParams = self.ieNet.layers[blob.name].params
            if 'num_classes' in outputParams:
                num_class = int(outputParams['num_classes'])
                print('  Num Classes {}'.format(num_class))

            logging.info('>> Found Known Detection Output')
            return True

        return False

    def detect_model_type(self, xml_file, bin_file, device):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        version_data = self.ieCore.get_versions(device)
        self.ver_major = int(version_data[device].major)
        self.ver_minor = int(version_data[device].minor)
        self.ver_build = version_data[device].build_number

        if self.ver_major >= 2 and self.ver_minor >= 1:
            self.ieNet = self.ieCore.read_network(model = xml_file, weights = bin_file)
        else:
            self.ieNet = IENetwork(model = xml_file, weights = bin_file)

        for key in self.ieNet.inputs:
            layer = self.ieNet.layers[key]
            print('Input Blobs  : {}'.format(key))
            print('- Laout      : {}'.format(self.ieNet.inputs[key].layout))
            print('- Shape      : {}'.format(self.ieNet.inputs[key].shape))
            print('- Layer Type : {}'.format(layer.type))

        for key in self.ieNet.outputs:
            layer = self.ieNet.layers[key]
            print('Output Blobs : {}'.format(key))
            print('- Laout      : {}'.format(self.ieNet.outputs[key].layout))
            print('- Shape      : {}'.format(self.ieNet.outputs[key].shape)) 
            print('- Layer Type : {}'.format(layer.type))

        xml = Path(xml_file)

        print('Model {} : In Count {} Out Count {}'.format(xml.name, len(self.ieNet.inputs), len(self.ieNet.outputs)))

        input_len  = len(self.ieNet.inputs)
        output_len = len(self.ieNet.outputs)

        if input_len == 1:
            """
            Look for known models with 1 input
            """
            print(next(iter(self.ieNet.inputs)))
            input_key  = next(iter(self.ieNet.inputs))
            input_blob  = self.ieNet.inputs[input_key]
            input_layer  = self.ieNet.layers[input_key]

            self.dump_blob(input_blob)

            if input_layer.type == 'Input':
                if output_len == 1:
                    """
                    1 x input & 1 x output
                    """
                    output_key   = next(iter(self.ieNet.outputs))
                    output_blob  = self.ieNet.outputs[output_key]
                    output_layer = self.ieNet.layers[output_key]

                    self.dump_blob(output_blob)

                    if input_layer.type == 'Input':
                        
                        if output_layer.type == 'DetectionOutput':
                            if self.check_detection_output(output_blob):
                                self.model_format = Output_Format.DetectionOutput

                        elif output_layer.type == 'RegionYolo':
                            print('  Found Yolo')
                            self.model_format = Output_Format.RegionYolo

                elif output_len == 2:
                    """
                    check for Human Pose
                    """
                    for key in self.ieNet.outputs:
                        output_layer = self.ieNet.layers[key]
                        if output_layer.type != 'Convolution':
                            self.model_format = Output_Format.Unknown
                            break
                        else:
                            output_name = self.ieNet.outputs[key].name

                            if output_name == 'Mconv7_stage2_L1' or output_name == 'Mconv7_stage2_L2':
                                self.model_format = Output_Format.HumanPose
                            else:
                                self.model_format = Output_Format.Unknown
                                break

                elif output_len == 3:
                    """
                    Check if this is Yolo v3
                    """
                    for key in self.ieNet.outputs:
                        output_layer = self.ieNet.layers[key]
                        if output_layer.type != 'RegionYolo':
                            self.model_format = Output_Format.Unknown
                            break
                        else:
                            self.model_format = Output_Format.RegionYolo

                    if self.model_format == Output_Format.RegionYolo:
                        print('  Found Yolo v3')

        elif input_len == 2:
            """
            Look for known models with 2 input
            """
            if 'image_info' in self.ieNet.inputs and 'image_tensor' in self.ieNet.inputs:

                if output_len == 1:
                    """
                    make sure there is only 1 DetectionOutput output 
                    """
                    output_key = next(iter(self.ieNet.outputs))
                    output_blob  = self.ieNet.outputs[output_key]
                    output_layer = self.ieNet.layers[output_key]
                    
                    if output_layer.type == 'DetectionOutput':
                        if self.check_detection_output(output_blob):
                            self.model_format = Output_Format.Faster_RCNN

        logging.info('>> Output Format {}'.format(self.model_format.name))


        # if len(self.ieNet.inputs) == 1 and self.ieNet.inputs[0] 

    def load_model(self, xml_file, bin_file, device, precision):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        del self.inference_processor
        self.inference_processor = None

        p_model = Path(xml_file).resolve()
        model_name = str(Path(p_model.name).stem)

        flag = Model_Flag.LoadError
        self.detect_model_type(xml_file, bin_file, device)

        if self.model_format == Output_Format.DetectionOutput:

            self.inference_processor = OBJECT_DETECTION(model_name, xml_file, bin_file)
            if self.inference_processor.load_model(target = device):
                flag = Model_Flag.Loaded

        elif self.model_format == Output_Format.Faster_RCNN:

            self.inference_processor = FASTER_RCNN_DETECTION(model_name, xml_file, bin_file)
            if self.inference_processor.load_model(target = device):
                flag = Model_Flag.Loaded

        elif self.model_format == Output_Format.RegionYolo:

            self.inference_processor = YOLO_DETECTION(model_name, xml_file, bin_file)
            if self.inference_processor.load_model(target = device):
                flag = Model_Flag.Loaded

        elif self.model_format == Output_Format.HumanPose:

            self.inference_processor = HUMANPOSE_DETECTION(model_name, xml_file, bin_file)
            if self.inference_processor.load_model(target = device):
                flag = Model_Flag.Loaded


        return flag

    def run_inference(self, frame, confidence):
        # logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.inference_processor:

            # pre-process incoming image
            inference_data = self.inference_processor.preprocess_for_inference(frame, confidence)

            # run inference
            results = self.inference_processor.run_inference(inference_data)

            # process the results and receive a list of detection results in common format
            detection_List = self.inference_processor.process_result(results, inference_data)

            # Annotation (Text, bounding box, etc)
            self.inference_processor.annotate_frame(detection_List, frame)

        return frame