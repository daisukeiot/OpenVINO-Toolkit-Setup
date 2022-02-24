from math import fabs
import os
import sys
import logging
import traceback
from OpenVINO_Config import Engine_State, Model_Flag
from openvino.inference_engine import IECore
import numpy as np
import cv2
from pathlib import Path
from Process_Object_Detection import Object_Detection_Processor 
from Process_Faster_RCNN import Object_Detection_RCNN_Processor
from OpenVINO_Util import OpenVINOUtil, ModelTypes

class OpenVINO_Core:

    def __init__(self):
        self.ie = IECore()
        self.name = ""

        self.asyncInference = False
        self.plugin = None
        self.ieNet = None

        self.result_processor = None

        self.exec_net = None
        self.model_type = ModelTypes.UNKNOWN

        devices = []
        for device in self.ie.available_devices:
            if 'MYRIAD' in device:
                if not 'MYRIAD' in devices:
                    devices.append('MYRIAD')
            else:
                if not device in devices:
                    devices.append(device)

        self.devices = devices
        # self.outputName = None
        self._debug = True
        self.ver_major = 0
        self.ver_minor = 0
        self.ver_build = 0

        self.current_hw = None
        self.current_precision = None
        self.current_model = None
        self.request_slot_curr = 1
        self.request_slot_next = 0

    def reset_engine(self):
        self.name = ""
        self.plugin = None
        self.ieNet = None
        self.result_processor = None

        self.exec_net = None
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
        if len(self.ie.available_devices) > 0:
            device = self.ie.available_devices[0]
            version = self.ie.get_versions(device)

            if os.getenv('OPENVINO_OBJECT_DETECTION_PYTHON'):
                signature = 'OpenVINO {}.{}.{} in Container'.format(version[device].major,version[device].minor, version[device].build_number)
            else:
                signature = 'OpenVINO {}.{}.{}'.format(version[device].major,version[device].minor, version[device].build_number)
        else:
            signature = 'OpenVINO No Hardware Found'

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

            logging.info('==================================================================')
            logging.info('Loading Model')
            logging.info('    Name      : {}'.format(self.name))
            logging.info('    Target    : {}'.format(device))
            logging.info('    Model     : {}'.format(xml_file))
            logging.info('    Precision : {}'.format(precision))

            version_data = self.ie.get_versions(device)
            self.ver_major = int(version_data[device].major)
            self.ver_minor = int(version_data[device].minor)
            self.ver_build = version_data[device].build_number

            # self.plugin = IEPlugin(device=device)

            # if 'MYRIAD' in device:
            #     #https://docs.openvinotoolkit.org/latest/_docs_IE_DG_supported_plugins_MYRIAD.html
            #     self.plugin.set_config({"VPU_FORCE_RESET": "NO"})

            if self.ie:
                del self.ie
            
            self.ie = IECore()

            if self.ver_major >= 2 and self.ver_minor >= 1: # and self.ver_build >= 42025:
                self.ieNet = self.ie.read_network(model = xml_file, weights = bin_file)
            else:
                self.ieNet = IENetwork(model = xml_file, weights = bin_file)

            self.util = OpenVINOUtil(self.ieNet)

            # process input

            inputs = self.util.get_ie_inputs()

            logging.info('==================================================================')
            logging.info('IR Inputs')

            for input_key in inputs:
                logging.info('Input Key     : {}'.format(input_key))
                logging.info('     Layout   : {}'.format(self.ieNet.input_info[input_key].tensor_desc.layout))
                logging.info('      Shape   : {}'.format(self.ieNet.input_info[input_key].tensor_desc.dims))
                logging.info('  Precision   : {}'.format(self.ieNet.input_info[input_key].tensor_desc.precision))

            logging.info('==================================================================')
            logging.info('IR Outputs')

            outputs = self.util.get_ie_outputs()

            for output_key in outputs:
                logging.info('Output Key    : {}'.format(output_key))
                logging.info('     Layout   : {}'.format(self.ieNet.outputs[output_key].layout))
                logging.info('      Shape   : {}'.format(self.ieNet.outputs[output_key].shape))
                logging.info('  Precision   : {}'.format(self.ieNet.outputs[output_key].precision))

            logging.info('>> Loading model to {}'.format(device))

            # self.exec_net = self.ie.load_network(network = self.ieNet, device_name = device, num_requests = 2)
            self.exec_net = self.ie.load_network(network = self.ieNet, device_name = device, num_requests = 2)

            logging.info('<< Model loaded to  {}'.format(device))

            self.model_type = self.util.check_model_type()

            logging.info('Model Type : {}'.format(self.model_type.value))

            if self.model_type == ModelTypes.SSD:

                assert(len(inputs) == 1 and len(outputs) == 1)

                input_key = inputs[0]
                output_key = outputs[0]
                params = self.util.get_params()
                input = self.ieNet.input_info[input_key]

                self.result_processor = Object_Detection_Processor(
                                            model_name = self.name,
                                            model_type = self.model_type,
                                            input_key = input_key,
                                            input_shape = input.tensor_desc.dims,
                                            input_layout = input.tensor_desc.layout,
                                            output_key = output_key,
                                            output_params = params)

            elif self.model_type == ModelTypes.YOLO_V1_TINY or \
                 self.model_type == ModelTypes.YOLO_V2 or \
                 self.model_type == ModelTypes.YOLO_V2_TINY:
                 
                 pass
                
            elif self.model_type == ModelTypes.YOLO_V3 or \
                 self.model_type == ModelTypes.YOLO_V3_TINY:

                input = self.ieNet.input_info[input_key]
                self.result_processor = Object_Detection_Yolo_v3_Processor(
                                            model_name = self.name,
                                            model_type = self.model_type,
                                            input_info = self.ieNet.input_info,
                                            outputs = self.ieNet.outputs,
                                            openvino_util = self.util)

            elif self.model_type == ModelTypes.YOLO_V4 or \
                 self.model_type == ModelTypes.YOLO_V4_TINY:

                pass

            elif self.model_type == ModelTypes.RESNET:

                output_key = next(iter(self.ieNet.outputs))

                print(output_key)

                if output_key != 'detection_output':
                    print("Unsupported {}".format(output_key))
                    return Model_Flag.Unsupported

                info_key = ""
                data_key = ""

                for input_key, input in self.ieNet.input_info.items():

                    if input_key == 'image_info':
                        info_key = input_key
                    elif input_key == 'image_tensor' or input_key == 'image':
                        data_key = input_key

                if len(info_key) > 0 and len(data_key) > 0:

                    input_image = self.ieNet.input_info[data_key]

                    params =  self.util.get_params()

                    self.result_processor = Object_Detection_RCNN_Processor(
                        model_name = self.name,
                        model_type = self.model_type,
                        info_key = info_key,
                        data_key = data_key,
                        data_shape = input_image.tensor_desc.dims,
                        data_layout = input_image.tensor_desc.layout,
                        output_key = output_key,
                        output_params = params)
            #         else:
            #             print("111114 Unsupported {}".format(key))
            #             return Model_Flag.Unsupported

            # elif outputFormat == Output_Format.RegionYolo:
            #     input_key  = next(iter(self.exec_net.input_info))
            #     input_blob = self.exec_net.input_info[input_key]

            #     self.inputFormat = Input_Format.Yolo
            #     self.result_processor = Object_Detection_Yolo_Processor(
            #                                 model_name = self.name,
            #                                 input_format = self.inputFormat,
            #                                 input_key = input_key,
            #                                 input_shape = input_blob.tensor_desc.dims,
            #                                 input_layout = input_blob.tensor_desc.layout,
            #                                 output_format = Output_Format.RegionYolo)

            #     # for key, blob in self.ieNet.outputs.items():
            #     #     self.result_processor.reshape_data[key] = self.ieNet.layers[self.ieNet.layers[key].parents[0]].shape
            #     #     self.result_processor.set_class_label(self.ieNet.layers[key].params)

            #     # for key, blob in self.result_processor.reshape_data.items():
            #     #     print('{} {}'.format(key, blob))


            # elif outputFormat == Output_Format.HumanPose:
            #     input_key  = next(iter(self.ieNet.input_info))
            #     input_blob = self.ieNet.input_info[input_key]
            #     self.inputFormat = Input_Format.HumanPose

            #     self.result_processor = Human_Pose_Processor(
            #                                 model_name = self.name,
            #                                 input_format = Input_Format.HumanPose,
            #                                 input_shape = input_blob.shape,
            #                                 input_layout = input_blob.layout
            #                                 )
            return Model_Flag.Loaded

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))
            return Model_Flag.LoadError

    def run_inference(self, frame, confidence):
#        if self._debug:
#            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return_frame = frame

        if self.result_processor == None:
            return return_frame

        if self.model_type == ModelTypes.SSD:

            frame_data, input_key = self.result_processor.process_for_inference(frame = frame)

            if frame_data.size > 0:

                results = self.exec_net.infer(inputs={input_key : frame_data})
                return_frame = self.result_processor.process_result(results, frame, confidence)

        elif self.model_type == ModelTypes.YOLO_V3:
            frame_data, input_key = self.result_processor.process_for_inference(frame = frame)

            if frame_data.size > 0:

                results = self.exec_net.infer(inputs={input_key : frame_data})
                return_frame = self.result_processor.process_result(results, frame, confidence)

        elif self.model_type == ModelTypes.RESNET:

            inference_data = self.result_processor.process_for_inference(frame = frame)

            if inference_data:
                results = self.exec_net.infer(inputs={inference_data.data_key : inference_data.image_data, inference_data.info_key : inference_data.image_info})
                return_frame = self.result_processor.process_result(results, frame, confidence)

        # elif self.inputFormat == Input_Format.Yolo:

        #     frame_data, input_key = self.result_processor.process_for_inference(frame = frame)

        #     if frame_data.size > 0:

        #         if self.asyncInference:
        #             self.result_processor.prev_frame = frame
        #             self.result_processor.prev_frame_data = frame_data
        #             self.exec_net.start_async(request_id=self.request_slot_next, inputs={input_key : frame_data})
        #             if self.exec_net.requests[self.request_slot_curr].wait(-1) == 0:
        #                 pass
        #             #     return_frame = self.result_processor.process_result(layers = self.ieNet.layers,
        #             #                                                         results = self.exec_net.requests[self.request_slot_curr].outputs, 
        #             #                                                         frame_data = self.result_processor.prev_frame_data, 
        #             #                                                         frame = self.result_processor.prev_frame, 
        #             #                                                         confidence = confidence)
        #         else:
        #             self.request_slot_curr = 0
        #             self.exec_net.infer(inputs={input_key : frame_data})
        #             return_frame = self.result_processor.process_result(layers = self.ieNet.layers,
        #                                                                 results = self.exec_net.requests[self.request_slot_curr].outputs,
        #                                                                 frame_data = frame_data,
        #                                                                 frame = frame,
        #                                                                 confidence = confidence)

        # elif self.inputFormat == Input_Format.HumanPose:

        #     frame_data, input_key = self.result_processor.process_for_inference(frame = frame)

        #     if frame_data.size > 0:

        #         if self.asyncInference:
        #             self.result_processor.prev_frame = frame
        #             self.exec_net.start_async(request_id=self.request_slot_next, inputs={input_key : frame_data})
        #             if self.exec_net.requests[self.request_slot_curr].wait(-1) == 0:
        #                 return_frame = self.result_processor.process_result(self.exec_net.requests[self.request_slot_curr].outputs, self.result_processor.prev_frame, confidence)
        #                 assert return_frame.size > 0, "Frame Empty"
        #         else:
        #             self.request_slot_curr = 0
        #             self.exec_net.infer(inputs={input_key : frame_data})
        #             return_frame = self.result_processor.process_result(self.exec_net.requests[self.request_slot_curr].outputs, frame, confidence)

        # elif self.inputFormat == Input_Format.Unknown:
        #     pass

        # else:
        # # elif self.inputFormat == Input_Format.Tensorflow or self.inputFormat == Input_Format.Caffe or self.inputFormat == Input_Format.IntelIR:
        #     # SSD/MobileNet Tensorflow models

        #     frame_data, input_key = self.result_processor.process_for_inference(frame = frame)

        #     if frame_data.size > 0:

        #         if self.asyncInference:
        #             self.result_processor.prev_frame = frame
        #             self.exec_net.start_async(request_id=self.request_slot_next, inputs={input_key : frame_data})
        #             if self.exec_net.requests[self.request_slot_curr].wait(-1) == 0:
        #                 return_frame = self.result_processor.process_result(self.exec_net.requests[self.request_slot_curr].outputs, self.result_processor.prev_frame, confidence)
        #                 assert return_frame.size > 0, "Frame Empty"
        #         else:
        #             self.request_slot_curr = 0
        #             self.exec_net.infer(inputs={input_key : frame_data})
        #             return_frame = self.result_processor.process_result(self.exec_net.requests[self.request_slot_curr].outputs, frame, confidence)

        # if self.asyncInference:
        #     self.request_slot_next, self.request_slot_curr = self.request_slot_curr, self.request_slot_next

        return return_frame
