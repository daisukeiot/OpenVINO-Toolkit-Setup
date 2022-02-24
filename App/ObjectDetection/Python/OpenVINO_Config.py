from enum import Enum, IntFlag, auto, IntEnum
import sys
import logging
import cv2
import numpy as np
import seaborn as sns
import colorsys

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

def hsv2rgb(h, s, v):
    return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))

def hls2rgb(h, s, v):
    return tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, s, v))

def color_palette2(numClasses):

    if numClasses == 2:
        # this is just Yes/No.
        colors = []
        colors.append((232, 35, 244))
        colors.append((0, 241, 255))
        return colors

    elif numClasses == 3:
        # this is just Yes/No.
        colors = []
        colors.append((232, 35, 244))
        colors.append((0, 241, 255))
        colors.append((255, 236, 0))
        return colors

    #colors = ((np.array(color_palette("hls", 80)) * 255)).astype(np.uint8)
    colorPalette = sns.color_palette(palette="Paired", n_colors = numClasses)
    colorPalette = sns.hls_palette(n_colors = numClasses, h = 0.3, l = 0.5, s=0.9)
    # colorPalette = sns.color_palette('Paired', n_colors = numClasses)
    return [hsv2rgb(*hsv) for hsv in colorPalette]
    #return [hls2rgb(*hsv) for hsv in colorPalette]


def HSVToRGB(h, s, v): 
    (r, g, b) = colorsys.hsv_to_rgb(h, s, v) 
    return (int(255*r), int(255*g), int(255*b)) 
 
def color_palette(numClasses): 
    if numClasses == 2:
        # this is just Yes/No.
        colors = []
        colors.append((232, 35, 244))
        colors.append((0, 241, 255))
        return colors

    huePartition = 1.0 / (numClasses + 1) 
    return [HSVToRGB(huePartition * value, 0.5, 1.0) for value in range(0, numClasses)]


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
        self.download_dir = None
        self.ir_dir = None
        self.flag = flag
        self.errorMsg = ""

    def to_json(self):
        return '{{\"modelName\":\"{}\",\"taskType\":\"{}\"}}'.format(self.modelName,self.task_type)
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
