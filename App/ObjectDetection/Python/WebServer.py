import sys
import logging
import traceback
import os
import json
import asyncio
from tornado import websocket, web, ioloop, platform
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from tornado.ioloop import IOLoop
import base64

class WebServer(object):

    #
    # To run on port 80, run following command to map port 8080 to 80
    # sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
    #
    def __init__(self,
                videoProcessor = None,
                port = 8080,
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
        self.ioloop = None

    def start_web_server(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        try: 
            assert IOLoop.current(False) is None, "invalid current thread's ioloop object."

            self.ioloop = asyncio.get_event_loop()
            asyncio.set_event_loop_policy(platform.asyncio.AnyThreadEventLoopPolicy())
            webContent = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'www')

            self.tornadoApp = web.Application([
                (r"/stream", ImageStreamHandler, {'videoProcessor': self.videoProcessor}),
                (r"/(.*)", web.StaticFileHandler, {'path': webContent, 'default_filename': 'index.html'})
            ])
            self.tornadoApp.listen(self.port)

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))

        if self.verbose:
            logging.info('<< {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))


    def stop_web_server(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        try:
            self.ioloop.close(all_fds=True)
            self.ioloop.stop()
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))

class ImageStreamHandler(websocket.WebSocketHandler):

    clients = []
    debug = False

    def initialize(self, 
                   videoProcessor):

        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        loop = asyncio.get_event_loop()
        self.debug = ImageStreamHandler.debug
        self.videoProcessor = videoProcessor
        self.eventloop = IOLoop.current()
        videoProcessor.imageStreamHandler = self

#
# Client connection opened
# Add to clients list so we can broadcast messages
#
    def open(self):
        logging.info('>> {0}:{1}() : Client IP {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, self.request.remote_ip))
        ImageStreamHandler.clients.append(self)

#
# Client connection closed
# Remove from clients list
#
    def on_close(self):
        logging.info('>> {0}:{1}() : Client IP {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, self.request.remote_ip))
        ImageStreamHandler.clients.remove(self)

#
# Clients sent message
#
    async def on_message(self, msg):

        try:
            if self.debug:
                if msg != 'nextFrame':
                    logging.info('>> {0}:{1}() : Client IP {2} Msg {3}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, self.request.remote_ip, msg))

            if msg == 'nextFrame':
                #
                # Return a frame to display
                #
                self.send_Display_Frame()

            elif msg == 'get_inference_engine_info': 
                #
                # Return path to video source
                #
                self.write_message(self.videoProcessor.get_inference_engine_info())

            elif msg == 'get_model_list':
                #
                # Return list of models
                #
                self.write_message(self.videoProcessor.get_model_list())

            elif msg == 'get_video_resolution':
                #
                # Return current video resolution
                #
                self.write_message(self.videoProcessor.get_video_resolution())

            elif msg == 'get_video_path':
                #
                # Return path to video source
                #
                self.write_message(self.videoProcessor.get_video_path())

            elif msg == 'get_device_params':
                self.write_message(self.videoProcessor.get_device_params())


            elif 'get_target_device' in msg:
                #
                # Return current device inference is running on
                #
                self.write_message(self.videoProcessor.get_target_device())

            elif 'get_precision' in msg:
                #
                # Return current precision (FP16, FP32)
                #
                self.write_message(self.videoProcessor.get_precision())

            elif 'get_confidence_level' in msg:
                #
                # Return confidence level
                #
                self.write_message(self.videoProcessor.get_confidence_level())                

            elif 'set_inference_state' in msg:
                #
                # Turn inference On/Off
                #
                self.write_message(self.videoProcessor.set_inference_state(msg))

            elif 'get_inference_state' in msg:
                #
                # Turn inference On/Off
                #
                self.write_message(self.videoProcessor.get_inference_state())

            else:
                json_data = json.loads(msg)

                if json_data.get('playback_mode'):
                    #
                    # Set video resolution
                    #
                    self.write_message(self.videoProcessor.playback_mode(msg))

                elif json_data.get('set_video_playback'):
                    #
                    # Set video playback (pause or play)
                    #
                    self.write_message(self.videoProcessor.set_video_playback(msg))

                elif json_data.get('set_video_path'):
                    #
                    # Set video resolution
                    #
                    loop = asyncio.get_event_loop()
                    self.write_message(self.videoProcessor.set_video_path(msg, loop))
                    self.write_message(self.videoProcessor.get_video_resolution())
                    self.write_message('{\"frame_ready\":1}')
                    # self.send_Display_Frame()

                elif json_data.get('set_video_resolution'):
                    #
                    # Set video resolution
                    #
                    self.write_message(self.videoProcessor.set_video_resolution(msg))

                elif json_data.get('set_ai_model'):
                    #
                    # Set AI Model to use.  This will start download, convert, then load model
                    #
                    loop = asyncio.get_event_loop()
                    load_model_task = loop.create_task(self.videoProcessor.set_ai_model(loop, msg))
                    await load_model_task

                elif json_data.get('set_target_device'):
                    #
                    # Set Device to run AI on
                    # CPU, GPU, MYRIAD
                    self.write_message(self.videoProcessor.set_device_params(msg, True))

                elif json_data.get('set_confidence_level'):
                    #
                    # Set confidence level threshold
                    #
                    self.write_message(self.videoProcessor.set_confidence_level(msg))

                # elif json_data.get('set_target_device'):
                #     #
                #     # Set target device to run inference on
                #     #
                #     self.write_message(self.videoProcessor.set_target_device(msg))

                # elif json_data.get('set_precision'):
                #     #
                #     # Set precision (FP16, FP32)
                #     #
                #     self.write_message(self.videoProcessor.set_precision(msg))
                else:
                    logging.warn('Unknown Message {}'.format(msg))

        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))#

# Pick up a frame data from Video Processor Class and send to client
#
    def send_Display_Frame(self):
        try:
            frame, fps = self.videoProcessor.get_display_frame()
            if frame != None:
                encoded = base64.b64encode(frame)
                self.write_message('{{\"Image\":\"{0}\", \"FPS\":\"{1:5.1f}\"}}'.format(encoded.decode(), fps), binary=False)
            else:
                logging.warn('<< {0}:{1}() : Empty Frame'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_obj, exc_tb)
            logging.error('!! {0}:{1}() : Exception {2}'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))

#
# Class method to broadcast message
#
    @classmethod
    def broadcast_message(cls, msg):
        if ImageStreamHandler.debug:
            logging.info('>> {} : {}'.format(sys._getframe().f_code.co_name, msg[0:200]))

        for client in ImageStreamHandler.clients:
            if client.ws_connection.stream.socket:
                client.write_message(msg)
            else:
                ImageStreamHandler.clients.remove(client)


#
# Class method to broadcast message
#
    @classmethod
    def broadcast_frame(cls, frame):
        if ImageStreamHandler.debug:
            logging.info('>> {}()'.format(sys._getframe().f_code.co_name))

        if not frame == None:
            encoded = base64.b64encode(frame)
            for client in ImageStreamHandler.clients:
                if client.ws_connection.stream.socket:
                    client.write_message('{{\"Image\":\"{0}\"}}'.format(encoded.decode()), binary=False)
                else:
                    ImageStreamHandler.clients.remove(client)
        else:
            logging.warn('<< {0}() : Empty Frame'.format(sys._getframe().f_code.co_name))

