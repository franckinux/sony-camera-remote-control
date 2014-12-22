# -*- coding: utf-8 -*-

from urlparse import urljoin
from xml.etree.ElementTree import XML, XMLParser
from xmlutils import StripNamespace

#import pdb; pdb.set_trace()

class ServerDevice(object):

    def __init__(self, s):
        target = StripNamespace()
        parser = XMLParser(target=target)
        root = XML(s, parser=parser)

        self.friendly_name = root.find("device/friendlyName").text
        self.device_type = root.find("device/deviceType").text
        self.model_description = root.find("device/modelDescription").text
        self.model_name = root.find("device/modelName").text
        self.udn = root.find("device/UDN").text

        self.__service_list = {}
        sl = root.findall("device/serviceList/service")
        for s in sl:
            si = {}
            service_id = s.find("serviceId").text
            si["service_type"] = s.find("serviceType").text
            si["xml_file"] = s.find("SCPDURL").text
            si["control_url"] = s.find("controlURL").text
            si["event_sub_url"] = s.find("eventSubURL").text
            if service_id not in self.__service_list:
                self.__service_list[service_id] = si

        self.__webapi_service_list = {}
        if "urn:schemas-sony-com:serviceId:ScalarWebAPI" in self.__service_list:
            sl = root.findall("device/X_ScalarWebAPI_DeviceInfo/X_ScalarWebAPI_ServiceList/X_ScalarWebAPI_Service")
            for s in sl:
                service_type = s.find("X_ScalarWebAPI_ServiceType").text
                si = {}
                action_list = s.find("X_ScalarWebAPI_ActionList_URL").text
                if not action_list.endswith('/'):
                    action_list += '/'
                si["action_list"] = action_list
                si["access_type"] = s.find("X_ScalarWebAPI_AccessType").text
                if service_type not in self.__webapi_service_list:
                    self.__webapi_service_list[service_type] = si

    def get_service(self, service):
        if service in self.__service_list:
            return self.__service_list[service]

    def has_api_service(self, service):
        return service in self.__webapi_service_list

    def get_endpoint_url(self, service):
        if self.has_api_service(service):
            webapi_service = self.__webapi_service_list[service]
            return urljoin(webapi_service["action_list"], service)
        else:
            return ""
