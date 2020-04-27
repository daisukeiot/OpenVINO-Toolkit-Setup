import sys
import logging
import traceback
import time
import cv2
import asyncio
import numpy as np
from FPS import FPS
from enum import IntEnum
import json
from OpenVINO_Engine import OpenVINO_Util, OpenVINO_Engine
from OpenVINO_Config import Engine_State, Model_Flag
from concurrent.futures import ThreadPoolExecutor, CancelledError
from WebServer import ImageStreamHandler
from pathlib import Path
from Video_Data import Video_Data, Video_Device_Type, Video_Data_State, Video_Playback_Mode
import youtube_dl

class VideoProcessorState(IntEnum):
    Unknown = 0
    Running = 1
    Stop = 2
    Pause = 3
    Error = 4

class VideoProcessor(object):
    #
    # Initialization of Video Processor Class
    # Reads video frame from Video Stream class and process (AI Inference etc)
    # Set frame data to displayFrame for visualization
    #
    def __init__(self,
                 videoPath = '/dev/video0',
                 videoW = 1024,
                 videoH = 768,
                 fontScale = 1.0,
                 verbose = True):

        self.verbose = verbose
        self._debug = False

        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        logging.info('===============================================================')
        logging.info('Initializing Video Processor with the following parameters:')
        logging.info('   - OpenCV Version     : {}'.format(cv2.__version__))
        logging.info('   - Device Path        : {}'.format(videoPath))
        logging.info('   - Frame Size         : {}x{}'.format(videoW, videoH))
        logging.info('===============================================================')

        # Video source
        self.videoData = Video_Data(self, videoPath)
        self.displayFrame = np.array([])
        self.frame_org = np.array([])

        # for Frame Rate measurement
        self.fps = FPS()

        playback_mode = self.videoData.get_playback_mode()
        self._playback_sync = (playback_mode == Video_Playback_Mode.Sync)
        self._fps_target = 30
        self._fps_wait = 1000.0/30
        self.currentFps = 30.0

        # For display
        self._fontScale = float(fontScale)
        self._annotate = False

        # Track states of this object
        self.set_video_processor_state(VideoProcessorState.Unknown)

        # To send message to clients (Browser)
        self.imageStreamHandler = None
        self.threadExecutor = None

        # OpenVINO
        self.inference_engine = None
        self.runInference = 0

        self.ioLoop = None
        self.current_model_data = None

#
# Sets up Video Processor Class
# Creates Video Stream Class for video capture
#
    def __enter__(self):
    # async def __aenter__(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.set_video_path('{{\"set_video_path\":\"{}\"}}'.format(self.videoData.videoPath))

        self.inference_engine = OpenVINO_Engine(self)

        # with OpenVINO_Util() as openVino:
        #     devices = openVino.get_supported_devices()

        #     for device in devices:
        #         logging.info('>> Device : {0}'.format(device))
        #         fullName = openVino.get_device_name(device)
        #         logging.info('>> Name   : {0}'.format(fullName))
        #         self.inference_engine.hwList.append(device)

        self.inference_engine.initialize_engine()

        return self

#
# Clean up Video Processor Class
#
    def __exit__(self, exception_type, exception_value, traceback):
    # async def __aexit__(self, exception_type, exception_value, traceback):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.threadExecutor:
            self.threadExecutor.shutdown(wait=True)

        self.set_video_processor_state(VideoProcessorState.Stop)

#
# Send message to browser
#
    def send_message(self, msg):
        if self.imageStreamHandler:
            ImageStreamHandler.broadcast_message(msg)

#
# Set Video Processor State flag
#
    def set_video_processor_state(self, flag):
        self._state = flag

#
# Initializes Video Source
#
    def _init_video_source(self):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        raise NotImplementedError

#
# Sets current video frame for display
#
    def set_display_frame(self, frame):
        assert frame.size > 0, "Frame Empty"
        self.displayFrame = frame

#
# Resturns current video frame for display
# Converts to byte data
#
    def get_display_frame(self):

        if self.displayFrame.size == 0:
            wallpaper = np.zeros((self.videoData.videoH, self.videoData.videoW, 3), np.uint8)
            ret, buffer = cv2.imencode( '.jpg', wallpaper )
        else:
            ret, buffer = cv2.imencode( '.jpg', self.displayFrame )

        if ret and buffer.size > 0:
            return buffer.tobytes(), self.currentFps
        else:
            assert(False), '>> Display Frame Empty *************** '

#
# Resturns Inference Engine Info
#
    def get_inference_engine_info(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.inference_engine:
            devices = json.dumps(self.inference_engine.get_devices())
            if self.runInference == 1:
                state = "On"
            else:
                state = "Off"

            return '{{\"{0}\":\"{1}\",\"devices\":{2},\"get_inference_state\":\"{3}\"}}'.format(sys._getframe().f_code.co_name, self.inference_engine.signature, devices, state)

        else:
            assert False, '>> {} : Inference Engine Not Set'.format(sys._getframe().f_code.co_name)
            return '{{\"{}\":\"Inference Engine Not Set\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name)

#
# Retrieve a list of models
#
    def get_model_list(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.inference_engine:

            json_data = json.loads('{\"get_model_list\":[]}')

            model_list = self.inference_engine.get_model_list()
            for model in model_list:
                json_data["get_model_list"].append(json.loads(model.to_json()))

        else:
            assert False, '>> {} : Inference Engine Not Set'.format(sys._getframe().f_code.co_name)
            return '{{\"{}\":\"Inference Engine Not Set\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name)

        return json_data

#
# Set to keep FPS for video or not
#
    def playback_mode(self, msg):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        jsonData = json.loads(msg)
        playback_mode = jsonData["playback_mode"]

        self._playback_sync = playback_mode == "0"
        self.videoData.set_playback_mode(playback_mode)

        return '{{\"playback_mode\":\"{0}\"}}'.format(self.videoData.get_playback_mode())

#
# Stop video process
#
    def set_video_playback(self, msg):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        jsonData = json.loads(msg)

        if jsonData['set_video_playback'] == "1":
            self.set_video_processor_state(VideoProcessorState.Running)
        else:
            self.set_video_processor_state(VideoProcessorState.Pause)

        return self.get_video_playback()

#
# Return current video playback state
#
    def get_video_playback(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self._state == VideoProcessorState.Pause:
            state = "0"
        elif self._state == VideoProcessorState.Running:
            state = "1"
        else:
            assert False, "Unexpected Video Processor State"

        return '{{\"get_video_playback\":\"{}\"}}'.format(state)

#
# Stop video process
#
    def set_video_stop(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.videoData.set_video_playback(isPause = True)
        self.set_video_processor_state(VideoProcessorState.Pause)

#
# Start video process
#
    def set_video_start(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.fps.reset(self.videoData.get_video_fps())
        self.videoData.set_video_playback(isPause = False)
        self.set_video_processor_state(VideoProcessorState.Running)

#
# Set Video Resolution
#
    def set_video_path(self, msg, loop = None):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        jsonData = json.loads(msg)

        if jsonData.get("set_video_path"):
            videoPath = jsonData["set_video_path"]
        else:
            videoPath = jsonData["videoPath"]

        self.set_video_processor_state(VideoProcessorState.Pause)

        video_data_state = self.videoData.set_video_path(videoPath, loop)

        if video_data_state == Video_Data_State.Running:
            self.fps.reset(self.videoData.get_video_fps())
            self.set_video_start()
        else:
            self.set_video_processor_state(VideoProcessorState.Pause)

        return self.get_video_path()

#
# Return current video path
#
    def get_video_path(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        
        return self.videoData.get_video_path()

#
# Set Video Resolution
#
    def set_video_resolution(self, msg):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return self.videoData.set_video_resolution(msg)
#
# Get Video Resolution
#
    def get_video_resolution(self):

        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return self.videoData.get_video_resolution()
#
# Set AI model to use
#
    async def set_ai_model(self, loop, msg):
        if self.verbose:
            logging.info('>> {0}:{1}() {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, msg))

        try:
            self.ioLoop = loop

            #1 Get Model Data
            model_data = self.inference_engine.get_ai_model_data(msg)

            current_hw        = json.loads(self.inference_engine.get_target_device())
            current_precision = json.loads(self.inference_engine.get_precision())

            if model_data.isFlagSet(Model_Flag.Loaded):
                json_data = json.loads(msg)
                device = json_data["set_target_device"]
                precision = json_data["set_precision"]

                if current_hw['get_target_device'] == device and current_precision['get_precision'] == precision:
                    logging.info(">> Model {} is loaded to {} {} {} {}".format(model_data.modelName, current_hw))
                    self.runInference = 1
                    self.send_message('{{\"set_ai_model\":\"Running {}\",\"isComplete\":1}}'.format(model_data.modelName))
            else:
                if self.current_model_data:
                    self.current_model_data.clearFlag(Model_Flag.Loaded)
                    self.current_model_data = None

            if not model_data is None:
                self.set_device_params(msg)
                # self.set_precision(msg)
                # self.set_target_device(msg)

                # create a task to download model from model zoo
                self.set_video_processor_state(VideoProcessorState.Pause)
                self.send_message('{{\"set_ai_model\":\"Downloading {}\"}}'.format(model_data.modelName))
                task = self.ioLoop.run_in_executor(None, self.inference_engine.download_model, model_data)
                task.add_done_callback(self.model_download_callback)
            else:
                json_data = json.loads(msg)
                self.send_message('{{\"set_ai_model\":\"Failed to get model data for {}\",\"isFailure\":1}}'.format(json_data["SetAiModel"]))

        except CancelledError:
            logging.info('-- {0}() - Cancelled'.format(sys._getframe().f_code.co_name))

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))
#
# Callback function for model download
#
    def model_download_callback(self, future):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        model_data = future.result()

        assert(model_data is not None, "Model Data is None")

        if model_data.isFlagSet(Model_Flag.Downloaded):

            self.send_message('{{\"set_ai_model\":\"{} downloaded.  Converting to IR\"}}'.format(model_data.modelName))

            if model_data.framework == 'dldt':
                task = self.ioLoop.run_in_executor(None, self.inference_engine.load_model, model_data)
                task.add_done_callback(self.model_load_callback)
            else:
                task = self.ioLoop.run_in_executor(None, self.inference_engine.convert_model, model_data)
                task.add_done_callback(self.model_convert_callback)
        else:
            self.set_video_start()
            self.send_message('{{\"set_ai_model\":\"Download failed {}\",\"isFailure\":1}}'.format(model_data.errorMsg))

#
# Callback function for model conversion
#
    def model_convert_callback(self, future):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        model_data = future.result()

        if model_data.isFlagSet(Model_Flag.Converted):
            logging.info('   FP16 {}'.format(str(model_data.ir_dir['FP16'])))
            logging.info('   FP32 {}'.format(str(model_data.ir_dir['FP32'])))
            self.send_message('{{\"set_ai_model\":\"{} converted to IR.\\nLoading....\", \"isSuccess\":1}}'.format(model_data.modelName))
            self.inference_engine.remove_model_dir(model_data)
            task = self.ioLoop.run_in_executor(None, self.inference_engine.load_model, model_data)
            task.add_done_callback(self.model_load_callback)
        else:
            self.set_video_start()
            self.send_message('{{\"set_ai_model\":\"Convert Failed : {}\",\"isFailure\":1}}'.format(model_data.errorMsg))

#
# Callback function for model load
#
    def model_load_callback(self, future):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        model_data = future.result()

        self.set_video_start()

        if model_data.isFlagSet(Model_Flag.Loaded):

            target_device = json.loads(self.inference_engine.get_target_device())
            
            self.send_message('{{\"set_ai_model\":\"Successfully loaded {}\", \"isComplete\":1}}'.format(model_data.modelName))
            self.send_message('{{\"get_inference_engine_info\":\"{} running on {}\"}}'.format(self.inference_engine.signature, target_device['get_target_device']))
            self.current_model_data = model_data
        else:
            self.send_message('{{\"set_ai_model\":\"Load failed : {}\",\"isFailure\":1}}'.format(model_data.errorMsg))

#
# Set hardware to run inference on
#
    def set_device_params(self, msg, reload = False):
        if self.verbose:
            logging.info('>> {0}:{1}() {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, msg))

        if self.inference_engine:
            self.inference_engine.set_target_device(msg)
            self.inference_engine.set_precision(msg)

            if reload == True and self.current_model_data:
                # create a task to download model from model zoo
                self.set_video_processor_state(VideoProcessorState.Pause)
                self.send_message('{{\"set_ai_model\":\"Loading {}\"}}'.format(self.current_model_data.modelName))
                task = self.ioLoop.run_in_executor(None, self.inference_engine.load_model, self.current_model_data)
                task.add_done_callback(self.model_download_callback)

            return self.inference_engine.set_target_device(msg)
        else:
            assert False, '>> {} : Inference Engine Not Set'.format(sys._getframe().f_code.co_name)
            return '{{\"{}\":\"Inference Engine Not Set\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name)

#
# Set hardware to run inference on
#
    # def set_target_device(self, msg):
    #     if self.verbose:
    #         logging.info('>> {0}:{1}() {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, msg))

    #     if self.inference_engine:
    #         self.inference_engine.set_target_device(msg)
    #         self.inference_engine.set_precision(msg)

    #         if self.current_model_data:
    #             # create a task to download model from model zoo
    #             self.set_video_processor_state(VideoProcessorState.Pause
    #             self.send_message('{{\"set_ai_model\":\"Loading {}\"}}'.format(self.current_model_data.modelName))
    #             task = self.ioLoop.run_in_executor(None, self.inference_engine.load_model, self.current_model_data)
    #             task.add_done_callback(self.model_download_callback)

    #         return self.inference_engine.set_target_device(msg)
    #     else:
    #         assert False, '>> {} : Inference Engine Not Set'.format(sys._getframe().f_code.co_name)
    #         return '{{\"{}\":\"Inference Engine Not Set\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name)

#
# Return hardware to run inference on
#
    def get_target_device(self):

        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.inference_engine:
            return self.inference_engine.get_target_device()
        else:
            assert False, '>> {} : Inference Engine Not Set'.format(sys._getframe().f_code.co_name)
            return '{{\"{}\":\"Inference Engine Not Set\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name)

#
# Set Inference Precision
#
    # def set_precision(self, msg):
    #     if self.verbose:
    #         logging.info('>> {0}:{1}() {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, msg))

    #     if self.inference_engine:

    #         self.inference_engine.set_precision(msg)

    #         if self.current_model_data:
    #             # create a task to download model from model zoo
    #             self.set_video_processor_state(VideoProcessorState.Pause
    #             self.send_message('{{\"set_ai_model\":\"Loading {}\"}}'.format(self.current_model_data.modelName))
    #             task = self.ioLoop.run_in_executor(None, self.inference_engine.load_model, self.current_model_data)
    #             task.add_done_callback(self.model_download_callback)

    #         return self.get_precision()
    #     else:
    #         assert False, '>> {} : Inference Engine Not Set'.format(sys._getframe().f_code.co_name)
    #         return '{{\"{}\":\"Inference Engine Not Set\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name)

#
# Get Inference Precision
#
    def get_precision(self):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.inference_engine:
            return self.inference_engine.get_precision()
        else:
            assert False, '>> {} : Inference Engine Not Set'.format(sys._getframe().f_code.co_name)
            return '{{\"{}\":\"Inference Engine Not Set\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name)

#
# Set Confidence Level threshold
#
    def set_confidence_level(self, msg):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        jsonData = json.loads(msg)
        confidenceLevel = int(jsonData["set_confidence_level"].replace('%',''))

        if self.inference_engine:
            return self.inference_engine.set_confidence_level(confidenceLevel)
        else:
            assert False, '>> {} : Inference Engine Not Set'.format(sys._getframe().f_code.co_name)
            return '{{\"{}\":\"Inference Engine Not Set\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name)

#
# Return Confidence Level threshold
#
    def get_confidence_level(self):
        if self._debug:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.inference_engine:
            return self.inference_engine.get_confidence_level()
        else:
            assert False, '>> {} : Inference Engine Not Set'.format(sys._getframe().f_code.co_name)
            return '{{\"{}\":\"Inference Engine Not Set\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name)

#
# Set Inference State
#
    def set_inference_state(self, msg):
        if self.verbose:
            logging.info('>> {0}:{1}() {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, msg))

        jsonData = json.loads(msg)
        inferenceState = jsonData["set_inference_state"]

        if self.current_model_data:
            #make sure model is loaded
            if not self.current_model_data.isFlagSet(Model_Flag.Loaded):
                return '{{\"{}\":\"{} is not loaded\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name, self.current_model_data.modelName)
            else:
                self.runInference = int(inferenceState)
                return self.get_inference_state()
        else:
            return '{{\"{}\":\"Model Data Not Set\", \"isFailure\":1}}'.format(sys._getframe().f_code.co_name)

#
# Get Current Inference State
#

    def get_inference_state(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return '{{\"{}\":\"{}\"}}'.format(sys._getframe().f_code.co_name, self.runInference)

    async def process_video_frame_async(self, executor):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        try:
            loop = asyncio.get_event_loop()
            task = await loop.run_in_executor(executor, self.process_video_frame)
            return task

        except CancelledError:
            logging.info('-- {0}() - Cancelled'.format(sys._getframe().f_code.co_name))
            self.set_video_processor_state(VideoProcessorState.Stop)
            return 0

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))
            return 1

    #
    # Saves frame data to a file
    #
    def save_image(self):
        cv2.imwrite("./frame.png", self.frame_org)

    #
    # Process Video Frame
    #
    def process_video_frame(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        textX, textY = cv2.getTextSize("FPS", cv2.FONT_HERSHEY_DUPLEX, self._fontScale, 1)[0]
        textX = int(textX * self._fontScale * 1.1)
        textY = int(textY * self._fontScale * 1.1)

        frame = np.array([])

        self.fps.reset(self.videoData.get_video_fps())

        while True:
            try:
                if self._state == VideoProcessorState.Stop:
                    logging.info('>> {0}:{1}() : Stop Video Processor'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
                    break

                if self._state == VideoProcessorState.Pause:
                    if self._debug:
                        logging.info('>> {0}:{1}() : Pause Video Processor'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
                    time.sleep(0.5)
                    continue

                if self.videoData is None:
                    logging.info('>> {0}:{1}() : No Video Data'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
                    time.sleep(0.5)
                    continue

                grabbed, frame = self.videoData.read_frame_queue()

                if self._debug:
                    logging.info("Grabbed {} frame size {}".format(grabbed, frame.size))

                # if (grabbed == False or frame.size == 0):
                if (grabbed == False):
                    time.sleep(1/30)
                    continue
                else:
                    self.frame_org = np.copy(frame)

                if self.runInference == 1:
                    # Run Inference
                    self.inference_engine.inference(frame)

                if self._annotate:
                    fps_annotation = 'FPS : {}'.format(self.currentFps)
                    cv2.putText( frame, fps_annotation, (10, textY + 10), cv2.FONT_HERSHEY_SIMPLEX, self._fontScale, (0,0,255), 2)

                self.set_display_frame(frame)
                self.currentFps = self.fps.fps(self._playback_sync)

            except Exception as ex:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, exc_obj, exc_tb)
                logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))

        if self.verbose:
            logging.info('<< {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

