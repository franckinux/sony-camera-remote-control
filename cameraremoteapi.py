# -*- coding: utf-8 -*-

from functools import partial
import json
import urllib2

#import pdb; pdb.set_trace()

class CameraRemoteApi(object):

    SERVICE_NAME = "camera"

    __METHODS = {
        #Shoot mode
        "setShootMode": {
            "params": ["shootMode"],
            "version": "1.0"
        },
        "getShootMode": {
            "params": [],
            "version": "1.0"
        },
        "getSupportedShootMode": {
            "params": [],
             "version": "1.0"
        },
        "getAvailableShootMode": {
            "params": [],
            "version": "1.0"
        },

        #Still capture
        "actTakePicture": {
            "params": [],
            "version": "1.0"
        },
        "awaitTakePicture": {
            "params": [],
            "version": "1.0"
        },
        "startContShooting": {
            "params": [],
            "version": "1.0"
        },
        "stoptContShooting": {
            "params": [],
            "version": "1.0"
        },

        #Movie recording
        "startMovieRec": {
            "params": [],
            "version": "1.0"
        },
        "stopMovieRec": {
            "params": [],
            "version": "1.0"
        },

        #Audio recording (N/A)
        #Intervall still recording (N/A)

        #Liveview
        "startLiveview": {
            "params": [],
            "version": "1.0"
        },
        "stopLiveview": {
            "params": [],
            "version": "1.0"
        },

        #Liveview size
        "startLiveviewWithSize": {
            "params": ["liveviewSize"],
            "version": "1.0"
        },
        "getLiveviewSize": {
            "params": ["liveviewSize"],
            "version": "1.0"
        },
        "getSupportedLiveviewSize": {
            "params": ["liveviewSize"],
            "version": "1.0"
        },
        "getAvailableLiveviewSize": {
            "params": ["liveviewSize"],
            "version": "1.0"
        },

        #Liveview frame (N/A)

        #Zoom
        "actZoom": {
            "params": ["zoomDirection", "zoomMovement"],
            "version": "1.0"
        },

        #Zoom setting (N/A)
        #Half-press shutter (N/A)

        #Touch AF position
        "setTouchAFPosition": {
            "params": ["xAxisPosition", "yAxisPosition"],
            "version": "1.0"
        },
        "getTouchAFPosition": {
            "params": [],
            "version": "1.0"
        },
        "cancelTouchAFPosition": {
            "params": [],
            "version": "1.0"
        },

        #Tracking focus (N/A)
        #Continuous shooting mode (N/A)
        #Continuous shooting speed (N/A)

        #Self-timer
        "setSelfTimer": {
            "params": ["selfTimer"],
            "version": "1.0"
        },
        "getSelfTimer": {
            "params": [],
            "version": "1.0"
        },
        "getSupportedSelfTimer": {
            "params": [],
            "version": "1.0"
        },
        "getAvailableSelfTimer": {
            "params": [],
            "version": "1.0"
        },

        #Exposure mode
        "setExposureMode": {
            "params": ["exposureMode"],
            "version": "1.0"
        },
        "getExposureMode": {
            "params": [],
            "version": "1.0"
        },
        "getSupportedExposureMode": {
            "params": [],
            "version": "1.0"
        },
        "getAvailableExposureMode": {
            "params": [],
            "version": "1.0"
        },

        #Focus mode
        "setFocusMode": {
            "params": ["focusMode"],
            "version": "1.0"
        },
        "getFocusMode": {
            "params": [],
            "version": "1.0"
        },
        "getSupportedFocusMode": {
            "params": [],
            "version": "1.0"
        },
        "getAvailableFocusMode": {
            "params": [],
            "version": "1.0"
        },

        #Exposure compensation
        "setExposureCompensation": {
            "params": ["exposureCompensation"],
            "version": "1.0"
        },
        "getExposureCompensation": {
            "params": [],
            "version": "1.0"
        },
        "getSupportedExposureCompensation": {
            "params": [],
            "version": "1.0"
        },
        "getAvailableExposureCompensation": {
            "params": [],
            "version": "1.0"
        },

        #F number
        "setFNumber": {
            "params": ["fNumber"],
            "version": "1.0"
        },
        "getFNumber": {
            "params": [],
            "version": "1.0"
        },
        "getSupportedFNumber": {
            "params": [],
            "version": "1.0"
        },
        "getAvailableFNumber": {
            "params": [],
            "version": "1.0"
        },

        #Shutter speed
        "setShutterSpeed": {
            "params": ["shutterSpeed"],
            "version": "1.0"
        },
        "getShutterSpeed": {
            "params": [],
            "version": "1.0"
        },
        "getAvailableShutterSpeed": {
            "params": [],
            "version": "1.0"
        },
        "getSupportedShutterSpeed": {
            "params": [],
            "version": "1.0"
        },

        #ISO speed rate
        "setIsoSpeedRate": {
            "params": ["isoSpeedRate"],
            "version": "1.0"
        },
        "getIsoSpeedRate": {
            "params": [],
            "version": "1.0"
        },
        "getSupportedIsoSpeedRate": {
            "params": [],
            "version": "1.0"
        },
        "getAvailableIsoSpeedRate": {
            "params": [],
            "version": "1.0"
        },

        #White bzalance
        "setWhiteBalance": {
            "params": [
                "whiteBalanceMode", "colorTemperatureEnabled",
                "colorTemperature"
            ],
            "version": "1.0"
        },

        #Program shift
        "setProgramShift": {
            "params": ["programShift"],
            "version": "1.0"
        },
        "getSupportedProgramShift": {
            "params": [],
            "version": "1.0"
        },

        #Flash mode
        "setFlashMode": {
            "params": ["flashMode"],
            "version": "1.0"
        },
        "getFlashMode": {
            "params": [],
            "version": "1.0"
        },
        "getSupportedFlashMode": {
            "params": [],
            "version": "1.0"
        },
        "getAvailableFlashMode": {
            "params": [],
            "version": "1.0"
        },

        #Still size (N/A)
        #Still quality (N/A)

        #Postview image size
        "setPostviewImageSize": {
            "params": ["postviewImageSize"],
            "version": "1.0"
        },
        "getPostviewImageSize": {
            "params": ["postviewImageSize"],
            "version": "1.0"
        },
        "getSupportedPostviewImageSize": {
            "params": ["postviewImageSize"],
            "version": "1.0"
        },
        "getAvailablePostviewImageSize": {
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
            "params": ["longPollingFlag"],
            "version": "1.0"
        },

        #Server information
        "getAvailableApiList": {
            "params": [],
            "version": "1.0"
        },
        "getApplicationInfo": {
            "params": [],
            "version": "1.0"
        },
        "getVersions": {
            "params": [],
            "version": "1.0"
        },
        "getMethodTypes": {
            "params": [],
            "version": "1.0"
        },
        "getMethodTypes": {
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

    def __init__(self, endpoint_url):
        self.__endpoint_url = endpoint_url
        self.__request_id = 1
        self.__timeout = 2

    def set_timeout(self, timeout):
        self.__timeout = timeout

    def __getattr__(self, name):
        if name in CameraRemoteApi.__METHODS:
            return partial(self.__trunk, name)
        else:
            raise AttributeError("Attribute %s not found" % (name,))

    def __trunk(self, name, *args, **kwargs):
        #check that the function exists in the service
        method = CameraRemoteApi.__METHODS[name]
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

        data_json = json.dumps(data)
        headers = {'content-type': 'application/json'}
        req = urllib2.Request(self.__endpoint_url, data_json, headers)
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
