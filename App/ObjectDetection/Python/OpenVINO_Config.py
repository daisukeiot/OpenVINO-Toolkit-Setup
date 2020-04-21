from enum import Enum, IntFlag, auto
import sys
import logging

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
