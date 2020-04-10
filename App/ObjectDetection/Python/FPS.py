import datetime

#####################################################################################
# Class to measure FPS
#####################################################################################
class FPS:
    def __init__(self):
        self._start = None
        self._now = None
        self._frameCount = 0

    def start(self):
        self._start = datetime.datetime.now()
        return self

    def reset(self):
        self._frameCount = 0
        self._start = datetime.datetime.now()
        return self

    def fps(self):
        self._frameCount += 1
        self._now = datetime.datetime.now()
        return round(self._frameCount / ((self._now - self._start).total_seconds()), 2)