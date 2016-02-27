# -*- coding: utf-8 -*-

import gi
gi.require_version("GUPnP", "1.0")
from gi.repository import GLib, GUPnP
import urllib.request
import urllib.parse
from xml.etree.ElementTree import XML, XMLParser
from xmlutils import StripNamespace

from cameraremoteapi import CameraRemoteApi
from utils import debug_trace

class CameraRemoteControl(object):

    def __init__(self, friendly_name, callback):
        self.__friendly_name = friendly_name
        self.__device_available_callback = callback

        ctx = GUPnP.Context.new(None, None, 0)
        # caution : keep cp as an attribute !
        self.cp = GUPnP.ControlPoint.new(ctx, "upnp:rootdevice")
        self.cp.set_active(True)
        self.cp.connect("device-proxy-available", self.__device_available)
        self.cp.connect("service-proxy-available", self.__service_available)

    def __service_available(self, cp, proxy):
        # not called !
        pass

    def __device_available(self, cp, proxy):
        proxy_friendly_name = proxy.get_friendly_name()
        # print("Found " + proxy_friendly_name)
        if proxy_friendly_name.startswith(self.__friendly_name):
            service = proxy.get_service("urn:schemas-sony-com:service:ScalarWebAPI:1")
            if service is not None:

                #browse the xml location file and search for the camera service
                #and set the action list uri
                location = proxy.get_location()
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
                        self.__device_available_callback(proxy_friendly_name, endpoint_url)
                        break
