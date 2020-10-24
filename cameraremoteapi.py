import aiohttp
import asyncio
from distutils.version import StrictVersion
from functools import partial
import json
import logging
from utils import upper_first_letter

# from utils import debug_trace

MINIMUM_API_VERSION = "2.0.0"

logger = logging.getLogger("cameraremote")


class CameraRemoteException(Exception):
    pass


class CameraRemoteEventWatcher:

    def __init__(self, camera_remote_api):
        self.__camera_remote_api = camera_remote_api
        self.event_watcher_task = None

        self.__registered_events = {
            "cameraStatus": None,
            "zoomInformation": None,
            "liveviewStatus": None,
            "liveviewOrientation": None,
            "takePicture": None,
            "storageInformation": None,
            "beepMode": None,
            "cameraFunction": None,
            "movieQuality": None,
            "stillSize": None,
            "cameraFunctionResult": None,
            "steadyMode": None,
            "viewAngle": None,
            "exposureMode": None,
            "postviewImageSize": None,
            "selfTimer": None,
            "shootMode": None,
            "exposureCompensation": None,
            "flashMode": None,
            "fNumber": None,
            "focusMode": None,
            "isoSpeedRate": None,
            "programShift": None,
            "shutterSpeed": None,
            "whiteBalance": None,
            "touchAFPosition": None,
            "focusStatus": None,
            "zoomSetting": None,
            "stillQuality": None,
            "contShootingMode": None,
            "contShootingSpeed": None,
            "contShooting": None,
            "flipSetting": None,
            "sceneSelection": None,
            "intervalTime": None,
            "colorSetting": None,
            "movieFileFormat": None,
            "infraredRemoteControl": None,
            "tvColorSystem": None,
            "trackingFocusStatus": None,
            "trackingFocus": None,
            "batteryInfo": None,
            "recordingTime": None,
            "numberOfShots": None,
            "autoPowerOff": None,
            "loopRecTime": None,
            "audioRecording": None,
            "windNoiseReduction": None,
        }

    def register_events(self, watched_events):
        for event_name, event_callback in watched_events.items():
            if event_name in self.__registered_events:
                self.__registered_events[event_name] = event_callback
            else:
                raise CameraRemoteException("unknwon event name %s" % (event_name))

    def __process_dict_item(self, item):
        event_name = item["type"]
        try:
            event_callback = self.__registered_events[event_name]
        except KeyError as e:
            raise CameraRemoteException("unknown event name %s" % (event_name,)) from e
        if event_callback is None:
            # the event is not watched
            return

        capitalized_event_name = upper_first_letter(event_name)
        current_item_key = "current" + capitalized_event_name
        if current_item_key in item:
            data = {}
            data["Current"] = item[current_item_key]
            try:
                data["Candidates"] = item[event_name + "Candidates"]
            except KeyError:
                try:
                    min_ = item["min" + capitalized_event_name]
                    max_ = item["max" + capitalized_event_name]
                    step = item["stepIndexOf" + capitalized_event_name]
                    value = min_
                    candidates = []
                    while value <= max_:
                        candidates.append(str(value))
                        value += step
                    data["Candidates"] = candidates
                except KeyError:
                    return
        else:
            data = item
        event_callback(data)

    async def __watcher(self):
        long_polling_flag = False
        while True:
            result = await self.__camera_remote_api.getEvent(None, longPollingFlag=long_polling_flag)
            if result[0] is not None:
                available_api_list = result[0]["names"]
                self.__camera_remote_api.set_available_api_list(available_api_list)

            for item in result[1:]:
                if type(item) == dict:
                    self.__process_dict_item(item)
                if type(item) == list:
                    for litem in item:
                        self.__process_dict_item(litem)
            long_polling_flag = True

    def __end_watcher(self, f):
        exception = f.exception()
        if exception is not None:
            logger.error("watcher event loop stopped unexpectedly, reason: %s" % (str(exception),))

    def start_event_watcher(self):
        self.event_watcher_task = asyncio.create_task(self.__watcher())
        self.event_watcher_task.add_done_callback(self.__end_watcher)

    def stop_event_watcher(self):
        if self.event_watcher_task is not None:
            self.event_watcher_task.cancel()


class CameraRemoteApi:

    SERVICE_NAME = "camera"

    def __init__(self, endpoint_url):
        self.__endpoint_url = endpoint_url
        self.__session = aiohttp.ClientSession(
            loop=asyncio.get_event_loop()
        )

        self.__request_id = 1
        self.__timeout = 5
        self.__global_api_version_ok = False
        # solve the chicken and egg problem
        self.__available_api_list = ["getAvailableApiList"]
        self.__events_watcher = CameraRemoteEventWatcher(self)

        self.__METHODS = {
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

            # Half-press shutter
            "actHalfPressShutter": {
                "params": [],
                "version": "1.0"
            },
            "cancelHalfPressShutter": {
                "params": [],
                "version": "1.0"
            },

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
                    "whiteBalanceMode",
                    "colorTemperatureEnabled",
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

        self.__PARAMS = {
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
                "Flash", "Color Temperature", "Custom"
            ],
            # setFlasmode
            "flashMode": ["off", "auto", "on", "slowSync", "rearSync", "wireless"],
            # setPostviewImageSize
            "postviewImageSize": ["Original", "2M"],

            # setShootMode
            "shootMode": ["still", "movie", "audio", "intervalstill"],
        }

        self.__TYPES = {
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

    async def __get_available_api_list(self):
        result = await self.getAvailableApiList()
        self.__available_api_list = result[0]

    def set_available_api_list(self, available_api_list):
        self.__available_api_list = available_api_list

    def is_method_available(self, method):
        """Checks if a method is currently available"""
        return method in self.__available_api_list

    async def initial_checks(self):
        """Perform initial ckecks"""
        # get initial available api list
        await self.__get_available_api_list()

        # check global api version
        result = await self.getApplicationInfo()
        api_version_str = result[1]
        self.__global_api_version_ok = \
            StrictVersion(api_version_str) >= StrictVersion(MINIMUM_API_VERSION)
        logger.info("Api name: " + result[0] + ", Api version: " + api_version_str)
        logger.debug("Api version OK ? " + str(self.__global_api_version_ok))

        # update method versions
        result = await self.getVersions()
        # get highest supported api version
        api_version = sorted(result[0], key=StrictVersion)[-1]
        logger.info("api version chosen: %s" % (api_version,))
        result = await self.getMethodTypes(apiVersion=api_version)
        for method_list in result:
            method_name = method_list[0]
            new_version = method_list[-1]
            try:
                current_version = self.__METHODS[method_name]["version"]
            except KeyError:
                logger.error("unknown %s method" % (method_name,))
                continue
            if StrictVersion(new_version) > StrictVersion(current_version):
                self.__METHODS[method_name]["version"] = new_version
                logger.debug("updating %s method version : %s -> %s" %
                          (method_name, current_version, new_version))
        return self.__events_watcher

    def set_default_timeout(self, timeout):
        self.__timeout = timeout

    def __getattr__(self, name):
        """Used for getting api methods"""
        error_msg = ""
        if name not in self.__available_api_list:
            error_msg = "method %s not in available api list" % (name,)
        elif name not in self.__METHODS:
            error_msg = "unknown %s method" % (name,)
        if error_msg != "":
            logger.error(error_msg)
            name = None
        return partial(self.__trunk, name)

    async def __get_response(self, data, headers, timeout):
        logger.debug("called > %s" % (data,))
        try:
            response = await self.__session.post(
                self.__endpoint_url,
                data=data.encode("ascii"),
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            )
            if response.status == 200:
                resp = await response.json()
                logger.debug("received < %s" % (resp,))
            else:
                raise CameraRemoteException("http error %d" % (response.status,))
        except asyncio.exceptions.TimeoutError as e:
            raise CameraRemoteException("reception timeout") from e
        else:
            response.release()
        return resp

    async def __trunk(self, name, *args, **kwargs):
        if name is None:
            # the method is not available : fail silently
            return None
        method = self.__METHODS[name]
        params = method["params"]

        # checks param numbers
        timeout = self.__timeout
        args_len = len(args)
        if 0 <= args_len <= 1:
            if args_len == 1:
                timeout = args[0]
        else:
            logger.error("%d parameters for %s method" % (args_len, name))
            raise CameraRemoteException("wrong number of parameters")
        kwargs_len = len(kwargs)
        if kwargs_len > len(params):
            logger.error("%d keyword parameters for %s method" % (kwargs_len, name))
            raise CameraRemoteException("wrong number of keyword parameters")

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
        param_items = []
        for param_name in params:
            param_items.append(kwargs[param_name])

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
        resp = await self.__get_response(data_json, headers, timeout)

        if resp["id"] != req_id:
            raise CameraRemoteException("bad id")

        if "result" in resp or "results" in resp:
            if method.get("available_api_list_changed", False):
                await self.__get_available_api_list()
            if "result" in resp:
                return resp["result"]
            else:
                return resp["results"]

        if "error" in resp:
            error = resp["error"][1]
            logger.error(error)
            raise CameraRemoteException(error)

    async def close(self):
        if self.__events_watcher is not None:
            self.__events_watcher.stop_event_watcher()
        await self.__session.close()
