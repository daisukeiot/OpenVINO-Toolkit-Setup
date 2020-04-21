import sys
import logging
import traceback
from enum import IntEnum
from OpenVINO_Config import Engine_State, Model_Flag
from openvino.inference_engine import IECore, IENetwork, IEPlugin
import numpy as np
import cv2
from pathlib import Path
from label_map import coco_category_map, voc_category_map

class Output_Format(IntEnum):
    Unknown = 0
    DetectionOutput = 1
    Softmax = 2
    Mconv7_stage2_L1 = 3
    Faster_RCNN = 4

class Input_Format(IntEnum):
    Unknown = 0
    Tensorflow = 1
    Caffe = 2
    Faster_RCNN = 3
    IntelIR = 4

class CV2_Draw_Info():

    def __init__(self):
        self.fontScale = 1.0
        self.thickness = 1
        self.lineType = cv2.LINE_AA
        # p_font = Path(Path('./').resolve() / 'segoeui.ttf')
        # if p_font.exists():
        #     self.font = ImageFont.truetype(str(p_font), 10)
        #     #self.fontSize = self.font.getsize('123.4%') 
        # else:
        self.fontName = cv2.FONT_HERSHEY_COMPLEX_SMALL
        self.textSize, self.textBaseline = cv2.getTextSize('%', self.fontName, self.fontScale, self.thickness)
        

class IE_Engine:

    def __init__(self):
        self.ie = IECore()
        self.name = ""
        self.plugin = None
        self.ieNet = None
        self.input_blob_key = None
        self.input_layout = None
        self.input_shape = None
        self.classLabels = {}

        self.output_blob_key = None
        self.exec_net = None
        self.devices = self.ie.available_devices
        self.outputFormat = Output_Format.Unknown
        self.inputFormat = Input_Format.Unknown
        self.outputName = None
        self.num_class = 0
        self._debug = True
        self.ver_major = 0
        self.ver_minor = 0
        self.ver_build = 0
        self.colors = []
        self.colors.append((232, 35, 244))
        self.colors.append((0, 241, 255))
        self.colors.append((10, 216, 186))
        self.colors.append((242, 188, 0))

        self.draw_info = CV2_Draw_Info()

    def reset_engine(self):
        self.name = ""
        self.plugin = None
        self.ieNet = None
        self.input_blob_key = None
        self.output_blob_key = None
        self.exec_net = None
        self.input_shape = None
        self.input_layout = None
        self.outputFormat = Output_Format.Unknown
        self.inputFormat = Input_Format.Unknown
        self.outputName = None
        self.num_class = 0
        self.ver_major = 0
        self.ver_minor = 0
        self.ver_build = 0
        self.classLabels = {}

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
            logging.info('==================================================================')

            for key in self.ieNet.inputs:
                logging.info('Input Key     : {}'.format(key))
                logging.info('     Layout   : {}'.format(self.ieNet.inputs[key].layout))
                logging.info('      Shape   : {}'.format(self.ieNet.inputs[key].shape))
                logging.info('  Precision   : {}'.format(self.ieNet.inputs[key].precision))
                # don't touch layers.  Somehow touching layer will cause load failure with Myriad
                # logging.info(' -Layers')
                # logging.info('       Type : {}'.format(self.ieNet.layers[key].type))
                # self.dump(self.ieNet.layers[key])

            if len(self.ieNet.inputs) > 2:
                return Model_Flag.Unsupported

            if len(self.ieNet.inputs) == 1:

                self.input_blob_key = next(iter(self.ieNet.inputs))

                if 'image_tensor' in self.ieNet.inputs.keys():
                    logging.info('Tensorflow Input')
                    self.inputFormat = Input_Format.Tensorflow
                    self.input_blob_key = 'image_tensor'
                    self.input_shape = self.ieNet.inputs[self.input_blob_key].shape
                    self.input_layout = self.ieNet.inputs[self.input_blob_key].layout
                    # self.ieNet.inputs[self.input_blob_key].precision = precision

                elif 'data' in self.ieNet.inputs.keys():
                    logging.info('Caffe Input')
                    self.inputFormat = Input_Format.Caffe
                    self.input_blob_key = 'data'
                    self.input_shape = self.ieNet.inputs[self.input_blob_key].shape
                    self.input_layout = self.ieNet.inputs[self.input_blob_key].layout

                else:
                    logging.info('Other Input')
                    self.inputFormat = Input_Format.IntelIR
                    self.input_shape = self.ieNet.inputs[self.input_blob_key].shape
                    self.input_layout = self.ieNet.inputs[self.input_blob_key].layout

            elif len(self.ieNet.inputs) == 2:

                if 'image_info' in self.ieNet.inputs.keys() and 'image_tensor' in self.ieNet.inputs.keys():
                    logging.info('Found Faster RCNN Inputs')
                    self.input_blob_key = 'image_tensor'
                    self.inputFormat = Input_Format.Faster_RCNN
                    self.input_shape = self.ieNet.inputs[self.input_blob_key].shape
                    self.input_layout = self.ieNet.inputs[self.input_blob_key].layout
                    # self.ieNet.inputs[self.input_blob_key].precision = precision

            # process output
            logging.info('==================================================================')
            # DetectionOutput
            self.output_blob_key = next(iter(self.ieNet.outputs))

            for key in self.ieNet.outputs:
                logging.info('Output Key    : {}'.format(key))
                logging.info('     Layout   : {}'.format(self.ieNet.outputs[key].layout))
                logging.info('      Shape   : {}'.format(self.ieNet.outputs[key].shape))
                logging.info('  Precision   : {}'.format(self.ieNet.outputs[key].precision))
                # logging.info(' -Layers')
                # logging.info('       Type : {}'.format(self.ieNet.layers[key].type))
                # self.dump(self.ieNet.layers[key])

            if len(self.ieNet.outputs) > 1:
                return Model_Flag.Unsupported

            logging.info('>> Loading model to {}'.format(device))

            # self.exec_net = self.ie.load_network(network = self.ieNet, device_name = device, num_requests = 2)
            self.exec_net = self.ie.load_network(network = self.ieNet, device_name = device)

            logging.info('<< Model loaded to  {}'.format(device))


            # touch layers only after we load
            self.output_blob_key = next(iter(self.ieNet.outputs))

            params = self.ieNet.layers[self.output_blob_key].params

            if 'num_classes' in params:
                self.num_class = int(params['num_classes'])
                logging.info('  num_class   : {}'.format(self.num_class))

            if self.ieNet.layers[self.output_blob_key].type == "DetectionOutput":
                #self.ieNet.outputs[self.output_blob_key].precision = precision
                self.outputFormat = Output_Format.DetectionOutput
                self.outputName = self.output_blob_key

            elif self.ieNet.layers[self.output_blob_key].type == "SoftMax":
                self.outputFormat = Output_Format.Softmax
                self.outputName = self.output_blob_key

            elif self.ieNet.layers[self.output_blob_key].type == "Convolution":
                self.outputFormat = Output_Format.Mconv7_stage2_L1
                self.outputName = self.output_blob_key
            else:
                return Model_Flag.Unsupported

            if self.outputFormat == Output_Format.DetectionOutput:

                if self.num_class == 91 or 'coco' in self.name:
                    logging.info("Loading Coco Label")
                    self.classLabels = coco_category_map
                elif self.num_class == 21:
                    logging.info("Loading VOC Label")
                    self.classLabels = voc_category_map

            return Model_Flag.Loaded

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))
            return Model_Flag.LoadError

    def annotate_result_object_detection(self, frame, rect, confidence, label_id):
        # if self._debug:
        #     logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        color = (232, 35, 244)

        try:
            if self.num_class == 91 or self.num_class == 21:
                color = self.colors[0]
                annotation_text = '{0} {1:.1f}%'.format(self.classLabels[label_id], float(confidence*100))

            elif self.num_class == 2:
                color = self.colors[0]
                annotation_text = '{0:.1f}%'.format(float(confidence*100))
            else:
                color = self.colors[label_id-1]
                annotation_text = '{0:.1f}%'.format(float(confidence*100))

        except IndexError as error:
            logging.error('Index Error {} : {}'.format(label_id, error))

        except Exception as ex:
            logging.error('Exception finding label {} : {}'.format(label_id, error))

        cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), color, 2)

        # pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        # draw = ImageDraw.Draw(pil_image)
        # draw.text((0,0), annotation_text, font=self.draw_info.font)

        # frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        cv2.putText(img = frame, 
                    text = annotation_text, 
                    org = (rect[0] + 5, rect[1] + int(self.draw_info.textSize[1] * 1.5)),
                    fontFace = self.draw_info.fontName,
                    fontScale = self.draw_info.fontScale,
                    color     = color,
                    thickness = self.draw_info.thickness,
                    lineType = self.draw_info.lineType)

    def annotate_result_classification(self, frame, confidence, inference_id, color = (232, 35, 244)):
        # if self._debug:
        #     logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if len(self.classLabels) > 0:
            annotation_text = '{} {}%'.format(self.classLabels[inference_id], confidence)
        else:
            annotation_text = '{} {}%'.format(inference_id, confidence)

        cv2.putText(img = frame, 
                    text = annotation_text, 
                    org = (5, 5),
                    fontFace = cv2.FONT_HERSHEY_COMPLEX_SMALL,
                    fontScale = 1.0,
                    color     = color,
                    thickness = 1,
                    lineType = cv2.LINE_AA)

    def run_inference(self, frame, confidence):
        # if self._debug:
        #     logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.inputFormat == Input_Format.Tensorflow or self.inputFormat == Input_Format.Caffe or self.inputFormat == Input_Format.IntelIR:
            # SSD/MobileNet Tensorflow models
            input_blob = self.ieNet.inputs[self.input_blob_key]

            if input_blob.layout == 'NCHW':
                frame_data = cv2.resize(frame, (input_blob.shape[3], input_blob.shape[2]))
                frame_data = frame_data.transpose((2,0,1))
                frame_data = frame_data.reshape(self.input_shape)
                self.exec_net.infer(inputs={self.input_blob_key : frame_data})

            if self.outputFormat & Output_Format.DetectionOutput:
                self.process_DetectionOutput(frame, confidence)

        elif self.inputFormat == Input_Format.Faster_RCNN:
            image_tensor = self.ieNet.inputs['image_tensor']
            image_info   = np.asarray([[image_tensor.shape[3], image_tensor.shape[2], 1]], dtype=np.float32)
            if image_tensor.layout == 'NCHW':
                frame_data = cv2.resize(frame, (image_tensor.shape[3], image_tensor.shape[2]))
                frame_data = frame_data.transpose((2,0,1))
                frame_data = frame_data.reshape(self.input_shape)
                self.exec_net.infer(inputs={"image_tensor" : frame_data, "image_info" : image_info})

            if self.outputFormat & Output_Format.DetectionOutput:
                self.process_DetectionOutput(frame, confidence)

        # elif self.outputFormat & Output_Format.Softmax:
        #     self.process_SoftmaxOutput(frame, confidence)

        # elif self.outputFormat & Output_Format.Mconv7_stage2_L1:
        #     self.process_HumanPose(frame, confidence)

    def process_DetectionOutput(self, frame, confidence):
        #
        # Process DetectionOutput
        # [image_id, label, conf, x_min, y_min, x_max, y_max]
        # - `image_id` - ID of the image in the batch
        # - `label` - predicted class ID
        # - `conf` - confidence for the predicted class
        # - (`x_min`, `y_min`) - coordinates of the top left bounding box corner (coordinates stored in normalized format, in range [0, 1])
        # - (`x_max`, `y_max`) - coordinates of the bottom right bounding box corner  (coordinates stored in normalized format, in range [0, 1])
        ieResults = self.exec_net.requests[0].outputs[self.outputName]

        imageH, imageW = frame.shape[:-1]

        rect = {}
        for index, ieResult in enumerate(ieResults[0][0]):
            # print('  obj {} id {} label {} conf {}'.format(index, int(ieResult[0]), int(ieResult[1]), ieResult[2]))

            if ieResult[0] == -1:
                break
            
            if ieResult[2] < confidence:
                continue

            # if self._debug:
            # print('  obj {} id {} label {} conf {}'.format(index, int(ieResult[0]), int(ieResult[1]), ieResult[2]))

            left   = np.int(imageW * ieResult[3])
            top    = np.int(imageH * ieResult[4])
            right  = np.int(imageW * ieResult[5])
            bottom = np.int(imageH * ieResult[6])
            rect = [left, top, right, bottom]
            self.annotate_result_object_detection(frame, rect, ieResult[2], int(ieResult[1]))

    def process_SoftmaxOutput(self, frame):

        prob = self.exec_net.requests[0].outputs[self.outputName][0]

        ids = np.argsort(prob)[::-1][:3]

        for id in ids:
            print('  id {} conf {}'.format(id, prob[id]))
            self.annotate_result_classification(frame, prob[id], id)

    def process_HumanPose(self, frame):

        input_shape = frame.shape
        poses = self.exec_net.requests[0].outputs[self.outputName]
        print(poses.shape)
        [b,c,h,w]=poses.shape

        out_heatmap = np.zeros([c, input_shape[0], input_shape[1]])

        for h in range(len(poses[0])):
            out_heatmap[h] = cv2.resize(poses[0][h], input_shape[0:2][::-1])
