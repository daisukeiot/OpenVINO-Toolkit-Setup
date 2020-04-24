import sys
import logging
import traceback
from OpenVINO_Config import Engine_State, Model_Flag, Output_Format, Input_Format
from openvino.inference_engine import IECore, IENetwork, IEPlugin
import numpy as np
import cv2
from pathlib import Path
from Process_Object_Detection import Object_Detection_Processor 
from Process_Faster_RCNN import Object_Detection_RCNN_Processor
from Process_Yolo import Object_Detection_Yolo_Processor

class OpenVINO_Core:

    def __init__(self):
        self.ie = IECore()
        self.name = ""

        self.asyncInference = False
        self.plugin = None
        self.ieNet = None

        self.result_processor = None

        self.exec_net = None

        devices = []
        for device in self.ie.available_devices:
            if device == 'CPU':
                devices.append('CPU')
            elif device == 'GPU':
                devices.append('CPU')
            elif 'MYRIAD' in device and not 'MYRIAD' in devices:
                devices.append('MYRIAD')

        self.devices = devices
        self.outputFormat = Output_Format.Unknown
        self.inputFormat = Input_Format.Unknown
        # self.outputName = None
        self._debug = True
        self.ver_major = 0
        self.ver_minor = 0
        self.ver_build = 0

        self.current_hw = None
        self.current_precision = None
        self.current_model = None

    def reset_engine(self):
        self.name = ""
        self.plugin = None
        self.ieNet = None
        self.result_processor = None

        self.exec_net = None
        self.outputFormat = Output_Format.Unknown
        self.inputFormat = Input_Format.Unknown
        # self.outputName = None
        self.ver_major = 0
        self.ver_minor = 0
        self.ver_build = 0
        self.classLabels = {}

        self.current_hw = None
        self.current_precision = None
        self.current_model = None

    def dump(self, obj):
        print('=================================================')
        for attr in dir(obj):
            print('obj.%s = %r' % (attr, getattr(obj,attr)))
        print('=================================================')

    def get_signature(self):
        cpu = self.ie.get_versions('CPU')

        signature = 'OpenVINO {}.{}.{}'.format(cpu['CPU'].major,cpu['CPU'].minor, cpu['CPU'].build_number)
        return signature


    def load_model(self, xml_file, bin_file, device = "MYRIAD", cpu_extension = None, precision = 'FP16'):
        # N : # of images in batch
        # C : Channel
        # H : Height
        # W : Width
        # Input => HWC
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        try:
            self.reset_engine()

            p_model = Path(xml_file).resolve()
            self.name = str(Path(p_model.name).stem)

            precision = precision

            logging.info('==================================================================')
            logging.info('Loading Model')
            logging.info('    Name      : {}'.format(self.name))
            logging.info('    Target    : {}'.format(device))
            logging.info('    Model     : {}'.format(xml_file))
            logging.info('    Precision : {}'.format(precision))

            version_data = self.ie.get_versions(device)

            self.ver_major = int(version_data[device].major)
            self.ver_minor = int(version_data[device].minor)
            self.ver_build = int(version_data[device].build_number)

            # self.plugin = IEPlugin(device=device)

            # if 'MYRIAD' in device:
            #     #https://docs.openvinotoolkit.org/latest/_docs_IE_DG_supported_plugins_MYRIAD.html
            #     self.plugin.set_config({"VPU_FORCE_RESET": "NO"})

            if self.ie:
                del self.ie
            
            self.ie = IECore()

            if self.ver_major >= 2 and self.ver_minor >= 1 and self.ver_build >= 42025:
                self.ieNet = self.ie.read_network(model = xml_file, weights = bin_file)
            else:
                self.ieNet = IENetwork(model = xml_file, weights = bin_file)

            # process input

            # image_tensor : TensorFlow
            # data         : Caffe

            if len(self.ieNet.inputs) > 2:
                logging.warn('!! Too many inputs.  Not supported')
                return  Model_Flag.LoadError

            # don't touch layers.  Somehow touching layer will cause load failure with Myriad
            # logging.info(' -Layers')
            # logging.info('       Type : {}'.format(self.ieNet.layers[key].type))
            # self.dump(self.ieNet.layers[key])

            logging.info('==================================================================')
            logging.info('Output Blobs')

            for key, blob in self.ieNet.outputs.items():

                logging.info('Output Key    : {}'.format(key))
                logging.info('     Layout   : {}'.format(blob.layout))
                logging.info('      Shape   : {}'.format(blob.shape))
                logging.info('  Precision   : {}'.format(blob.precision))
                # logging.info(' -Layers')
                # logging.info('       Type : {}'.format(self.ieNet.layers[key].type))
                # self.dump(self.ieNet.layers[key])

            logging.info('==================================================================')
            logging.info('Input Blobs')

            for key, blob in self.ieNet.inputs.items():

                logging.info('Input Key     : {}'.format(key))
                logging.info('     Layout   : {}'.format(blob.layout))
                logging.info('      Shape   : {}'.format(blob.shape))
                logging.info('  Precision   : {}'.format(blob.precision))

            logging.info('>> Loading model to {}'.format(device))

            # self.exec_net = self.ie.load_network(network = self.ieNet, device_name = device, num_requests = 2)
            self.exec_net = self.ie.load_network(network = self.ieNet, device_name = device, num_requests = 4)

            logging.info('<< Model loaded to  {}'.format(device))

            # # touch layers only after we load
            # self.output_blob_key = next(iter(self.ieNet.outputs))

            for key, blob in self.ieNet.outputs.items():

                layer = self.ieNet.layers[key]

                if layer.type == 'DetectionOutput':
                    outputFormat = Output_Format.DetectionOutput
                elif layer.type == 'RegionYolo':
                    outputFormat = Output_Format.RegionYolo
                else:
                    return Model_Flag.Unsupported

            if outputFormat == Output_Format.DetectionOutput:
                if len(self.ieNet.inputs) == 1 and len(self.ieNet.outputs) == 1:
                    # 1 input, 1 output

                    input_key  = next(iter(self.ieNet.inputs))
                    output_key = next(iter(self.ieNet.outputs))

                    layer = self.ieNet.layers[output_key]

                    if layer.type == 'DetectionOutput':
                        outputFormat = Output_Format.DetectionOutput
                    else:
                        return Model_Flag.Unsupported

                    if input_key == 'image_tensor':
                        self.inputFormat = Input_Format.Tensorflow
                    elif input_key == 'image':
                        self.inputFormat = Input_Format.IntelIR
                    elif input_key == 'data':
                        self.inputFormat = Input_Format.Caffe
                    else:
                        self.inputFormat = Input_Format.Other

                    params = self.ieNet.layers[output_key].params
                    input_blob = self.ieNet.inputs[input_key]

                    self.result_processor = Object_Detection_Processor(
                                                model_name = self.name,
                                                input_format = self.inputFormat,
                                                input_key = input_key,
                                                input_shape = input_blob.shape,
                                                input_layout = input_blob.layout,
                                                output_format = outputFormat,
                                                output_key = output_key,
                                                output_params = params)

                elif len(self.ieNet.inputs) == 2 and len(self.ieNet.outputs) == 1:
                    # 2 inputs and 1 output.  Faster RCNN

                    output_key = next(iter(self.ieNet.outputs))

                    layer = self.ieNet.layers[output_key]

                    if layer.type != 'DetectionOutput':
                        return Model_Flag.Unsupported

                    info_key = ""
                    data_key = ""

                    for key, blob in self.ieNet.inputs.items():

                        if key == 'image_info':
                            info_key = key
                        elif key == 'image_tensor':
                            data_key = key

                    if len(info_key) > 0 and len(data_key) > 0:

                        self.inputFormat = Input_Format.Faster_RCNN
                        input_blob = self.ieNet.inputs[data_key]
                        params = self.ieNet.layers[output_key].params

                        self.result_processor = Object_Detection_RCNN_Processor(
                            model_name = self.name,
                            input_format = self.inputFormat,
                            info_key = info_key,
                            data_key = data_key,
                            data_shape = input_blob.shape,
                            data_layout = input_blob.layout,
                            output_format = Output_Format.DetectionOutput,
                            output_key = output_key,
                            output_params = params)
                    else:
                        return Model_Flag.Unsupported

            elif outputFormat == Output_Format.RegionYolo:
                input_key  = next(iter(self.ieNet.inputs))
                input_blob = self.ieNet.inputs[input_key]

                self.inputFormat = Input_Format.Yolo
                self.result_processor = Object_Detection_Yolo_Processor(
                                            model_name = self.name,
                                            input_format = self.inputFormat,
                                            input_key = input_key,
                                            input_shape = input_blob.shape,
                                            input_layout = input_blob.layout,
                                            output_format = Output_Format.RegionYolo)

                for key, blob in self.ieNet.outputs.items():
                    self.result_processor.reshape_data[key] = self.ieNet.layers[self.ieNet.layers[key].parents[0]].shape
                    self.result_processor.set_class_label(self.ieNet.layers[key].params)

                for key, blob in self.result_processor.reshape_data.items():
                    print('{} {}'.format(key, blob))

            return Model_Flag.Loaded

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))
            return Model_Flag.LoadError

    def run_inference(self, frame, confidence):
        # if self._debug:
        #     logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.inputFormat == Input_Format.Faster_RCNN:

            inference_data = self.result_processor.process_for_inference(frame = frame)

            if inference_data:
                if self.asyncInference:
                    self.exec_net.start_async(request_id=0, inputs={inference_data.data_key : inference_data.image_data, inference_data.info_key : inference_data.image_info})
                    if self.exec_net.requests[0].wait(-1) == 0:
                        self.result_processor.process_result(self.exec_net.requests[0].outputs, frame, confidence)
                else:
                    self.exec_net.infer(inputs={inference_data.data_key : inference_data.image_data, inference_data.info_key : inference_data.image_info})
                    self.result_processor.process_result(self.exec_net.requests[0].outputs, frame, confidence)

        elif self.inputFormat == Input_Format.Yolo:

            frame_data, input_key = self.result_processor.process_for_inference(frame = frame)

            if frame_data.size > 0:

                if self.asyncInference:
                    self.exec_net.start_async(request_id=0, inputs={input_key : frame_data})
                    if self.exec_net.requests[0].wait(-1) == 0:
                        self.result_processor.process_result(self.exec_net.requests[0].outputs, frame_data, frame, confidence)
                else:
                    self.exec_net.infer(inputs={input_key : frame_data})
                    self.result_processor.process_result(self.ieNet.layers, self.exec_net.requests[0].outputs, frame_data, frame, confidence)

        else:
        # elif self.inputFormat == Input_Format.Tensorflow or self.inputFormat == Input_Format.Caffe or self.inputFormat == Input_Format.IntelIR:
            # SSD/MobileNet Tensorflow models

            frame_data, input_key = self.result_processor.process_for_inference(frame = frame)

            if frame_data.size > 0:

                if self.asyncInference:
                    self.exec_net.start_async(request_id=0, inputs={input_key : frame_data})
                    if self.exec_net.requests[0].wait(-1) == 0:
                        self.result_processor.process_result(self.exec_net.requests[0].outputs, frame, confidence)
                else:
                    self.exec_net.infer(inputs={input_key : frame_data})
                    self.result_processor.process_result(self.exec_net.requests[0].outputs, frame, confidence)
