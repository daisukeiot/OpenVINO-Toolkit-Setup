import sys
import logging
import cv2
import asyncio
from queue import Queue
import threading
from threading import Thread
import time
import numpy as np
from enum import Enum

class VideoStreamState(Enum):
    Unknown = 0
    Initialized = 1
    Stop = 2
    VideoSourceErr = 3
    Pause = 4

class VideoStream(object):

    #
    # Initialization of Video Stream Class
    # Reads video frame from the specified video source
    # Supports :
    # USB Camera : /dev/videoX
    #
    def __init__(self, 
                 videoProcessor,
                 verbose = True):

        self.verbose = verbose
        self._debug = False

        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.cv2_Capture = None
        self.videoProcessor = videoProcessor
        self.frameQueue = Queue(maxsize=5)
        self._state = VideoStreamState.Unknown

    #
    # Initializes video stream
    # Opens CV2 Video Capture class
    # Sets camera resolution
    #
    def init_video_stream(self, videoW = 0, videoH = 0):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        ret = False

        if (self.videoProcessor.devicePath != None):
            self.cv2_Capture = cv2.VideoCapture(self.videoProcessor.devicePath)

            if (self.cv2_Capture.isOpened()):
                w = self.cv2_Capture.get(cv2.CAP_PROP_FRAME_WIDTH)
                h = self.cv2_Capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
                logging.info('>> Resolution {0}x{1}'.format(w, h))
                
                if (videoW != 0):
                    self.cv2_Capture.set(cv2.CAP_PROP_FRAME_WIDTH, videoW)

                if (videoH != 0):
                    self.cv2_Capture.set(cv2.CAP_PROP_FRAME_HEIGHT, videoH)

                logging.info('>> Resolution {0}x{1}'.format(videoW, videoH))

                w = self.cv2_Capture.get(cv2.CAP_PROP_FRAME_WIDTH)
                h = self.cv2_Capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
                logging.info('>> Resolution {0}x{1}'.format(w, h))

                self.cv2_Capture.set(cv2.CAP_PROP_FPS, 30)

                time.sleep(1)

                # read 1 frame to be sure

                ret, frame = self.cv2_Capture.read()

                if ret or frame.size == 0:
                    self._state = VideoStreamState.Initialized
                else:
                    logging.error('Failed to grap frame from {0}'.format(self.videoProcessor.devicePath))
            else:
                self._state = VideoStreamState.VideoSourceErr
                logging.error('Failed to open capture device {0}'.format(self.videoProcessor.devicePath))
            
        return ret

    #
    # Set Video Stream Property
    #
    def set_video_stream_property(self, cv2_prop, value):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        
        return self.cv2_Capture.set(cv2_prop, value)

    #
    # Get Video Stream Property
    #
    def get_video_stream_property(self, cv2_prop):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        
        return self.cv2_Capture.get(cv2_prop)

    #
    # Set Video Stream State
    #
    def set_video_stream_state(self, state):
        if self.verbose:
            logging.info('>> {0}:{1}() : State {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, state))
        self._state = state

    #
    # Get Video Stream State
    #
    @property
    def get_video_stream_state(self):
        if self.verbose:
            logging.info('>> {0}:{1}() : State {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, self._state))
        return self._state

    #
    # Capture Video Stream
    # Inserts video frame to frameQueue
    #
    def capture_video_frame(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
            logging.info('capture_video_frame {}'.format(threading.current_thread()))

        while True:

            if self._state == VideoStreamState.Stop:
                while not self.frameQueue.empty():
                    self.frameQueue.get()
                break

            if self._state == VideoStreamState.Pause:
                time.sleep(0.3)
                continue

            ret, frame = self.cv2_Capture.read()

            if ret:
                if not self.frameQueue.full():
                    self.frameQueue.put(frame)
                else:
                    self.frameQueue.get()

        if self.verbose:
            logging.info('<< {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

    #
    # Pick up a frame from frameQueue
    # returns Bool, frame (or empty array if the queue is empty)
    #
    def read_frame_queue(self):
        if self.frameQueue.empty():
            return False, np.array([])
        else:
            return True, self.frameQueue.get()