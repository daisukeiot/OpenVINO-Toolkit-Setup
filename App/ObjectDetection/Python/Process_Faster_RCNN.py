import sys
import logging
import traceback
import numpy as np
import cv2

from label_map import coco_category_map, voc_category_map
from OpenVINO_Config import Output_Format, Input_Format, color_list, CV2_Draw_Info



#
# For Faster RCNN models
#
class RCNN_Inference_Data():
    def __init__(self,
                 image_info,
                 info_key,
                 image_data,
                 data_key):

        self.info_key   = info_key
        self.image_info = image_info
        self.data_key   = data_key
        self.image_data = image_data

class Object_Detection_RCNN_Processor():
    def __init__(self, 
                 model_name,
                 input_format,
                 info_key,
                 data_key,
                 data_shape,
                 data_layout,
                 output_format,
                 output_key,
                 output_params):

        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.model_name = model_name
        self.info_key = info_key
        self.data_key = data_key
        self.data_shape = data_shape
        self.data_layout = data_layout
        self.input_format = input_format

        self.output_key = output_key
        self.output_format = output_format

        self.colors = color_list()
        self.draw_info = CV2_Draw_Info()

        if 'num_classes' in output_params:
            self.num_class = int(output_params['num_classes'])
        else:
            self.num_class = 0

        if (self.num_class == 91 or self.num_class == 80 or self.num_class == 81) or 'coco' in self.model_name:
            logging.info("Loading Coco Label")
            self.classLabels = coco_category_map
        elif self.num_class == 21 or self.num_class == 20:
            logging.info("Loading VOC Label")
            self.classLabels = voc_category_map

        logging.info('==================================================================')
        logging.info('Input Format  : {}'.format(self.input_format.name))
        logging.info('    Info Key  : {}'.format(self.info_key))
        logging.info('    Data Key  : {}'.format(self.data_key))
        logging.info('       Shape  : {}'.format(self.data_shape))
        logging.info('      Layout  : {}'.format(self.data_layout))
        logging.info('Output Format : {}'.format(self.output_format.name))
        logging.info('         Key  : {}'.format(self.output_key))
        logging.info('  num_class   : {}'.format(self.num_class))

    def process_for_inference(self, frame):

        inference_Data = None

        if self.data_layout == 'NCHW':
            n, c, h, w = self.data_shape
            # resize based on shape
            frame_data = cv2.resize(frame, (w, h))
            # convert from H,W,C to C,H,W
            frame_data = frame_data.transpose((2,0,1))
            # convert to C,H,W to N,C,H,W
            frame_data = frame_data.reshape(self.data_shape)
            # create image_info
            image_info  = np.asarray([w, h, 1], dtype=np.float32)

            inference_Data = RCNN_Inference_Data(image_info = image_info, info_key = self.info_key, image_data = frame_data, data_key = self.data_key)

        return inference_Data


    def process_result(self, results = None, frame = None, confidence = 1):
        rect = {}

        imageH, imageW = frame.shape[:-1]

        for result in results[self.output_key][0][0]:

            if result[0] == -1:
                return
            
            if result[2] < confidence:
                continue

            # add 3 px padding
            left   = np.int(imageW * result[3]) + 3
            top    = np.int(imageH * result[4]) + 3
            right  = np.int(imageW * result[5]) + 3
            bottom = np.int(imageH * result[6]) + 3

            rect = [left, top, right, bottom]

            self.annotate(frame, rect, result[2], int(result[1]))

    def annotate(self, frame, rect, confidence, label_id):

        try:
            if self.num_class <= 2:
                # only Yes/No (or detected / not detected)
                color = self.colors[0]
                annotation_text = '{0:.1f}%'.format(float(confidence*100))
            elif self.num_class < 20:
                
                if len(self.colors) >= self.num_class:
                    # different color for each object (up to 4)
                    color = self.colors[label_id]
                else:
                    color = self.colors[0]
                annotation_text = '{0:.1f}%'.format(float(confidence*100))
            else:
                if len(self.classLabels) >= self.num_class:
                    color = self.colors[0]
                    annotation_text = '{0} {1:.1f}%'.format(self.classLabels[label_id], float(confidence*100))
                else:
                    color = self.colors[0]
                    annotation_text = '{0:.1f}%'.format(float(confidence*100))

        except IndexError as error:
            logging.error('Index Error {} : {}'.format(label_id, error))

        except Exception as ex:
            logging.error('Exception finding label {} : {}'.format(label_id, ex))

        x1 = max(rect[0], 0)
        y1 = max(rect[1], 0)
        x2 = min(rect[2], frame.shape[1])
        y2 = min(rect[3], frame.shape[0])

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        cv2.putText(img = frame, 
                    text = annotation_text, 
                    org = (x1 + 5, y1 + int(self.draw_info.textSize[1] * 1.5)),
                    fontFace = self.draw_info.fontName,
                    fontScale = self.draw_info.fontScale,
                    color     = color,
                    thickness = self.draw_info.thickness,
                    lineType = self.draw_info.lineType)

