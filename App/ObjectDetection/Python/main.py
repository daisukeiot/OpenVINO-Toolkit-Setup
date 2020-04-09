import sys
import asyncio
from concurrent.futures import CancelledError
import logging
from VideoProcess import VideoProcessor
from WebServer import WebServer
from concurrent.futures import ThreadPoolExecutor
import threading
import atexit

logging.basicConfig(format='[%(thread)-5d] %(asctime)s - %(message)s', level=logging.INFO)
logging.getLogger("asyncio").setLevel(logging.INFO)

async def main():
    logging.info('{0}() : Python {1}'.format(sys._getframe().f_code.co_name, sys.version_info))

    tasks = []

    # try:
    #
    # Default to USB Webcam
    #
    async with VideoProcessor(devicePath = '/dev/video0') as videoProcessor:

        loop = asyncio.get_event_loop()

        #
        # Initialize Tornado Web Server
        #
        webServer = WebServer(videoProcessor = videoProcessor, port = 80)

        if (sys.version_info >= (3, 7)):
            loop = asyncio.get_running_loop()
            loop.set_debug(False)
        else:
            loop = asyncio.get_event_loop()
            loop.set_debug(False)

        #
        # Create a Thread Pool Executor to run Video Stream and Video Processor
        #
        videoExecutor = ThreadPoolExecutor(max_workers=3, thread_name_prefix='videoThread')

        #
        # Start Capturing from Video
        #
        streamLoop = asyncio.new_event_loop()
        videoStreamTask = streamLoop.run_in_executor(videoExecutor, videoProcessor.videoStream.capture_video_frame)
        tasks.append(videoStreamTask)
        #
        # Start Processing video frames
        #
        videoLoop = asyncio.new_event_loop()
        videoProcessTask = videoLoop.run_in_executor(videoExecutor, videoProcessor.process_video_frame)
        tasks.append(videoProcessTask)
        #
        # Start Tornado Web Server
        #
        webServer.startWebServer()

        #
        # keyboard input
        #
        inputTask = loop.run_in_executor(None, stdin_listener)
        await inputTask

        await asyncio.wait(tasks)

    # except CancelledError:
    #     logging.info('-- {0}() - Cancelled'.format(sys._getframe().f_code.co_name))

    # except Exception as ex:
    #     logging.info('<< {0}() ****  Exception {1} ****'.format(sys._getframe().f_code.co_name, ex))

def stdin_listener():
    while True:
        selection = input("Press Q to quit\n")
        if selection == "Q" or selection == "q":
            print("Quitting...")
            break

if __name__ == "__main__":

    #
    # get_running_loop was added to v3.7
    #
    if (sys.version_info >= (3, 7)):
        asyncio.run(main())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()