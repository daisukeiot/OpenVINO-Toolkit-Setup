from enum import Enum, IntFlag, auto, IntEnum
import sys
import logging
import cv2

class CV2_Draw_Info():

    def __init__(self):
        self.fontScale = 0.8
        self.thickness = 1
        self.lineType = cv2.LINE_AA
        self.fontName = cv2.FONT_HERSHEY_COMPLEX_SMALL
        self.textSize, self.textBaseline = cv2.getTextSize('%', self.fontName, self.fontScale, self.thickness)
       
def color_list():
    colors = []
    colors.append((232, 35, 244))
    colors.append((0, 241, 255))
    colors.append((255, 236, 0))
    colors.append((242, 188, 0))
    return colors

class Output_Format(IntEnum):
    Unknown = 0
    DetectionOutput = 1
    Softmax = 2
    Mconv7_stage2_L1 = 3
    Faster_RCNN = 4
    RegionYolo = 5

class Input_Format(IntEnum):
    Unknown = 0
    Tensorflow = 1
    Caffe = 2
    Faster_RCNN = 3
    IntelIR = 4
    Yolo = 5
    Other = 6

class Engine_State(IntFlag):
    Unknown = auto()
    Initialized = auto()
    Has_OpenVINO_Tool = auto()
    Running = auto()
    Stop = auto()
    Pause = auto()
    LoadModel = auto()

class Model_Flag(IntFlag):
    Uninitialized = auto()
    HasPostProc = auto()
    Downloaded = auto()
    Converted = auto()
    Loaded = auto()
    Unsupported = auto()
    LoadError = auto()

class OpenVINO_Model_Data():
    def __init__(self, 
                 modelName,
                 folderName,
                 framework,
                 task_type,
                 model_file = "",
                 archive_format = "",
                 flag = Model_Flag.Uninitialized):

        self._debug = True
        self.modelName = modelName
        self.folderName = folderName
        self.framework = framework
        self.task_type = task_type
        self.model_file = model_file
        self.archive_format = archive_format
        self.model_dir = None
        self.ir_dir = None
        self.flag = flag
        self.errorMsg = ""

    def to_json(self):
        return '{{\"modelName\":\"{}\"}}'.format(self.modelName)
        # return json.dumps(self, default=lambda o: o.__dict__)

    def dump_model_data(self):
        if self._debug:
            logging.info('Model Name  : {}'.format(self.modelName))
            logging.info('  Framework : {}'.format(self.framework))
            if self.flag & Model_Flag.HasPostProc:
                logging.info('  Archive   : {}'.format(self.model_file))
                logging.info('  Format    : {}'.format(self.archive_format))

    def setFlag(self, flag):
        self.flag |= flag

    def clearFlag(self, flag):
        self.flag |= ~flag

    def isFlagSet(self, flag):
        return ((self.flag & flag) == flag)
