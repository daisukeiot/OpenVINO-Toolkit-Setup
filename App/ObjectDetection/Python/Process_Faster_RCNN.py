import sys
import logging
import traceback
import numpy as np
import cv2

from label_map import coco_80_class_map, coco_90_class_map, voc_class_map
from OpenVINO_Config import color_palette, CV2_Draw_Info
from OpenVINO_Util import OpenVINOUtil, ModelTypes


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
                 model_type,
                 info_key,
                 data_key,
                 data_shape,
                 data_layout,
                 output_key,
                 output_params):

        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.model_name = model_name
        self.model_type = model_type
        self.info_key = info_key
        self.data_key = data_key
        self.data_shape = data_shape
        self.data_layout = data_layout

        self.output_key = output_key

        self.prev_frame = None

        self.draw_info = CV2_Draw_Info()

        self.num_class, self.class_Label, self.has_background = OpenVINOUtil.get_class_label(modelType = model_type, output_param = output_params)

        self.colors = color_palette(self.num_class)

        logging.info('==================================================================')
        logging.info('Model Type   : {}'.format(self.model_type.value))
        logging.info('   Info Key  : {}'.format(self.info_key))
        logging.info('   Data Key  : {}'.format(self.data_key))
        logging.info('      Shape  : {}'.format(self.data_shape))
        logging.info('     Layout  : {}'.format(self.data_layout))
        logging.info(' Output Key  : {}'.format(self.output_key))
        logging.info(' Class Label : {} ({})'.format(self.class_Label, self.num_class))
        logging.info('  Background : {}'.format(self.has_background))

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
                break
            
            if result[2] < confidence:
                continue

            # add 3 px padding
            left   = np.int(imageW * result[3]) + 3
            top    = np.int(imageH * result[4]) + 3
            right  = np.int(imageW * result[5]) + 3
            bottom = np.int(imageH * result[6]) + 3

            rect = [left, top, right, bottom]

            print("Class {}".format(int(result[1])))
            if self.has_background:
                label_id = int(result[1]) - 1
            else:
                label_id = int(result[1])

            self.annotate(frame, rect, result[2], label_id)

        return frame

    def annotate(self, frame, rect, confidence, label_id):

        color = (255, 0, 0)
        annotation_text = "Unknown"

        try:
            if self.class_Label is not None:
                color = self.colors[label_id]
                annotation_text = '{0} {1:.1f}%'.format(self.class_Label.value[label_id], float(confidence*100))
            else:
                if self.num_class <= 2:
                    # only Yes/No (or detected / not detected)
                    color = self.colors[label_id]
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

