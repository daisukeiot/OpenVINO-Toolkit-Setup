import sys
import logging
import time
import cv2
from VideoStream import VideoStream, VideoStreamState
import asyncio
import numpy as np
from FPS import FPS
from enum import Enum
import threading
import json

class VideoProcessorState(Enum):
    Unknown = 0
    Initialized = 1
    Stop = 2
    Pause = 3

class VideoProcessor(object):

    #
    # Initialization of Video Processor Class
    # Reads video frame from Video Stream class and process (AI Inference etc)
    # Set frame data to displayFrame for visualization
    #
    def __init__(self,
                 devicePath = '/dev/video0',
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
        logging.info('   - Device Path        : {}'.format(devicePath))
        logging.info('   - Frame Sizeh        : {}x{}'.format(videoW, videoH))
        logging.info('===============================================================')

        # Video source
        self.devicePath = devicePath
        self._videoW = videoW
        self._videoH = videoH

        self.videoStream = None

        self.displayFrame = np.array([])

        # for Frame Rate measurement
        self.fps = FPS()
        self.currentFps = 30

        # For display
        self._fontScale = float(fontScale)
        self._annotate = False

        # Track states of this object
        self._state = VideoProcessorState.Unknown

        # To send message to clients (Browser)
        self.imageStreamHandler = None

    #
    # Sets up Video Processor Class
    # Creates Video Stream Class for video capture
    #
    async def __aenter__(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.videoStream = VideoStream(videoProcessor = self, verbose = self.verbose)
        if self.videoStream.init_video_stream(self._videoW, self._videoH):

            logging.info('Opened Capture Device {0}'.format(self.devicePath))

            self._state = VideoProcessorState.Initialized
        else:
            logging.info('Failed to open Capture Device {0}'.format(self.devicePath))

        return self

    #
    # Clean up Video Processor Class
    #
    async def __aexit__(self, exception_type, exception_value, traceback):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self._state = VideoProcessorState.Stop
        self.videoStream.set_video_stream_state(VideoStreamState.Stop)

    #
    # Initializes Video Source
    #
    def _init_video_soruce(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        raise NotImplementedError

    #
    # Resturns current video frame for display
    # Converts to byte data
    #
    def get_display_frame(self):

        if self.displayFrame.size > 0:
            ret, buffer = cv2.imencode( '.jpg', self.displayFrame )

            if ret and buffer.size > 0:
                return buffer.tobytes(), self.currentFps
            else:
                logging.info('>> Display Frame Empty *************** ')

        return None, self.currentFps

    #
    # Set Video Resolution
    #
    def set_video_resolution(self, msg):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        jsonData = json.loads(msg)
        resolution = jsonData["VideoRes"]

        logging.info('>> New Resolution {}'.format(resolution))

        # https://webcamtests.com/resolution

        if resolution == "vga":
            w = 640
            h = 480
        elif resolution == "xga":
            w = 1024
            h = 726
        elif resolution == "hd":
            w = 1280
            h = 720
        elif resolution == "wxga":
            w = 1280
            h = 800
        elif resolution == "fhd":
            w = 1920
            h = 1080
        else:
            w = 0
            h = 0

        if w != 0 and h != 0:
            self._state = VideoProcessorState.Pause
            self.videoStream.set_video_stream_state(VideoStreamState.Pause)
            self.videoStream.set_video_stream_property(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.videoStream.set_video_stream_property(cv2.CAP_PROP_FRAME_HEIGHT, h)

            w = self.videoStream.get_video_stream_property(cv2.CAP_PROP_FRAME_WIDTH)
            h = self.videoStream.get_video_stream_property(cv2.CAP_PROP_FRAME_HEIGHT)

            logging.info('>> {0}:{1}() : New Resolution {2}x{3}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, w, h))

            if w == 640 and h == 480:
                res = "vga"
            elif w == 1024 and h == 768:
                res = "xga"
            elif w == 1280 and h == 720:
                res = "hd"
            elif w == 1280 and h == 800:
                res = "wxga"
            elif w == 1920 and h == 1080:
                res = "fhd"
            
            if self.imageStreamHandler:
                self.imageStreamHandler.message_writer('{{\"VideoRes\":\"{0}\"}}'.format(res))

            self.videoStream.set_video_stream_state(VideoStreamState.Initialized)
            self._state = VideoProcessorState.Initialized

    #
    # Set Video Stream Property
    #
    def set_video_stream_property(self, cv2_prop, value):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        self.videoStream.set_video_stream_property(cv2_prop, value)

    #
    # Sets current video frame for display
    #
    def set_display_frame(self, frame):
        self.displayFrame = frame

    #
    # Process Video Frame
    #
    def process_video_frame(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
            logging.info('process_video_frame {}'.format(threading.current_thread()))

        self.fps.start()
        self.fps.reset()

        textX, textY = cv2.getTextSize("FPS", cv2.FONT_HERSHEY_DUPLEX, self._fontScale, 1)[0]
        textX = int(textX * self._fontScale * 1.1)
        textY = int(textY * self._fontScale * 1.1)

        frame = np.array([])

        while True:

            if self._state == VideoProcessorState.Stop:
                break

            if self._state == VideoProcessorState.Pause:
                time.sleep(0.5)
                continue

            grabbed, frame = self.videoStream.read_frame_queue()

            if self._debug:
                logging.info("Grabbed {} frame size {}".format(grabbed, frame.size))

            if (grabbed == False or frame.size == 0):
                time.sleep(0.01)
                continue
            else:
                pass

            self.currentFps = self.fps.fps()

            if self._annotate:
                fps_annotation = 'FPS : {}'.format(self.currentFPS)
                cv2.putText( frame, fps_annotation, (10, textY + 10), cv2.FONT_HERSHEY_SIMPLEX, self._fontScale, (0,0,255), 2)

            self.set_display_frame(frame)

        if self.verbose:
            logging.info('<< {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

