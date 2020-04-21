import time
import logging

#####################################################################################
# Class to measure FPS
#####################################################################################
class FPS:
    def __init__(self):
        self._start = None
        self._start_all = None
        self._frameCount = 0
        self._target = 0

    def start(self):
        self._start = time.time()

    def stop(self):
        now = time.time()
        return round(self._frameCount / (now - self._start_all), 2)

    def reset(self, target = 0):

        logging.info('>> FPS Reset to {} FPS'.format(target))
        if target == 0:
            self._target = 1000/30
        else:
            self._target = 1000 / target
        self._frameCount = 0
        self._start_all = time.time()
        self._start = self._start_all

    def fps(self, sync = False):
        now = time.time()
        delta = (now - self._start) * 1000

        if sync:
            if self._target > delta:
                wait_time = self._target - delta
                time.sleep(wait_time/1000.0)

            now = time.time()
            delta = (now - self._start) * 1000

        self._start = now
        return round((1000.0/delta), 1)