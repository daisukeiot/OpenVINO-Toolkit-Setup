import sys
import asyncio
import logging
import traceback
from VideoProcessor import VideoProcessor
from WebServer import WebServer
from concurrent.futures import ThreadPoolExecutor, CancelledError
# import threading
import signal

# logging.basicConfig(format='[%(thread)-5d] %(asctime)s - %(message)s', level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logging.getLogger("asyncio").setLevel(logging.INFO)

async def shutdown(loop, executor, signal=None):

    if signal:
        logging.info(f"Received exit signal {signal.name}...")

    if (sys.version_info >= (3, 7)):
        current_task = asyncio.current_task()
        all_tasks = asyncio.all_tasks()
    else:
        current_task = asyncio.Task.current_task()
        all_tasks = asyncio.Task.all_tasks()

    tasks = [t for t in all_tasks if t is not current_task]

    logging.info(f"Cancelling {len(tasks)} outstanding tasks")

    [task.cancel() for task in tasks]

    logging.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)

    logging.info("Shutting down executor")
    executor.shutdown(wait=False)

    logging.info(f"Releasing {len(executor._threads)} threads from executor")
    for thread in executor._threads:
        try:
            thread._tstate_lock.release()
        except Exception:
            pass

    loop.stop()

async def main():
    logging.info('{0}() : Python {1}'.format(sys._getframe().f_code.co_name, sys.version_info))
    tasks = []
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='videoThread')

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: loop.create_task(shutdown(loop, executor, signal=s)))

    try:
        #
        # Default to USB Webcam
        #
        # with VideoProcessor(videoPath = '/home/wcbiot/OpenVINO-Toolkit-Setup/App/ObjectDetection/Python/youtube.mp4') as videoProcessor:
        with VideoProcessor(videoPath = '/dev/video0') as videoProcessor:
        # async with VideoProcessor(devicePath = '/dev/video0') as videoProcessor:

            #
            # Initialize Tornado Web Server
            #
            webServer = WebServer(videoProcessor = videoProcessor, port = 8080)

            if (sys.version_info >= (3, 7)):
                loop = asyncio.get_running_loop()
                loop.set_debug(False)
            else:
                loop = asyncio.get_event_loop()
                loop.set_debug(False)

            #
            # Start Capturing from Video
            #
            videoStreamTask = loop.create_task(videoProcessor.videoData.capture_video_frame_async(executor))
            tasks.append(videoStreamTask)

            #
            # Start Processing video frames
            #
            videoProcessTask = loop.create_task(videoProcessor.process_video_frame_async(executor))
            tasks.append(videoProcessTask)

            #
            # Start Tornado Web Server
            #
            webServer.start_web_server()
            
            #
            # keyboard input
            #
            inputTask = loop.run_in_executor(executor, stdin_listener)
            # tasks.append(inputTask)
            await inputTask


            for task in tasks:
                # print("Task {}", task)
                task.cancel()

            done, futures = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            
            # webServer.stop_web_server()

    except CancelledError:
        logging.info('-- {0}() - Cancelled'.format(sys._getframe().f_code.co_name))

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_obj, exc_tb)
        logging.error('!! {0}() : Exception {1}'.format(sys._getframe().f_code.co_name, ex))

    finally:
        logging.info('-- {0}() - Finally'.format(sys._getframe().f_code.co_name))
        for task in asyncio.Task.all_tasks():
            logging.info("Task {}".format(task))

        # done, futures = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        # print("done {}", done)
        # print("futures {}", futures)
        # await asyncio.gather(*tasks, return_exceptions=True)
        await loop.shutdown_asyncgens()
        # loop.run_until_complete(loop.shutdown_asyncgens())
        # loop.stop()
        # loop.close()

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
