from math import trunc
import os
import sys
import logging
import traceback
from enum import Enum
from openvino.inference_engine import IECore, IENetwork
import ngraph as ng
from ngraph.impl import Node
from typing import Union, Dict, Optional, Tuple, List
from label_map import LabelMap

# API List
# https://docs.openvino.ai/2021.4/api/ngraph_python_api/_autosummary/ngraph.Function.html?highlight=get_parameters#ngraph-function

#https://github.com/openvinotoolkit/model_analyzer/blob/3b76aaeaf61c7b6bb3b119aa4d9c7f0e90d165a3/model_analyzer/network_metadata.py

class ModelTypes(Enum):
    CLASSIFICATION = 'classificator'
    SSD = 'ssd'
    YOLO_V1_TINY = 'Yolo v1 Tiny'
    YOLO_V2 = 'Yolo v2'
    YOLO_V2_TINY = 'Yolo v2 Tiny'
    YOLO_V3 = 'YOLO V3'
    YOLO_V3_ONNX = 'Yolo v3 ONNX'
    YOLO_V3_TINY = 'Yolo v3 Tiny'
    YOLO_V3_TINY_ONNX = 'Yolo v3 Tiny ONNX'
    YOLO_V4 = 'Yolo v4'
    YOLO_V4_TINY = 'Yolo v4 Tiny'
    YOLO_V4_BASE = "Yolo v4 Base"
    RESNET = "RCNN"
    SEMANTIC_SEGM = 'segmentation'
    INSTANCE_SEGM = 'mask_rcnn'
    INAPINTING = 'inpainting'
    STYLE_TRANSFER = 'style_transfer'
    SUPER_RESOLUTION = 'super_resolution'
    FACE_RECOGNITION = 'face_recognition'
    LANDMARK_DETECTION = 'landmark_detection'
    GENERIC = 'generic'
    UNKNOWN = 'unknown'

class YoloAnchors(Enum):
    yolo_v1_tiny = [1.0800000429153442, 1.190000057220459, 3.4200000762939453, 4.409999847412109, 6.630000114440918, 11.380000114440918, 9.420000076293945, 5.110000133514404, 16.6200008392334, 10.520000457763672]
    yolo_v2 =      [0.5727300047874451, 0.6773849725723267, 1.874459981918335, 2.062530040740967, 3.3384299278259277, 5.474339962005615, 7.882820129394531, 3.527780055999756, 9.770520210266113, 9.168279647827148]
    yolo_v3 =      [10.0, 13.0, 16.0, 30.0, 33.0, 23.0, 30.0, 61.0, 62.0, 45.0, 59.0, 119.0, 116.0, 90.0, 156.0, 198.0, 373.0, 326.0]
    yolo_v3_tiny = [10.0, 14.0, 23.0, 27.0, 37.0, 58.0, 81.0, 82.0, 135.0, 169.0, 344.0, 319.0]

class OpenVINOUtil:
    def __init__(self, network: IENetwork):
        self.ieNet = network
        self.ngFunction = ng.function_from_cnn(self.ieNet)
        self.ops = self.ngFunction.get_ordered_ops()

        # Get Parameters (Input)
        self.input_nodes = self.ngFunction.get_parameters()

        # Get Resulst (Output)
        self.output_nodes = list()

        for output_layer in self.ngFunction.get_results():
            self.output_nodes.append(output_layer.input(0).get_source_output().get_node())
    
    def get_ie_outputs(self) -> list:
        return [*self.ieNet.outputs]

    def get_ie_inputs(self) -> list:
        return [*self.ieNet.input_info]
    
    def get_node_types(self) -> list:
        return [node.get_type_name() for node in self.ops]

    def get_params(self):
        if len(self.output_nodes) < 1:
            return None

        output = self.output_nodes[0]

        if isinstance(output, Node):
            params = output._get_attributes()
        else:
            params = output.params

        return params

    @staticmethod
    def get_class_label(modelType, output_param) -> Tuple:

        classLabel = None
        background = False
        num_class = 0

        print(output_param)

        if modelType == ModelTypes.SSD or \
           modelType == ModelTypes.RESNET :
            num_class = output_param['num_classes']

            if 'background_label_id' in output_param:
                background = True

        elif modelType == ModelTypes.YOLO_V1_TINY or \
                modelType == ModelTypes.YOLO_V2 or \
                modelType == ModelTypes.YOLO_V2_TINY or \
                modelType == ModelTypes.YOLO_V3 or \
                modelType == ModelTypes.YOLO_V3_TINY:

            num_class = output_param['classes']
            
            if 'background_label_id' in output_param:
                background = True

        if num_class == 90:
            logging.info("Loading Coco 90 Label")
            classLabel = LabelMap.COCO90
            background = False
        if num_class == 91:
            logging.info("Loading Coco 90 Label")
            classLabel = LabelMap.COCO90
            background = True
        elif num_class == 80:
            logging.info("Loading Coco 80 Label")
            classLabel = LabelMap.COCO80
            background = False
        elif num_class == 81:
            logging.info("Loading Coco 80 Label")
            classLabel = LabelMap.COCO80
            background = True
        elif num_class == 20:
            logging.info("Loading VOC Label")
            classLabel = LabelMap.VOC20
        elif num_class == 21:
            logging.info("Loading VOC Label")
            classLabel = LabelMap.VOC20
            background = True
        else:
            logging.info("Unknown Class {}".format(num_class))

        return num_class, classLabel, background

    @staticmethod
    def dump(obj):
       for attr in dir(obj):
           if hasattr( obj, attr ):
               print( "obj.%s = %s" % (attr, getattr(obj, attr)))
    
    @staticmethod
    def _get_ngraph_output_shape(layer: Node, port: int = 0) -> tuple:
        partial_shape = layer.output(port).get_partial_shape()
        if partial_shape.is_dynamic:
            return ()
        return partial_shape.to_shape()

    def check_model_type(self) -> ModelTypes:

        model_types = {
            ModelTypes.CLASSIFICATION: self._is_model_classification,
            ModelTypes.SSD: self._is_model_ssd,
            ModelTypes.YOLO_V1_TINY: self._is_model_tiny_yolo_v1,
            ModelTypes.YOLO_V2: self._is_model_yolo_v2,
            ModelTypes.YOLO_V2_TINY: self._is_model_yolo_v2_tiny,
            ModelTypes.YOLO_V3: self._is_model_yolo_v3,
            ModelTypes.YOLO_V3_TINY: self._is_model_yolo_v3_tiny,
            ModelTypes.YOLO_V3_TINY_ONNX: self._is_model_yolo_v3_tiny_onnx,
            ModelTypes.YOLO_V3_ONNX: self._is_model_yolo_v3_onnx,
            ModelTypes.YOLO_V4: self._is_model_yolo_v4,
            ModelTypes.YOLO_V4_TINY: self._is_model_yolo_v4_tiny,
            ModelTypes.YOLO_V4_BASE: self._is_model_yolo_v4_base,
            ModelTypes.RESNET: self._is_model_resnet
            # ModelTypes.INSTANCE_SEGM: self._is_instance_segmentation,
            # ModelTypes.SEMANTIC_SEGM: self._is_semantic_segmentation,
            # ModelTypes.INAPINTING: self._is_inpainting,
            # ModelTypes.STYLE_TRANSFER: self._is_style_transfer,
            # ModelTypes.SUPER_RESOLUTION: self._is_super_resolution,
            # ModelTypes.FACE_RECOGNITION: self._is_face_recognition,
            # ModelTypes.LANDMARK_DETECTION: self._is_landmark_detection
        }

        for t_type, t_detector in model_types.items():
            if t_detector():
                return t_type
        return ModelTypes.GENERIC

    def _is_model_classification(self) -> bool:
        if len(self.output_nodes) != 1:
            return False

        layer_types = set(self.get_node_types())
        excluded_types = {'PRelu', 'NormalizeL2'}
        valid_layer_types = not layer_types & excluded_types

        out_layer = self.output_nodes[0]
        out_shape = self._get_ngraph_output_shape(out_layer)

        minimal_shape = len(out_shape) == 2
        reduced_shapes = out_shape[2] == out_shape[3] == 1 and out_shape[1] > 1

        # To qualify, the outputs' HW shapes must either be missing or equal 1
        return (minimal_shape or reduced_shapes) and valid_layer_types

    def _is_model_ssd(self) -> bool:

        if len(self.input_nodes) != 1 or len(self.output_nodes) != 1:
            return False

        input = self.ieNet.input_info[next(iter(self.ieNet.input_info))]
        output = self.ieNet.outputs[next(iter(self.ieNet.outputs))]

        if input.layout != 'NCHW' or output.layout != 'NCHW':
            return False

        if len(output.shape) !=4:
            return False

        if output.shape[0] != 1 or output.shape[1] != 1 or output.shape[3] != 7:
            return False

        node_types = set(self.get_node_types())
        output_types = {node.get_type_name() for node in self.output_nodes}

        return 'ROIPooling' not in node_types and 'DetectionOutput' in output_types

    def _get_yolo_anchor(self) -> Optional[List[float]]:
        region = [output for output in self.output_nodes if output.get_type_name() == 'RegionYolo']
        if region:
            return region[0]._get_attributes().get('anchors', [])

    def _is_yolo(self) -> bool:
        layer_types = set(self.get_node_types())

        return 'RegionYolo' in layer_types

    def _is_model_tiny_yolo_v1(self) -> bool:
        
        if self._is_yolo() and len(self.output_nodes) == 1:
            anchors = self._get_yolo_anchor() 
            return anchors == YoloAnchors.yolo_v1_tiny.value

        return False

    def _is_model_yolo_v2(self) -> bool:

        if self._is_yolo() and len(self.output_nodes) == 1:
            anchors = self._get_yolo_anchor() 
            if anchors == YoloAnchors.yolo_v2.value:
                if self.output_nodes[0].output(0).get_partial_shape().to_shape()[1] == 153425:
                    return True

        return False

    def _is_model_yolo_v2_tiny(self) -> bool:

        if self._is_yolo() and len(self.output_nodes) == 1:
            anchors = self._get_yolo_anchor() 
            if anchors == YoloAnchors.yolo_v2.value:
                if self.output_nodes[0].output(0).get_partial_shape().to_shape()[1] == 71825:
                    return True

        return False
    
    def _is_model_yolo_v3_onnx(self) -> bool:

        if self._is_yolo():
            return False
        elif len(self.output_nodes) != 3 or len(self.input_nodes) != 2:
            return False
        else:
            if len(self.input_nodes) == 2 and len(self.output_nodes) == 3:
                for output in self.output_nodes:
                    if not output.get_output_partial_shape(0).is_dynamic:
                        if 'yolonms_layer_1' not in output.get_friendly_name():
                            return False
                        elif output.shape[-1] == 4:
                            if output.shape[-2] != 10647:
                                return False
                        elif output.shape[-1] == 3:
                            if output.shape[0] != 1600:
                                return False
                        elif output.shape[1] == 80:
                            if output.shape[2] != 10647:
                                return False
                return True
        return False

    def _is_model_yolo_v3(self) -> bool:

        if self._is_yolo() and len(self.output_nodes) == 3:
            anchors = self._get_yolo_anchor() 

            return anchors == YoloAnchors.yolo_v3.value

        return False

    def _is_model_yolo_v3_tiny_onnx(self) -> bool:

        if self._is_yolo():
            return False
        elif len(self.output_nodes) != 3 or len(self.input_nodes) != 2:
            return False
        else:
            for output in self.output_nodes:
                if not output.get_output_partial_shape(0).is_dynamic:
                    if 'yolonms_layer_1' not in output.get_friendly_name():
                        return False
                    elif output.shape[-1] == 4:
                        if output.shape[-2] != 2535:
                            return False
                    elif output.shape[-2] == 3:
                        if output.shape[1] != 1600:
                            return False
                    elif output.shape[1] == 80:
                        if output.shape[2] != 2535:
                            return False
            return True
        return False
    
    def _is_model_yolo_v3_tiny(self) -> bool:

        if self._is_yolo() and len(self.output_nodes) == 2:
            anchors = self._get_yolo_anchor() 

            return anchors == YoloAnchors.yolo_v3_tiny.value

        return False

    def _is_model_yolo_v4(self) -> bool:

        if self._is_yolo():
            return False
        elif len(self.output_nodes) != 3 or len(self.input_nodes) != 1:
            return False
        else:
            for node in self.output_nodes:
                if not 'StatefulPartitionedCall/model/conv2d' in node.get_friendly_name() and not '/separable_conv2d/YoloRegion' in node.get_friendly_name():
                    return False

            return True

        return False

    def _is_model_yolo_v4_tiny(self) -> bool:

        if self._is_yolo():
            return False
        elif len(self.output_nodes) != 2 or len(self.input_nodes) != 1:
            return False
        else:
            for node in self.output_nodes:
                if not 'conv2d_20/BiasAdd/Add' in node.get_friendly_name() and not 'conv2d_17/BiasAdd/Add' in node.get_friendly_name():
                    return False

            return True
        return False

    def _is_model_yolo_v4_base(self) -> bool:

        if self._is_yolo():
            if len(self.output_nodes) == 3 and len(self.input_nodes) == 1:
                return True

        return False

    def _is_model_resnet(self) -> bool:

        if len(self.output_nodes) == 1 and len(self.input_nodes) == 2:

            for key, blob in self.ieNet.input_info.items():

                if key == 'image_info':
                    info_key = key
                elif key == 'image_tensor' or key == 'image':
                    data_key = key

            if len(info_key) > 0 and len(data_key) > 0:
                return True

        return False 