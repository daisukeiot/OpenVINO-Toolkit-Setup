import sys
import logging
import traceback
import numpy as np
import cv2
from math import exp as exp
from label_map import coco_category_map, voc_category_map
from OpenVINO_Config import Output_Format, Input_Format, color_list, CV2_Draw_Info

class YoloParams:
    def __init__(self, param, side):
        self.num = 3 if 'num' not in param else int(param['num'])
        self.coords = 4 if 'coords' not in param else int(param['coords'])
        self.classes = 80 if 'classes' not in param else int(param['classes'])
        self.side = side
        self.anchors = [10.0, 13.0, 16.0, 30.0, 33.0, 23.0, 30.0, 61.0, 62.0, 45.0, 59.0, 119.0, 116.0, 90.0, 156.0,
                        198.0,
                        373.0, 326.0] if 'anchors' not in param else [float(a) for a in param['anchors'].split(',')]

        self.isYoloV3 = False

        if param.get('mask'):
            mask = [int(idx) for idx in param['mask'].split(',')]
            self.num = len(mask)

            maskedAnchors = []
            for idx in mask:
                maskedAnchors += [self.anchors[idx * 2], self.anchors[idx * 2 + 1]]
            self.anchors = maskedAnchors

            self.isYoloV3 = True # Weak way to determine but the only one.

    def log_params(self):
        params_to_print = {'classes': self.classes, 'num': self.num, 'coords': self.coords, 'anchors': self.anchors}
        [logging.info("         {:8}: {}".format(param_name, param)) for param_name, param in params_to_print.items()]

#
# For Faster RCNN models
#
class Object_Detection_Yolo_Processor():

    def __init__(self,
                 model_name,
                 input_format,
                 input_key,
                 input_shape,
                 input_layout,
                 output_format):

        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.model_name = model_name
        self.input_key = input_key
        self.input_shape = input_shape
        self.input_layout = input_layout
        self.input_format = input_format

        self.output_format = output_format

        self.reshape_data = dict()

        self.colors = color_list()
        self.draw_info = CV2_Draw_Info()
        self.num_class = 0
        self.classLabels = None

        logging.info('==================================================================')
        logging.info('Input Format  : {}'.format(self.input_format.name))
        logging.info('         Key  : {}'.format(self.input_key))
        logging.info('       Shape  : {}'.format(self.input_shape))
        logging.info('      Layout  : {}'.format(self.input_layout))
        logging.info('Output Format : {}'.format(self.output_format.name))

    def set_class_label(self, output_params):

        if 'classes' in output_params:
            self.num_class = max(int(output_params['classes']),self.num_class)

        if (self.num_class == 91 or self.num_class == 80 or self.num_class == 81) or 'coco' in self.model_name:
            logging.info("Loading Coco Label")
            self.classLabels = coco_category_map
        elif self.num_class == 21 or self.num_class == 20:
            logging.info("Loading VOC Label")
            self.classLabels = voc_category_map

    def process_for_inference(self, frame):

        frame_data = np.array([])

        if self.input_layout == 'NCHW':
            n, c, h, w = self.input_shape
            # resize based on shape
            frame_data = cv2.resize(frame, (w, h))
            # convert from H,W,C to C,H,W
            frame_data = frame_data.transpose((2,0,1))
            # convert to C,H,W to N,C,H,W
            frame_data = frame_data.reshape(self.input_shape)

        return frame_data, self.input_key

    def process_result(self, layers, results = None, frame_data = None, frame = None, confidence = 1):

        objects = list()

        for layer_name, out_blob in results.items():
            shape = self.reshape_data[layer_name]
            out_blob = out_blob.reshape(shape)
            layer_params = YoloParams(layers[layer_name].params, out_blob.shape[2])
            #layer_params.log_params()
            objects += self.parse_yolo_region(out_blob, frame_data.shape[2:],
                                            frame.shape[:-1], layer_params,
                                            confidence)

        objects = sorted(objects, key=lambda obj : obj['confidence'], reverse=True)

        for i in range(len(objects)):
            if objects[i]['confidence'] == 0:
                continue
            for j in range(i + 1, len(objects)):
                if self.intersection_over_union(objects[i], objects[j]) > 0.4:
                    objects[j]['confidence'] = 0

        # Drawing objects with respect to the --prob_threshold CLI parameter
        objects = [obj for obj in objects if obj['confidence'] >= confidence]

        origin_im_size = frame.shape[:-1]
        for obj in objects:

            if obj['xmax'] > origin_im_size[1] or obj['ymax'] > origin_im_size[0] or obj['xmin'] < 0 or obj['ymin'] < 0:
                continue

            # add 3 px padding
            left   = obj['xmin']
            top    = obj['ymin']
            right  = obj['xmax']
            bottom = obj['ymax']

            rect = [left, top, right, bottom]

            self.annotate(frame, rect, obj['confidence'], obj['class_id'] + 1)

    def parse_yolo_region(self, blob, resized_image_shape, original_im_shape, params, threshold):
        # ------------------------------------------ Validating output parameters ------------------------------------------
        _, _, out_blob_h, out_blob_w = blob.shape
        assert out_blob_w == out_blob_h, "Invalid size of output blob. It sould be in NCHW layout and height should " \
                                        "be equal to width. Current height = {}, current width = {}" \
                                        "".format(out_blob_h, out_blob_w)

        # ------------------------------------------ Extracting layer parameters -------------------------------------------
        orig_im_h, orig_im_w = original_im_shape
        resized_image_h, resized_image_w = resized_image_shape
        objects = list()
        predictions = blob.flatten()
        side_square = params.side * params.side

        # ------------------------------------------- Parsing YOLO Region output -------------------------------------------
        for i in range(side_square):
            row = i // params.side
            col = i % params.side
            for n in range(params.num):
                obj_index = self.entry_index(params.side, params.coords, params.classes, n * side_square + i, params.coords)
                scale = predictions[obj_index]
                if scale < threshold:
                    continue
                box_index = self.entry_index(params.side, params.coords, params.classes, n * side_square + i, 0)
                # Network produces location predictions in absolute coordinates of feature maps.
                # Scale it to relative coordinates.
                x = (col + predictions[box_index + 0 * side_square]) / params.side
                y = (row + predictions[box_index + 1 * side_square]) / params.side
                # Value for exp is very big number in some cases so following construction is using here
                try:
                    w_exp = exp(predictions[box_index + 2 * side_square])
                    h_exp = exp(predictions[box_index + 3 * side_square])
                except OverflowError:
                    continue
                # Depends on topology we need to normalize sizes by feature maps (up to YOLOv3) or by input shape (YOLOv3)
                w = w_exp * params.anchors[2 * n] / (resized_image_w if params.isYoloV3 else params.side)
                h = h_exp * params.anchors[2 * n + 1] / (resized_image_h if params.isYoloV3 else params.side)
                for j in range(params.classes):
                    class_index = self.entry_index(params.side, params.coords, params.classes, n * side_square + i,
                                            params.coords + 1 + j)
                    confidence = scale * predictions[class_index]
                    if confidence < threshold:
                        continue
                    objects.append(self.scale_bbox(x=x, y=y, h=h, w=w, class_id=j, confidence=confidence,
                                            h_scale=orig_im_h, w_scale=orig_im_w))
        return objects


    def entry_index(self, side, coord, classes, location, entry):
        side_power_2 = side ** 2
        n = location // side_power_2
        loc = location % side_power_2
        return int(side_power_2 * (n * (coord + classes + 1) + entry) + loc)


    def scale_bbox(self, x, y, h, w, class_id, confidence, h_scale, w_scale):
        xmin = int((x - w / 2) * w_scale)
        ymin = int((y - h / 2) * h_scale)
        xmax = int(xmin + w * w_scale)
        ymax = int(ymin + h * h_scale)
        return dict(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, class_id=class_id, confidence=confidence)

    def intersection_over_union(self, box_1, box_2):
        width_of_overlap_area = min(box_1['xmax'], box_2['xmax']) - max(box_1['xmin'], box_2['xmin'])
        height_of_overlap_area = min(box_1['ymax'], box_2['ymax']) - max(box_1['ymin'], box_2['ymin'])
        if width_of_overlap_area < 0 or height_of_overlap_area < 0:
            area_of_overlap = 0
        else:
            area_of_overlap = width_of_overlap_area * height_of_overlap_area
        box_1_area = (box_1['ymax'] - box_1['ymin']) * (box_1['xmax'] - box_1['xmin'])
        box_2_area = (box_2['ymax'] - box_2['ymin']) * (box_2['xmax'] - box_2['xmin'])
        area_of_union = box_1_area + box_2_area - area_of_overlap
        if area_of_union == 0:
            return 0
        return area_of_overlap / area_of_union

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