import sys
import logging
import cv2

class VideoCapture(object):

    def __init__(self):

        self.verbose = True

        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        logging.info('===============================================================')
        logging.info('Initializing Video Capture with the following parameters:')
        logging.info('   - OpenCV Version     : {}'.format(cv2.__version__))
        logging.info('===============================================================')

        self._debug = False

    async def __aenter__(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

    async def __aexit__(self):
        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
