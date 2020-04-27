import sys
import logging
import traceback
import cv2
import asyncio
from queue import Queue, Full
import time
import numpy as np
from enum import IntEnum
from pathlib import Path
from concurrent.futures import CancelledError
import json
import youtube_dl


class Video_Device_Type(IntEnum):
    Unknown = 0
    Camera = 1
    Video = 2
    Youtube = 3

class Video_Data_State(IntEnum):
    Unknown = 0
    Error = 1
    Init = 2
    Downloading = 3
    Running = 4

class Video_Stream_State(IntEnum):
    Unknown = 0
    Error = 1
    Stop = 2
    Running = 3
    Pause = 4

class Video_Playback_Mode(IntEnum):
    Sync = 0
    Perf = 1

class Video_Data():

    def __init__(self, videoProcessor, videoPath = ""):
        self.verbose = False
        self._debug = False

        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self.videoPath = ""
        self.videoProcessor = videoProcessor
        self.videoW = 0
        self.videoH = 0
        self._set_video_data_state(Video_Data_State.Unknown)
        self._set_video_type()
        self.frame_count = -1
        self.fps = 30
        self.playback_mode = Video_Playback_Mode.Sync
        self.frame_queue = Queue(maxsize=3)
        self.cv2_cap = None
        self._set_video_stream_state(Video_Stream_State.Unknown)
        self.set_video_path(videoPath)

#
# Set Video Path
# validates and collects parameters such as resolution
#
    def set_video_path(self, videoPath, ioLoop = None):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        # check if this is the same video file
        if self.videoPath == videoPath:
            # if this is a video file set frame to the beginning
            video_type = self._get_video_type()
            if video_type == Video_Device_Type.Video or video_type == Video_Device_Type.Youtube:
                self._set_cv2_prop(cv2.CAP_PROP_POS_FRAMES, 0)

            # make sure video data and stream are running
        else:

            self._set_video_data_state(Video_Data_State.Init)

            self.videoPath = videoPath
            
            self._set_video_type()

            if self._get_video_type() == Video_Device_Type.Youtube:
                # download video
                self.download_video(ioLoop)
            else:
                self._set_video_param(self.videoPath)

        if self.get_video_data_state() == Video_Data_State.Running:
            # start video capture
            self._set_video_stream_state(Video_Stream_State.Running)

        return self.get_video_data_state()

#
# Set up video parameters
# - resolution
# - FPS
#
    def _set_video_param(self, videoPath):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if len(videoPath) > 0:
            logging.info('>> Video : {}'.format(videoPath))
            self.cv2_cap  = cv2.VideoCapture(videoPath)
            if self.cv2_cap.isOpened():
                self.videoW = int(self._get_cv2_prop(cv2.CAP_PROP_FRAME_WIDTH))
                self.videoH = int(self._get_cv2_prop(cv2.CAP_PROP_FRAME_HEIGHT))

                self._set_video_type()

                self.fps = int(self._get_cv2_prop(cv2.CAP_PROP_FPS))

                if self._get_video_type() == Video_Device_Type.Youtube:
                    self.frame_count = int(self._get_cv2_prop(cv2.CAP_PROP_FRAME_COUNT))
                else:
                    self._set_cv2_prop(cv2.CAP_PROP_FPS, self.fps)
                    self.frame_count = 0

                logging.info('Video Device : {}'.format(self.videoPath))
                logging.info('  Resolution : {}x{}'.format(self.videoW, self.videoH))
                logging.info('         FPS : {}'.format(self.fps))
                logging.info(' Frame count : {}'.format(self.frame_count))

                self._set_video_data_state(Video_Data_State.Running)
            else:
                self._set_video_data_state(Video_Data_State.Error)
                logging.error('>> Video Open Failed')
        else:
            self._set_video_data_state(Video_Data_State.Error)
            logging.info('>> Video Empty!!!!')

#
# Check if the path is for Youtube Video
#
    def __IsYoutube(self):
        try:
            if 'www.youtube.com' in self.videoPath.lower() or 'youtu.be' in self.videoPath.lower():
                return True
            else:
                return False
        except ValueError:
            return False

#
# Check if the path is for Webcam or Camera
#
    def __IsCamera(self):
        try:
            if self.videoPath.startWith('/dev'):
                return True
            else:
                return False
        except ValueError:
            return False

#
# Set CV2 property
#
    def _set_cv2_prop(self, cv2_prop, value):
        return self.cv2_cap.set(cv2_prop, value)

#
# Get CV2 property
#
    def _get_cv2_prop(self, cv2_prop):
        return self.cv2_cap.get(cv2_prop)

#
# Set playback mode
#
    def set_playback_mode(self, mode):
        if self.verbose:
            logging.info('>> {0}:{1}() : Mode {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, mode))

        if mode == "0":
            self.playback_mode = Video_Playback_Mode.Sync
        else:
            self.playback_mode = Video_Playback_Mode.Perf
#
# Return playback mode
#
    def get_playback_mode(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return self.playback_mode

#
# Return FPS
#
    def get_video_fps(self):
        if self.verbose:
            logging.info('>> {0}:{1}() : {2} FPS'.format(self.__class__.__name__, sys._getframe().f_code.co_name, self.fps))
        return self.fps
#
# Set Video Type
#
    def _set_video_type(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.__IsYoutube():
            self.videoType = Video_Device_Type.Youtube
        elif self.__IsCamera:
            self.videoType = Video_Device_Type.Camera
        else:
            self.videoType = Video_Device_Type.Unknown

#
# Return Video Type
#
    def _get_video_type(self):
        return self.videoType

#
# Set Video Data State
#
    def _set_video_data_state(self, state):
        if self.verbose:
            logging.info('>> {0}:{1}() : State {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, state))

        self.state = state

#
# Return Video Data State
#
    def get_video_data_state(self):
        return self.state

#
# Start stop video
#
    def set_video_playback(self, isPause):

        if isPause:
            self._set_video_stream_state(Video_Stream_State.Pause)
        else:
            self._set_video_stream_state(Video_Stream_State.Running)

#
# Set Video Stream State
#
    def _set_video_stream_state(self, state):
        if self.verbose:
            logging.info('>> {0}:{1}() : State {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, state))

        self.stream_state = state

#
# Return Video Stream State
#
    def get_video_stream_state(self):
        return self.stream_state

#
# Return Video Type
#
    def get_video_type(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return self.videoType
#
# Download Youtube Video
# Set up task to download
#
    def download_video(self, ioLoop = None):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self._get_video_type() == Video_Device_Type.Youtube:

            self._set_video_data_state(Video_Data_State.Downloading)
            self._set_video_stream_state(Video_Stream_State.Pause)

            if not ioLoop is None:
                task = ioLoop.run_in_executor(None, self._download_video)
                task.add_done_callback(self._download_callback)                
            else:
                logging.info("!! No ioLoop")

#
# Download video
#
    def _download_video(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        p_video_url = Path(self.videoPath)
        p_video = Path(Path('./').resolve() / 'video' / ((p_video_url.name).split('=')[1] + '.mp4'))

        if not p_video.exists():

            self.videoProcessor.set_video_stop()

            ydl_opts = {
                'format':'136',
                'outtmpl': str(p_video)
            }

            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    logging.info('downloading {}....'.format(str(p_video)))
                    ydl.download([self.videoPath])

                return str(p_video)

            except Exception as ex:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, exc_obj, exc_tb)
                logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))
        else:
            return str(p_video)

        return ""
#
# Callback for video download
#
    def _download_callback(self, future):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        video_path = future.result()
        logging.info('Video Download Callback : {}'.format(video_path))

        if len(video_path) > 0:
            p_video = Path(video_path).resolve()

            if p_video.exists():
                self._set_video_param(str(p_video))
                self._set_video_data_state(Video_Data_State.Running)
                self._set_video_stream_state(Video_Stream_State.Running)
                self.videoProcessor.set_video_start()
            else:
                self._set_video_data_state(Video_Data_State.Error)
        else:
            self._set_video_data_state(Video_Data_State.Error)

        self.videoProcessor.send_message(self.get_video_path())
        self.videoProcessor.send_message(self.get_video_resolution())

    def get_video_path(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return '{{\"get_video_path\":\"{0}\", \"video_type\":{1}, \"state\":{2}, \"playback_mode\":\"{3}\"}}'.format(self.videoPath, int(self.videoType), self.state, self.playback_mode)

#
# Set Video Resolution
#
    def set_video_resolution(self, msg):

        jsonData = json.loads(msg)
        resolution = jsonData["set_video_resolution"]

        if self.verbose:
            logging.info('>> {0}:{1}() : New Resolution {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, resolution))

        # https://webcamtests.com/resolution

        if resolution == "vga":
            w = 640
            h = 480
        elif resolution == "xga":
            w = 1024
            h = 768
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

        self.videoW = w
        self.videoH = h

        try:

            if w != 0 and h != 0 and self.get_video_stream_state() != Video_Stream_State.Error :
                # Pause video stream
                self._set_video_stream_state(Video_Stream_State.Pause)
                time.sleep(0.1)
                # set resolution
                self._set_cv2_prop(cv2.CAP_PROP_FRAME_WIDTH, w)
                self._set_cv2_prop(cv2.CAP_PROP_FRAME_HEIGHT, h)
                
                # read one frame
                grabbed, frame = self.cv2_cap.read()

                if grabbed == False:
                    logging.error('>> Capture failed after chaniging resolution')
                    self._set_video_stream_state(Video_Stream_State.Error)
                else:
                    # Restart capture
                    self._set_video_stream_state(Video_Stream_State.Running)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))

        return self.get_video_resolution()

    def get_video_resolution(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        w = self.videoW
        h = self.videoH

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
        else:
            res = "{}x{}".format(w, h)

        return '{{\"get_video_resolution\":\"{0}\", \"resolution\":\"{1}x{2}\"}}'.format(res, w, h)

#
# Allocate a new task in a new thread pool to capture video frame
#
    async def capture_video_frame_async(self, executor):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        try:
            loop = asyncio.get_event_loop()
            task = await loop.run_in_executor(executor, self.capture_video_frame)
            return task

        except CancelledError:
            logging.info('-- {0}() - Cancelled'.format(sys._getframe().f_code.co_name))
            self._set_video_stream_state(Video_Stream_State.Stop)
            return 0

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))
            self._set_video_stream_state(Video_Stream_State.Error)
            return 1

#
# Capture Video Stream
# Inserts video frame to frame_queue
#
    def capture_video_frame(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        self._set_video_stream_state(Video_Stream_State.Running)

        try:
            while True:
                #
                # To do : Add error handling
                #
                if self.get_video_stream_state() == Video_Stream_State.Stop:
                    logging.info('>> Stream Stop')
                    while not self.frame_queue.empty():
                        self.frame_queue.get()
                    break

                if self.get_video_stream_state() == Video_Stream_State.Pause:
                    if self._debug:
                        logging.info('>> Stream Pause')
                    if (self._get_video_type() != Video_Device_Type.Video):
                        while not self.frame_queue.empty():
                            self.frame_queue.get()
                    time.sleep(0.3)
                    continue

                ret, frame = self.cv2_cap.read()

                video_type = self._get_video_type()

                if ret:
                    # can be a blocking call
                    if video_type == Video_Device_Type.Video or video_type == Video_Device_Type.Youtube:
                        self.frame_queue.put(item = frame)
                    else:
                        try:
                            self.frame_queue.put(item = frame, timeout=0.03)
                        except Full:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put_nowait(item = frame)
                        except Exception as ex:
                            pass
                else:
                    if video_type == Video_Device_Type.Video or video_type == Video_Device_Type.Youtube:
                        current_frame = self._get_cv2_prop(cv2.CAP_PROP_POS_FRAMES)
                        if current_frame == self.frame_count:
                            self._set_video_stream_state(Video_Stream_State.Pause)
                            continue

                    logging.error("!!!Capture Failed")

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))

        if self.verbose:
            logging.info('<< {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

#
# Pick up a frame from frame_queue
# returns Bool, frame (or empty array if the queue is empty)
#
    def read_frame_queue(self):
        return True, self.frame_queue.get()

        # if self.frame_queue.empty():
        #     return False, np.array([])
        # else:
        #     return True, self.frame_queue.get()
