import sys
import logging
from pathlib import Path
from openvino.inference_engine import IECore, IENetwork
import numpy as np
import cv2
from OpenVINO_Config import BLOB_DATA, color_list
from label_map import coco_80_category_map, coco_90_category_map, voc_category_map

class INFERENCE_DATA():

    def __init__(self, frame, confidence):
        self.frame_org = frame
        self.confidence = confidence
        self.input_key = None
        self.input_frame = None

#
# Super class for inference processor
#
class INFERENCE_PROCESS_CORE():

    color_list = color_list()

    def __init__(self, model_name, xml_file, bin_file):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        
        # self.p_xml, self.p_bin = self.check_model(model_path, model_name)
        self.model_name = model_name
        self.p_xml = xml_file
        self.p_bin = bin_file
        self.ieCore = IECore()
        self.ieNet = None
        self.execNet = None
        self.input_blobs = []
        self.output_blobs = []

        self.fontName = cv2.FONT_HERSHEY_SIMPLEX
        self.fontScale = 0.5
        self.fontThickness = 2
        self.lineThickness = 2
        self.textSize, self.textBaseline = cv2.getTextSize('12.3%', self.fontName, self.fontScale, self.fontThickness)
        self.classLabel = None
        self.num_class = 0
        self.colors = color_list()
        
        """
        print('Text Width  {}'.format(self.textSize[0]))
        print('Text Height {}'.format(self.textSize[1]))
        """
        
    def check_model(self, model_path, model_name):
        """
        Check Model File
        """
        p_folder = Path(Path(model_path).resolve())
        p_xml    = Path(p_folder / model_name)
        p_bin    = p_xml.with_suffix('.bin')

        if not p_folder.exists() or not p_xml.exists() or not p_bin.exists():
            cstr('Model File Not exists')
            raise StopExecution

        print("Found Model : {}".format(str(p_xml)))
        return p_xml, p_bin

    def _load_model(self, target='CPU'):
        """
        Load model to Execution Network.
        Build lists of input and output blobs
        """
        if not target in self.ieCore.available_devices:
            logging.error('!! Specified device not available : {}'.format(target))
            return

        self.ieNet = self.ieCore.read_network(model = str(self.p_xml), weights = str(self.p_bin))

        for key in self.ieNet.inputs:
            blob = BLOB_DATA(self.ieNet.inputs[key])
            self.input_blobs.append(blob)
            # print('Input Blob   : {}'.format(key))
            # print('- Layout     : {}'.format(self.ieNet.inputs[key].layout))
            # print('- Shape      : {}'.format(self.ieNet.inputs[key].shape))

        for key in self.ieNet.outputs:
            blob = BLOB_DATA(self.ieNet.outputs[key])
            self.output_blobs.append(blob)
            # print('Output Blob  : {}'.format(key))
            # print('- Layout     : {}'.format(self.ieNet.outputs[key].layout))
            # print('- Shape      : {}'.format(self.ieNet.outputs[key].shape))    

        logging.info('>> Loading model to {}'.format(target))
        self.execNet = self.ieCore.load_network(network = self.ieNet, device_name = target, num_requests = 1)

    def preprocess_for_inference(self, frame, confidence):
        """
        A wrapper to call per model pre-process routine
        """
        return self.preprocess_internal(frame, confidence)

    def run_inference(self, inference_data):
        """
        A wrapper to call per model inference execution routine
        """
        return self.run_inference_internal(inference_data)

    def annotate_frame_common(self, detection_List, frame):
        """
        Annotation function for most of object detection models.
        Receives list of detection results in the following format :
        Index      : Index of detected object
        Classid    : Index of detected class
        Confidence : Confidence Level
        Rect       : Coordinates to draw a bounding box
        """
        try:
            for item in detection_List:
                X1 = item[3]
                Y1 = item[4]
                X2 = item[5]
                Y2 = item[6]
                confidence = item[2]
                class_id = int(item[1])
                rect = [X1, Y1, X2, Y2]
                npdata = np.array(rect)

                if self.num_class < 20:
                    # Labels are only available for VOC (20), COCO (80, 90)
                    # Just add confidence level
                    color = self.colors[class_id]
                    annotation_text = '{0:.1f}%'.format(float(confidence*100))

                else:
                    color = self.colors[class_id]
                    annotation_text = '{0} {1:.1f}%'.format(self.classLabel[class_id], float(confidence*100))   

                frame = self.draw_rect(frame, npdata, annotation_text, color)

        except IndexError as error:
            logging.error('Index Error {} : {}'.format(class_id, error))

        return frame

    def draw_rect(self, frame, rect, label = None, color = (0,255,0)):
        """
        Add a bounding box and Annotation text if specified
        """        
        (X1, Y1, X2, Y2) = rect.astype('int')
        
        if label:

            if self.textSize[0] > (X2-X1):
                textY = Y1 - 5
            else:
                textY = Y1 + 5 + self.textSize[1]

            cv2.putText(frame, label, (X1 + 3, textY),
                        self.fontName, self.fontScale, color, self.fontThickness)        
 
        frame = cv2.rectangle(frame, (X1, Y1), (X2, Y2), color, self.lineThickness)
        
        return frame

    def load_label(self, output_key, param_name):
        """
        Set label for VOC and COCO based on # of classes in output parameter
        Also set color list for the # of labels
        """     
        output_layer = self.ieNet.layers[output_key]
        outputParams = self.ieNet.layers[output_key].params

        if param_name in outputParams:
            self.num_class = int(outputParams[param_name])
            print('  Num Classes {}'.format(self.num_class))

            if self.num_class == 91:
                logging.info("Loading Coco 90 Label")
                self.classLabel = coco_90_category_map
            elif self.num_class == 80 or self.num_class == 81:
                logging.info("Loading Coco 80 Label")
                self.classLabel = coco_80_category_map
            elif 'coco' in self.model_name:
                logging.info("Loading Coco 90 Label")
                self.classLabel = coco_90_category_map
            elif self.num_class == 21 or self.num_class == 20:
                logging.info("Loading VOC Label")
                self.classLabel = voc_category_map

            if self.num_class >= 20:
                # generate a list of random colors
                if len(INFERENCE_PROCESS_CORE.color_list) < self.num_class + 1:
                    INFERENCE_PROCESS_CORE.color_list = np.random.uniform(50, 255, size=(self.num_class + 1, 3))
            else:
                INFERENCE_PROCESS_CORE.color_list = color_list()

            self.colors = INFERENCE_PROCESS_CORE.color_list