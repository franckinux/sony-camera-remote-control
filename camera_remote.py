#/usr/bin/python2
# -*- coding: utf-8 -*-

from gi.repository import GLib, GUPnP
from cameraremoteapi import CameraRemoteApi
import urllib2
from urlparse import urljoin
from xml.etree.ElementTree import XML, XMLParser
from xmlutils import StripNamespace
#import pdb; pdb.set_trace()

class CameraRemoteControl(object):

    def __init__(self, friendly_name):
        self.friendly_name = friendly_name
        self.camera_remote_api = None

        ctx = GUPnP.Context.new(None, None, 0)
        self.cp = GUPnP.ControlPoint.new(ctx, "upnp:rootdevice")
        self.cp.set_active(True)
        self.cp.connect("device-proxy-available", self.device_available)
        self.cp.connect("service-proxy-available", self.service_available)

    def service_available (self, cp, proxy):
        print "coucou"

    def device_available (self, cp, proxy):
        print ("Found " + proxy.get_friendly_name())
        if proxy.get_friendly_name().startswith(self.friendly_name):
            service = proxy.get_service("urn:schemas-sony-com:service:ScalarWebAPI:1")
            if service is not None:

                #browse the xml location file and search for the camera service
                #and set the action list uri
                location = proxy.get_location()
                xd = urllib2.urlopen(location)
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
                        endpoint_url = urljoin(camera_action_list, CameraRemoteApi.SERVICE_NAME)
                        self.camera_remote_api = CameraRemoteApi(endpoint_url)
                        break

if __name__ == "__main__":
    app = CameraRemoteControl("ILCE")
    try:
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        pass
