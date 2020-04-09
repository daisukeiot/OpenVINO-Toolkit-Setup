import sys
import logging
import os
import asyncio
from tornado import websocket, web, ioloop, platform
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
import base64
import threading

class WebServer(object):

    def __init__(self,
                videoProcessor = None,
                port = 80,
                verbose = True):

        self.verbose = verbose

        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        logging.info('===============================================================')
        logging.info('Initializing Tornado Web Server with the following parameters:')
        logging.info('   - Port               : {}'.format(port))
        logging.info('===============================================================')

        self.videoProcessor = videoProcessor
        self.port = port
        self.tornadoApp = None

    def startWebServer(self): 
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
            logging.info('Thread {}'.format(threading.current_thread()))

        asyncio.set_event_loop_policy(platform.asyncio.AnyThreadEventLoopPolicy())
        webContent = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'www')

        self.tornadoApp = web.Application([
            (r"/stream", ImageStreamHandler, {'videoProcessor': self.videoProcessor}),
            (r"/(.*)", web.StaticFileHandler, {'path': webContent, 'default_filename': 'index.html'})
        ])
        self.tornadoApp.listen(self.port)

        if self.verbose:
            logging.info('<< {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

class ImageStreamHandler(websocket.WebSocketHandler):

    def initialize(self, videoProcessor):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        self.debug = True
        self.clients = []
        self.videoProcessor = videoProcessor
        videoProcessor.imageStreamHandler = self

    def open(self):
        if self.debug:
            logging.info('>> {0}:{1}() : Client IP {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, self.request.remote_ip))
            logging.info('open {}'.format(threading.current_thread()))

        self.clients.append(self)

    def on_close(self):
        if self.debug:
            logging.info('>> {0}:{1}() : Client IP {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, self.request.remote_ip))
            logging.info('open {}'.format(threading.current_thread()))

        self.clients.remove(self)

    def on_message(self, msg):
        # if self.debug:
        #     logging.info('>> {0}:{1}() : Client IP {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, self.request.remote_ip))

        if msg == 'nextFrame':
            #
            # Return a frame to display
            #
            self.send_Display_Frame()

        elif msg == 'getVideoPath':
            #
            # Return path to video source
            #
            self.message_writer('{{\"DevicePath\":\"{0}\"}}'.format(self.videoProcessor.devicePath))

        elif 'VideoRes' in msg:
            self.videoProcessor.set_video_resolution(msg)

        else:
            logging.warn('Unknown Message {}'.format(msg))

    def send_Display_Frame(self):
        try:
            frame, fps = self.videoProcessor.get_display_frame()
            if not frame == None:
                encoded = base64.b64encode(frame)
                self.write_message('{{\"Image\":\"{0}\", \"FPS\":{1:.2f}}}'.format(encoded.decode(), fps), binary=False)
            else:
                logging.warn('<< {0}:{1}() : Empty Frame'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        except Exception as ex:
            logging.error('<< {0}:{1}() : Exception : {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))

    def message_writer(self, json_data):
        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        for client in self.clients:
            if client.ws_connection.stream.socket:
                client.write_message(json_data)
            else:
                self.clients.remove(client)