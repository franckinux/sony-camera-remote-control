# -*- coding: utf-8 -*-

from distutils.version import StrictVersion
from functools import partial
import json
import logging
import socket
import urllib

# from utils import debug_trace

MINIMUM_API_VERSION = "2.0.0"


class CameraRemoteApi(object):

    SERVICE_NAME = "camera"

    __METHODS = {
        # Shoot mode
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

        # Still capture
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

        # Movie recording
        "startMovieRec": {
            "params": [],
            "version": "1.0"
        },
        "stopMovieRec": {
            "params": [],
            "version": "1.0"
        },

        # Audio recording (N/A)
        # Intervall still recording (N/A)

        # Liveview
        "startLiveview": {
            "params": [],
            "version": "1.0"
        },
        "stopLiveview": {
            "params": [],
            "version": "1.0"
        },

        # Liveview size
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

        # Liveview frame (N/A)

        # Zoom
        "actZoom": {
            "params": ["zoomDirection", "zoomMovement"],
            "version": "1.0"
        },

        # Zoom setting (N/A)
        # Half-press shutter (N/A)

        # Touch AF position
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

        # Tracking focus (N/A)
        # Continuous shooting mode (N/A)
        # Continuous shooting speed (N/A)

        # Self-timer
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

        # Exposure mode
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

        # Focus mode
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

        # Exposure compensation
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

        # F number
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

        # Shutter speed
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

        # ISO speed rate
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

        # White balance
        "setWhiteBalance": {
            "params": [
                "whiteBalanceMode", "colorTemperatureEnabled",
                "colorTemperature"
            ],
            "version": "1.0"
        },
        "getWhiteBalance": {
            "params": [],
            "version": "1.0"
        },
        "getSupportedWhiteBalance": {
            "params": [],
            "version": "1.0"
        },
        "getAvailableWhiteBalance": {
            "params": [],
            "version": "1.0"
        },

        # Program shift
        "setProgramShift": {
            "params": ["programShift"],
            "version": "1.0"
        },
        "getSupportedProgramShift": {
            "params": [],
            "version": "1.0"
        },

        # Flash mode
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

        # Still size (N/A)
        # Still quality (N/A)

        # Postview image size
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

        # Movie file format (N/A)
        # Movie quality (N/A)
        # Steady mode (N/A)
        # View angle (N/A)
        # Scene selection (N/A)
        # Color setting (N/A)
        # Interval time (N/A)
        # Flip setting (N/A)
        # TV color system (N/A)

        # Camera setup
        "startRecMode": {
            "params": [],
            "version": "1.0",
            "available_api_list_changed": True,
        },
        "stopRecMode": {
            "service": ["camera"],
            "params": [],
            "version": "1.0",
            "available_api_list_changed": True,
        },

        # Camera function (N/A)
        # Transfering images (N/A)
        # Remode playback (N/A)
        # Delete contents (N/A)
        # IR remote control (N/A)
        # Auto power off (N/A)
        # Beep mode (N/A)
        # Date/time setting (N/A)
        # Storage information (N/A)

        # Event notification
        "getEvent": {
            "params": ["longPollingFlag"],
            "version": "1.0"
        },

        # Server information
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
            "params": ["apiVersion"],
            "version": "1.0"
        },
    }

    __PARAMS = {
        # startLiveViewWithSize
        "liveviewSize": ["L", "M"],
        # actZoom
        "zoomDirection": ["in", "out"],
        "zoomMovement": ["start", "stop", "1shot"],
        # setZoomSetting
        "zoom": ["Optical Zoom Only", "On:Clear Image Zoom"],
        # setExposureMode
        "exposureMode": [
            "Program Auto", "Aperture", "Shutter", "Manual",
            "Intelligent Auto", "Superior Auto"
        ],
        # setFocusMode
        "focusMode": ["AF-S", "AF-C", "DMF", "MF"],
        # setWhiteBalance
        "whiteBalanceMode": [
            "Auto WB", "Daylight", "Shade", "Cloudy", "Incandescent"
            "Fluorescent: Warm White (-1)", "Fluorescent: Cool White (0)",
            "Fluorescent: Day White (+1)", "Fluorescent: Daylight (+2)",
            "Flash", "Color Temperature", "Custom 1", "Custom 2", "Custom 3"
        ],
        # setFlasmode
        "flashMode": ["off", "auto", "on", "slowSync", "rearSync", "wireless"],
        # setPostviewImageSize
        "postviewImageSize": ["Original", "2M"],

        # setShootMode
        "shootMode": ["still", "movie", "audio", "intervalstill"],
    }

    __TYPES = {
        # setTouchAFPosition
        "xAxisPosition": float,
        "yAxisPosition": float,
        # setSelfTimer
        "selfTimer": int,
        # setExposureCompensation
        "exposureCompensation": int,
        # setWhiteBalance
        "colorTemperatureEnabled": bool,
        "colorTemperature": int,
        # setProgramShift
        "programShift": int,

        # getEvent
        "longPollingFlag": bool,
        # getMethodTypes
        "apiVersion": str,
    }

    def __init__(self, endpoint_url):
        self.__endpoint_url = endpoint_url
        self.__request_id = 1
        self.__timeout = 5
        self.__global_api_version_ok = False
        # solve the chicken and egg problem
        self.__available_api_list = ["getAvailableApiList"]

    def __get_available_api_list(self):
        status, result = self.getAvailableApiList()
        if status:
            self.__available_api_list = result[0]

    def set_available_api_list(self, available_api_list):
        self.__available_api_list = available_api_list

    def is_method_available(self, method):
        """Checks if a method is currently available"""
        return method in self.__available_api_list

    def initial_checks(self):
        """Perform initial ckecks just after remote api creation"""
        # get initial available api list
        self.__get_available_api_list()

        # check global api version
        status, result = self.getApplicationInfo()
        if status:
            api_version_str = result[1]
            self.__global_api_version_ok = \
                StrictVersion(api_version_str) >= StrictVersion(MINIMUM_API_VERSION)
            logging.info("Api name: " + result[0] + ", Api version: " + api_version_str)
            logging.debug("Api version OK ? " + str(self.__global_api_version_ok))

        # update method versions
        status, result = self.getVersions()
        if status:
            # get highest supported api version
            api_version = sorted(result[0], key=StrictVersion)[-1]
            logging.info("api version chosen: %s" % (api_version,))
            status, result = self.getMethodTypes(apiVersion=api_version)
            if status:
                for method_list in result:
                    method_name = method_list[0]
                    new_version = method_list[-1]
                    try:
                        current_version = CameraRemoteApi.__METHODS[method_name]["version"]
                    except KeyError:
                        logging.error("unknown %s method" % (method_name,))
                        continue
                    if StrictVersion(new_version) > StrictVersion(current_version):
                        CameraRemoteApi.__METHODS[method_name]["version"] = new_version
                        logging.debug("updating %s method version : %s -> %s" %
                                  (method_name, current_version, new_version))

    def set_default_timeout(self, timeout):
        self.__timeout = timeout

    def __getattr__(self, name):
        """Used for getting api methods"""
        error_msg = ""
        if name not in self.__available_api_list:
            error_msg = "method %s not in available api list" % (name,)
        elif name not in CameraRemoteApi.__METHODS:
            error_msg = "unknown %s method" % (name,)
        if error_msg != "":
            logging.error(error_msg)
            name = None
        return partial(self.__trunk, name)

    def __trunk(self, name, *args, **kwargs):
        if name is None:
            # the method is not available
            return True, None
        method = CameraRemoteApi.__METHODS[name]
        params = method["params"]

        # checks param numbers
        timeout = self.__timeout
        args_len = len(args)
        if 0 <= args_len <= 1:
            if args_len == 1:
                timeout = args[0]
        else:
            logging.error("%d parameters for %s method" % (args_len, name))
            return False, "wrong number of parameters"
        kwargs_len = len(kwargs)
        if kwargs_len > len(params):
            logging.error("%d keyword parameters for %s method" % (kwargs_len, name))
            return False, "wrong number of keyword parameters"

        # param checks
        for param_name, param_value in kwargs.items():
            # check param name (enables optional parameters)
            if param_name not in params:
                raise Exception("\"%s\" : unknown parameter" % (param_name,))
            # check param value
            if param_name in self.__PARAMS:
                if param_value not in self.__PARAMS[param_name]:
                    raise ValueError("\"%s\" : unknown value" % (param_value,))
            elif param_name in self.__TYPES:
                if type(param_value) != self.__TYPES[param_name]:
                    raise ValueError("\"%s\" : wrong type" % (param_value,))
        # fill the query "params" value
        if method.get("by_order", True):
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
        logging.debug("called > %s" % (data_json,))
        headers = {'content-type': 'application/json'}
        req = urllib.request.Request(self.__endpoint_url, data_json.encode("ascii"), headers)
        try:
            resp_json = urllib.request.urlopen(req, None, timeout).read()
        except (socket.timeout, urllib.error.URLError):
            return False, "timeout"
        resp = json.loads(resp_json.decode("ascii"))
        logging.debug("received < %s" % (resp,))

        if resp["id"] != req_id:
            raise Exception("bad id")

        if "result" in resp or "results" in resp:
            if method.get("available_api_list_changed", False):
                self.__get_available_api_list()
            if "result" in resp:
                return True, resp["result"]
            else:
                return True, resp["results"]

        if "error" in resp:
            return False, tuple(resp["error"])
