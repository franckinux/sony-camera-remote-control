# -*- coding: utf-8 -*-

from functools import partial
import json
import urllib2

#import pdb; pdb.set_trace()

class SimpleRemoteApi(object):

    __METHODS = {
        #Shoot mode
        "setShootMode": {
            "service": ["camera"],
            "params": ["shootMode"],
            "version": "1.0"
        },
        "getShootMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getSupportedShootMode": {
            "service": ["camera"],
            "params": [],
             "version": "1.0"
        },
        "getAvailableShootMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Still capture
        "actTakePicture": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "awaitTakePicture": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "startContShooting": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "stoptContShooting": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Movie recording
        "startMovieRec": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "stopMovieRec": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Audio recording (N/A)
        #Intervall still recording (N/A)

        #Liveview
        "startLiveview": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "stopLiveview": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Liveview size
        "startLiveviewWithSize": {
            "service": ["camera"],
            "params": ["liveviewSize"],
            "version": "1.0"
        },
        "getLiveviewSize": {
            "service": ["camera"],
            "params": ["liveviewSize"],
            "version": "1.0"
        },
        "getSupportedLiveviewSize": {
            "service": ["camera"],
            "params": ["liveviewSize"],
            "version": "1.0"
        },
        "getAvailableLiveviewSize": {
            "service": ["camera"],
            "params": ["liveviewSize"],
            "version": "1.0"
        },

        #Liveview frame (N/A)

        #Zoom
        "actZoom": {
            "service": ["camera"],
            "params": ["zoomDirection", "zoomMovement"],
            "version": "1.0"
        },

        #Zoom setting (N/A)
        #Half-press shutter (N/A)

        #Touch AF position
        "setTouchAFPosition": {
            "service": ["camera"],
            "params": ["xAxisPosition", "yAxisPosition"],
            "version": "1.0"
        },
        "getTouchAFPosition": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "cancelTouchAFPosition": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Tracking focus (N/A)
        #Continuous shooting mode (N/A)
        #Continuous shooting speed (N/A)

        #Self-timer
        "setSelfTimer": {
            "service": ["camera"],
            "params": ["selfTimer"],
            "version": "1.0"
        },
        "getSelfTimer": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getSupportedSelfTimer": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getAvailableSelfTimer": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Exposure mode
        "setExposureMode": {
            "service": ["camera"],
            "params": ["exposureMode"],
            "version": "1.0"
        },
        "getExposureMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getSupportedExposureMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getAvailableExposureMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Focus mode
        "setFocusMode": {
            "service": ["camera"],
            "params": ["focusMode"],
            "version": "1.0"
        },
        "getFocusMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getSupportedFocusMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getAvailableFocusMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Exposure compensation
        "setExposureCompensation": {
            "service": ["camera"],
            "params": ["exposureCompensation"],
            "version": "1.0"
        },
        "getExposureCompensation": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getSupportedExposureCompensation": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getAvailableExposureCompensation": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #F number
        "setFNumber": {
            "service": ["camera"],
            "params": ["fNumber"],
            "version": "1.0"
        },
        "getFNumber": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getSupportedFNumber": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getAvailableFNumber": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Shutter speed
        "setShutterSpeed": {
            "service": ["camera"],
            "params": ["shutterSpeed"],
            "version": "1.0"
        },
        "getShutterSpeed": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getAvailableShutterSpeed": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getSupportedShutterSpeed": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #ISO speed rate
        "setIsoSpeedRate": {
            "service": ["camera"],
            "params": ["isoSpeedRate"],
            "version": "1.0"
        },
        "getIsoSpeedRate": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getSupportedIsoSpeedRate": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getAvailableIsoSpeedRate": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #White bzalance
        "setWhiteBalance": {
            "service": ["camera"],
            "params": [
                "whiteBalanceMode", "colorTemperatureEnabled",
                "colorTemperature"
            ],
            "version": "1.0"
        },

        #Program shift
        "setProgramShift": {
            "service": ["camera"],
            "params": ["programShift"],
            "version": "1.0"
        },
        "getSupportedProgramShift": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Flash mode
        "setFlashMode": {
            "service": ["camera"],
            "params": ["flashMode"],
            "version": "1.0"
        },
        "getFlashMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getSupportedFlashMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getAvailableFlashMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Still size (N/A)
        #Still quality (N/A)

        #Postview image size
        "setPostviewImageSize": {
            "service": ["camera"],
            "params": ["postviewImageSize"],
            "version": "1.0"
        },
        "getPostviewImageSize": {
            "service": ["camera"],
            "params": ["postviewImageSize"],
            "version": "1.0"
        },
        "getSupportedPostviewImageSize": {
            "service": ["camera"],
            "params": ["postviewImageSize"],
            "version": "1.0"
        },
        "getAvailablePostviewImageSize": {
            "service": ["camera"],
            "params": ["postviewImageSize"],
            "version": "1.0"
        },

        #Movie file format (N/A)
        #Movie quality (N/A)
        #Steady mode (N/A)
        #View angle (N/A)
        #Scene selection (N/A)
        #Color setting (N/A)
        #Interval time (N/A)
        #Flip setting (N/A)
        #TV color system (N/A)

        #Camera setup
        "startRecMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "stopRecMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },

        #Camera function (N/A)
        #Transfering images (N/A)
        #Remode playback (N/A)
        #Delete contents (N/A)
        #IR remote control (N/A)
        #Auto power off (N/A)
        #Beep mode (N/A)
        #Date/time setting (N/A)
        #Storage information (N/A)

        #Event notification
        "getEvent": {
            "service": ["camera"],
            "params": ["longPollingFlag"],
            "version": "1.0"
        },

        #Server information
        "getAvailableApiList": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getApplicationInfo": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getVersions": {
            "service": ["camera", "system", "avContent"],
            "params": [],
            "version": "1.0"
        },
        "getMethodTypes": {
            "service": ["camera"],
            "params": [],
            "version": "1.0"
        },
        "getMethodTypes": {
            "service": ["camera", "system", "avContent"],
            "params": ["apiVersion"],
            "version": "1.0"
        },
    }

    __PARAMS = {
        #startLiveViewWithSize
        "liveviewSize": ["L", "M"],
        #actZoom
        "zoomDirection": ["in", "out"],
        "zoomMovement": ["start", "stop", "1shot"],
        #setZoomSetting
        "zoom": ["Optical Zoom Only", "On:Clear Image Zoom"],
        #setExposureMode
        "exposureMode": [
            "Program Auto", "Aperture", "Shutter", "Manual",
            "Intelligent Auto", "Superior Auto"
        ],
        #setFocusMode
        "focusMode": ["AF-S", "AF-C", "DMF", "MF"],
        #setWhiteBalance
        "whiteBalanceMode": [
            "Auto WB", "Daylight", "Shade", "Cloudy", "Incandescent"
            "Fluorescent: Warm White (-1)", "Fluorescent: Cool White (0)",
            "Fluorescent: Day White (+1)", "Fluorescent: Daylight (+2)",
            "Flash", "Color Temperature", "Custom 1", "Custom 2", "Custom 3"
        ],
        #setFlasmode
        "flashMode": ["off", "auto", "on", "slowSync", "rearSync", "wireless"],
        #setPostviewImageSize
        "postviewImageSize": ["Original",  "2M"],

        #setShootMode
        "shootMode": ["still", "movie", "audio", "intervalstill"],
    }

    __TYPES = {
        #setTouchAFPosition
        "xAxisPosition": float,
        "yAxisPosition": float,
        #setSelfTimer
        "selfTimer": int,
        #setExposureCompensation
        "exposureCompensation": int,
        #setWhiteBalance
        "colorTemperatureEnabled": bool,
        "colorTemperature": int,
        #setProgramShift
        "programShift": int,

        #getEvent
        "longPollingFlag": bool,
    }

    def __init__(self):
        self.__request_id = 1
        self.__device_server = None
        self.__service = None
        self.__timeout = 2

    def set_device_server(self, device_server):
        self.__device_server = device_server
        self.__service = None

    def set_service(self, service):
        if self.__device_server is None:
            raise Exception("device server not set")

        if not self.__device_server.has_api_service(service):
            raise Exception("service not provided by device server")

        self.__service = service

    def set_timeout(self, timeout):
        self.__timeout = timeout

    def __getattr__(self, name):
        if name in SimpleRemoteApi.__METHODS:
            return partial(self.__trunk, name)
        else:
            raise AttributeError("Attribute %s not found" % (name,))

    def __trunk(self, name, *args, **kwargs):
        if self.__device_server is None:
            raise Exception("device server not set")

        #check that the function exists in the service
        method = SimpleRemoteApi.__METHODS[name]
        if self.__service not in method["service"]:
            raise Exception("\"%s\": method not provided by the service" % (name,))
        params = method["params"]
        if len(args) != 0 or len(kwargs) > len(params):
            raise Exception('wrong number of parameters')
        by_order = method.get("by_order", True)

        #param checks
        for param_name, param_value in kwargs.items():
            #check param name (enables optional parameters)
            if param_name not in params:
                raise Exception("\"%s\" : unknown parameter" % (param_name,))
            #check param value
            if param_name in self.__PARAMS:
                if param_value not in self.__PARAMS[param_name]:
                    raise ValueError("\"%s\" : unknown value" % (param_value,))
            elif param_name in self.__TYPES:
                if type(param_value) != self.__TYPES[param_name]:
                    raise ValueError("\"%s\" : wrong type" % (param_value,))
        #fill the "params" in the query
        if by_order:
            param_items = []
            for param_name, param_value in kwargs.items():
                param_items.append(param_value)
        else:
            param_items = [{}]
            for param_name, param_value in kwargs.items():
                param_items[0][param_name] = param_value

        data = {
            "method": name,
            "params": param_items,
            "id": self.__request_id,
            "version": method["version"]
        }
        req_id = self.__request_id
        self.__request_id += 1

        if self.__service not in method["service"]:
            raise Exception("service error")
        url = self.__device_server.get_endpoint_url(self.__service)

        data_json = json.dumps(data)
        headers = {'content-type': 'application/json'}
        req = urllib2.Request(url, data_json, headers)
        resp_json = urllib2.urlopen(req, timeout=self.__timeout).read()
        resp = json.loads(resp_json)

        if req_id != req_id:
            raise Exception("bad id")

        if "result" in resp:
            #print resp["result"]
            return True, resp["result"]
        if "results" in resp:
            #print resp["results"]
            return True, resp["results"]

        if "error" in resp:
           #print("code: %d, error \"%s\"" % tuple(resp["error"]))
            return False, tuple(resp["error"])[1]
