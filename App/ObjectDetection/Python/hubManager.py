import sys
import logging
import json
import uuid

#https://docs.python.org/3/library/concurrent.futures.html#exception-classes
from concurrent.futures import CancelledError
from azure.iot.device import MethodResponse
from azure.iot.device import Message
from azure.iot.device.aio import IoTHubDeviceClient

class HubManager:
    def __init__(self,
                 connectionString):

        logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))
        self.verbose = True
        self.listeners = None
        self.twin = None

        items = connectionString.split(';')

        for item in items:
            values = item.split('=')
            if 'DeviceId' in values[0]:
                self.deviceId = values[1]
                break

        self.deviceClient = IoTHubDeviceClient.create_from_connection_string(connectionString)

    async def __aenter__(self):

        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        await self.deviceClient.connect()

        if self.deviceClient.connected:
            self.twin = await self.get_twin()

        return self

    async def __aexit__(self, exception_type, exception_value, traceback):

        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        if self.deviceClient.connected:
            await self.deviceClient.disconnect()

        if self.verbose:
            logging.info('<< {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

    def process_twin(self, payload):
        if self.verbose:
            logging.info('-- {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

#
# Listens for Desired Twin Updates
#
    async def twin_patch_listener(self):

        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        try:
            while True:
                # Wait for Desired Twin Update
                patch = await self.deviceClient.receive_twin_desired_properties_patch()  # blocking call
                logging.info('Twin Patch Data : {}'.format(patch))

        except CancelledError:
            logging.info('-- {0}:{1}() - Cancelled'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        except Exception as ex:
            logging.info('<< {0}:{1}() ****  Exception {2} ****'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))

        finally:
            if self.verbose:
                logging.info('<< {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return 0

#
# Listens for C2D messages
#
    async def message_listener(self):

        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        try:
            while True:
                # Wait for C2D Message
                message = await self.deviceClient.receive_message()
                logging.info('C2D Message  : {}'.format(message.data))
                logging.info('    Property : {}'.format(message.custom_properties))

        except CancelledError:
            logging.info('-- {0}:{1}() - Cancelled'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        except Exception as ex:
            logging.info('<< {0}:{1}() ****  Exception {2} ****'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))

        finally:
            if self.verbose:
                logging.info('<< {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return 0

#
# Listens for Direct Method
#
    async def generic_method_listener(self):

        if self.verbose:
            logging.info('>> {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        try:
            while True:
                # Wait for Direct Method
                method_request = await self.deviceClient.receive_method_request()
                logging.info('Direct Method : {}'.format(method_request.name))
                logging.info('           id : {}'.format(method_request.request_id))
                logging.info('      payload : {}'.format(method_request.payload))

                # Send Response
                payload = {"result": True, "data": "success"}
                status = 200

                method_response = MethodResponse.create_from_method_request(
                    method_request, status, payload
                )
                await self.deviceClient.send_method_response(method_response)

        except CancelledError:
            logging.info('-- {0}:{1}() - Cancelled'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        except Exception as ex:
            logging.info('<< {0}:{1}() ****  Exception {2} ****'.format(self.__class__.__name__, sys._getframe().f_code.co_name, ex))

        finally:
            if self.verbose:
                logging.info('<< {0}:{1}()'.format(self.__class__.__name__, sys._getframe().f_code.co_name))

        return 0

#
# Retrieve Device/Module Twin
#
    async def get_twin(self):
        # get the twin
        twinData = await self.deviceClient.get_twin()
        logging.info("Twin Data : {}".format(twinData))
        return twinData

#
# A wrapper to send D2C message
#
    async def send_Message(self, message, messageType="Telemetry"):
        msg = Message(json.dumps(message))
        msg.message_id = uuid.uuid4()
        msg.custom_properties["MessageType"] = messageType

        logging.info("Send Message : {}".format(msg.data))
        await self.deviceClient.send_message(msg)

