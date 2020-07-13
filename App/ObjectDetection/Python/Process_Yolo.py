import sys
import logging
import numpy as np
from OpenVINO_Config import BLOB_DATA
import cv2
from Process_Core import INFERENCE_PROCESS_CORE, INFERENCE_DATA
from math import exp as exp

class YOLO_DETECTION_INFERENCE_DATA(INFERENCE_DATA):

    def __init__(self, frame, confidence):
        super().__init__(frame, confidence)

class YOLO_PARAMS:
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

class YOLO_DETECTION(INFERENCE_PROCESS_CORE):

    def __init__(self, model_name, xml_file, bin_file):
        super().__init__(model_name, xml_file, bin_file)
        self.reshape_data = dict()
        
    def load_model(self, target='CPU'):
        self._load_model(target)

        if self.ieNet == None or self.execNet == None:
            logging.error('!! {0}:{1}() : Error loading model'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
            return False

        """
        Check expected # of inputs/outputs
        """
        output_key = next(iter(self.ieNet.outputs))
        self.load_label(output_key, 'classes')

        for key, blob in self.ieNet.outputs.items():
            self.reshape_data[key] = self.ieNet.layers[self.ieNet.layers[key].parents[0]].shape

        return True

    def preprocess_internal(self, frame, confidence):
        """
        Convert image format for Yolo inference
        Typically :

        Format : NCHW
        Shape  : 1 x 3 x Height x Width
        """
        inference_data = YOLO_DETECTION_INFERENCE_DATA(frame, confidence)

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
        detection_List = self.process_yolo_result(results, inference_data)
        
        return detection_List

    def process_yolo_result(self, results, inference_data):
        """
        """
        detection_List = list()

        for layer_name, out_blob in results.items():
            shape = self.reshape_data[layer_name]
            out_blob = out_blob.reshape(shape)
            layer_params = YOLO_PARAMS(self.ieNet.layers[layer_name].params, out_blob.shape[2])
            #layer_params.log_params()
            detection_List += self.parse_yolo_region(out_blob, inference_data.input_frame.shape[2:],
                                            inference_data.frame_org.shape[:-1], layer_params,
                                            inference_data.confidence)

        detection_List = sorted(detection_List, key=lambda obj : obj['confidence'], reverse=True)

        for i in range(len(detection_List)):
            if detection_List[i]['confidence'] == 0:
                continue
            for j in range(i + 1, len(detection_List)):
                if self.intersection_over_union(detection_List[i], detection_List[j]) > 0.4:
                    detection_List[j]['confidence'] = 0

        # Drawing detection_List with respect to the --prob_threshold CLI parameter
        detection_List = [obj for obj in detection_List if obj['confidence'] >= inference_data.confidence]

        return detection_List

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

    def annotate_frame(self, detection_List, frame):
        """
        A wrapper function to call annotation function.
        Calls generic annotation function.
        """
        frame_size = frame.shape[:-1]

        try:
            for item in detection_List:

                if item['xmax'] > frame_size[1] or item['ymax'] > frame_size[0] or item['xmin'] < 0 or item['ymin'] < 0:
                    continue

                # add 3 px padding
                X1 = item['xmin']
                Y1 = item['ymin']
                X2 = item['xmax']
                Y2 = item['ymax']

                confidence = item['confidence']
                class_id = item['class_id'] + 1
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