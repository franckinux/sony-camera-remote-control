# import asyncio
import upnpclient
import urllib.request
import urllib.parse
from xml.etree.ElementTree import XML, XMLParser
from xmlutils import StripNamespace

from cameraremoteapi import CameraRemoteApi
# from utils import debug_trace


class CameraRemoteControl(object):

    def __init__(self, friendly_name, callback):
        self.__friendly_name = friendly_name
        self.__device_available_callback = callback

    async def discover(self):
        devices = upnpclient.discover()
        for d in devices:
            await self.__device_available(d)

    async def __device_available(self, device):
        friendly_name = device.friendly_name
        if friendly_name.startswith(self.__friendly_name):
            for s in device.services:
                if s.service_id == "urn:schemas-sony-com:serviceId:ScalarWebAPI":

                    # browse the xml location file and search for the camera service
                    # and set the action list uri
                    location = device.location
                    xd = urllib.request.urlopen(location)
                    s = xd.read()

                    target = StripNamespace()
                    parser = XMLParser(target=target)
                    root = XML(s, parser=parser)

                    sl = root.findall("device/X_ScalarWebAPI_DeviceInfo/X_ScalarWebAPI_ServiceList/X_ScalarWebAPI_Service")
                    for s in sl:
                        service_type = s.find("X_ScalarWebAPI_ServiceType").text
                        if service_type == CameraRemoteApi.SERVICE_NAME:
                            camera_action_list = s.find("X_ScalarWebAPI_ActionList_URL").text
                            if not camera_action_list.endswith('/'):
                                camera_action_list += '/'
                            endpoint_url = urllib.parse.urljoin(camera_action_list, CameraRemoteApi.SERVICE_NAME)
                            await self.__device_available_callback(friendly_name, endpoint_url)
                            break
