import sys
import logging
import numpy as np
from OpenVINO_Config import BLOB_DATA
import cv2
from Process_Core import INFERENCE_PROCESS_CORE, INFERENCE_DATA

class OBJECT_DETECTION_INFERENCE_DATA(INFERENCE_DATA):

    def __init__(self, frame, confidence):
        super().__init__(frame, confidence)

class OBJECT_DETECTION(INFERENCE_PROCESS_CORE):

    def __init__(self, model_name, xml_file, bin_file):
        super().__init__(model_name, xml_file, bin_file)
        
    def load_model(self, target='CPU'):
        self._load_model(target)

        if self.ieNet == None or self.execNet == None:
            logging.error('!! {0}:{1}() : Error loading model'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
            return False

        if len(self.output_blobs) == 1:
            output_key = next(iter(self.ieNet.outputs))
            self.load_label(output_key, 'num_classes')
        else:
            logging.error('!! {0}:{1}() : Object Detection Model with {2} outputs. 1 output expected.'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ))
            return False            

        return True

    def preprocess_internal(self, frame, confidence):
        """
        Convert image format for object detection inference
        Typically :

        Format : NCHW
        Shape  : 1 x 3 x Height x Width
        """
        inference_data = OBJECT_DETECTION_INFERENCE_DATA(frame, confidence)

        frame_data = np.array([])
        input_blob = next(iter(self.input_blobs))
        
        if input_blob.layout == 'NCHW':
            n, c, h, w = input_blob.shape
            # resize based on shape
            frame_data = cv2.resize(frame, (w, h))
            # convert from H,W,C to C,H,W
            frame_data = frame_data.transpose((2,0,1))
            # convert to C,H,W to N,C,H,W
            inference_data.input_frame = frame_data.reshape(input_blob.shape)
            # set input key name
            inference_data.input_key = input_blob.name
        else:
            logging.error('!! {0}:{1}() : Unexpected input Layout {2}.  NCHW expected.'.format(self.__class__.__name__, sys._getframe().f_code.co_name, input_blob.layout))

        return inference_data

    def run_inference_internal(self, inference_data):
        """
        Execute inference
        """
        return self.execNet.infer(inputs={inference_data.input_key : inference_data.input_frame})

    def process_result(self, results, inference_data):
        """
        A wrapper function to call internal result processing function
        """
        detection_List = self.process_humanpose_result(results, inference_data)
        
        return detection_List

    def process_humanpose_result(self, results, inference_data):
        """
        Process results for object detection results in 1x1xNx7 format

        The net outputs "detection_output" blob with shape: [1x1xNx7], where N is the number of detected object. 
        For each detection, the description has the format: [image_id, label, conf, x_min, y_min, x_max, y_max], 
        where:

            image_id - ID of image in batch
            label - ID of predicted class
            conf - Confidence for the predicted class
            (x_min, y_min) - Coordinates of the top left bounding box corner
            (x_max, y_max) - Coordinates of the bottom right bounding box corner.

        Returns a list of detected objects
        """
        detection_List = list()
        
        h, w = inference_data.frame_org.shape[:2]
        
        objects = results[self.output_blobs[0].name]
        
        for i in np.arange(0, objects.shape[2]):
        
            # check confidence level
            if objects[0, 0, i, 2] < inference_data.confidence:
                continue
                
            # use N as index for label and color
            object_index = i

            # compute rectangle for bounding box
            rect = objects[0, 0, i, 3:7] * np.array([w, h, w, h])
            (X1, Y1, X2, Y2) = rect.astype('int')

            # index, classid, confidence, rect
            detection_Item = (object_index, objects[0, 0, i, 1], objects[0, 0, i, 2], X1, Y1, X2, Y2)
            detection_List.append(detection_Item)

        return detection_List
    
    def annotate_frame(self, detection_List, frame):
        """
        A wrapper function to call annotation function.
        Calls generic annotation function.
        """
        return self.annotate_frame_common(detection_List, frame)