#!/usr/bin/python2
# -*- coding: utf-8 -*-

#DIRECT-4vE0:ILCE-7R
#DIRECT-fBEO:ILCE-6000

from distutils.version import StrictVersion
from io import BytesIO
from NetworkManager import NetworkManager
from PIL import Image
import urllib2
import sys
import time
from urlparse import urljoin

from serverdevice import ServerDevice
from simpleremoteapi import SimpleRemoteApi
from ssdp import discover

#import pdb; pdb.set_trace()

def search_interfaces():
    """search for interfaces connected to a sony camera"""
    devices = [dev \
               for dev in NetworkManager.GetDevices() \
               if dev.Interface != "lo" and \
                  dev.SpecificDevice().__class__.__name__ == "Wireless"]
    candidate_devices = []
    for dev in devices:
        devi = dev.Interface
        devs = dev.SpecificDevice()
        access_point = devs.ActiveAccessPoint
        aps = access_point.Ssid
        #aps = "DIRECT-fBEO:ILCE-6000"
        aps0 = aps.split(':')
        if len(aps0) == 2:
            aps01 = aps0[0].split('-')
            if len(aps01) == 2:
                if aps01[0] == "DIRECT" and len(aps01[1]) == 4:
                    aps02 = aps0[1].split('-')
                    if aps02[0] in ["ILCE"] and aps02[1] in ["6000", "7R"]:
                        candidate_devices.append({"interface": devi,
                                                  "ssid": aps,
                                                  "address": dev.Ip4Address})
    return candidate_devices

def discover_camera(cam_addr):
    """discover sony device and record informations from this"""
    resp = discover("ssdp:all", timeout=5, retries=3, addr=cam_addr)
    services = []
    for r in resp:
        #decompose usn string
        usn = r.usn.split('::')

        uuid = None
        if len(usn) >= 1:
            if usn[0].startswith("uuid:"):
                uuid = usn[0][len("uuid:")+1:]

        urn = None
        if len(usn) == 2:
            if usn[1].startswith("urn:"):
                urn = usn[0][len("urn:")+1:]

        d = {"uuid": uuid, "urn": urn, "location": r.location}
        if d not in services:
            services.append(d)

    location = None
    for s in services:
        if location is None:
            location = s["location"]
        else:
            if location != s["location"]:
                raise Exception("multiple locations")

    if location is None:
        raise Exception("location is not defined")

    #read location
    xd = urllib2.urlopen(location)
    server_device = ServerDevice(xd.read())

    if server_device.model_name != "SonyImagingDevice":
       raise Exception("bad model name")

    return server_device, location

def main():
    candidate_devices = search_interfaces()

    if len(candidate_devices) == 0:
        print >> sys.stderr, "no interface connected to a sony camera"
        sys.exit(1)
    if len(candidate_devices) > 1:
        for i, cd in enumerate(candidate_devices):
            print i + " - " + cd["ssid"]
        i = input("choose camera")
        cam = candidate_devices[i]
    else:
        cam = candidate_devices[0]

    cam_interface = cam["interface"]
    cam_ssid = cam["ssid"]
    cam_addr = cam["address"]
    print cam_ssid + " on " + cam_interface + " which address is " + cam_addr

    server_device, location = discover_camera(cam_addr)
    camera = server_device.has_api_service("camera")
    print "camera : " + str(camera)
    av_content =server_device.has_api_service("avContent")
    print "avContent : " + str(av_content)

    remote_api = SimpleRemoteApi()
    remote_api.set_device_server(server_device)
    remote_api.set_service("camera")

    status, application_info = remote_api.getApplicationInfo()
    print "Application name : " + application_info[0]
    application_version = application_info[1]
    print "Appication version : "  + application_version
    if StrictVersion(application_version) < StrictVersion("2.0.0"):
        print "invalid application version"
        sys.exit(1)

    status, version = remote_api.getVersions()
    print "Version : " + version[0][0]
#[[u'1.0']]

    #remote_api.getMethodTypes(apiVersion="1.0")
#[[u'actTakePicture', [], [u'string*'], u'1.0'], [u'actZoom', [u'string', u'string'], [u'int'], u'1.0'], [u'awaitTakePicture', [], [u'string*'], u'1.0'], [u'cancelTouchAFPosition', [], [], u'1.0'], [u'getApplicationInfo', [], [u'string', u'string'], u'1.0'], [u'getAvailableApiList', [], [u'string*'], u'1.0'], [u'getAvailableExposureCompensation', [], [u'int', u'int', u'int', u'int'], u'1.0'], [u'getAvailableExposureMode', [], [u'string', u'string*'], u'1.0'], [u'getAvailableFNumber', [], [u'string', u'string*'], u'1.0'], [u'getAvailableFlashMode', [], [u'string', u'string*'], u'1.0'], [u'getAvailableFocusMode', [], [u'string', u'string*'], u'1.0'], [u'getAvailableIsoSpeedRate', [], [u'string', u'string*'], u'1.0'], [u'getAvailableLiveviewSize', [], [u'string', u'string*'], u'1.0'], [u'getAvailablePostviewImageSize', [], [u'string', u'string*'], u'1.0'], [u'getAvailableSelfTimer', [], [u'int', u'int*'], u'1.0'], [u'getAvailableShootMode', [], [u'string', u'string*'], u'1.0'], [u'getAvailableShutterSpeed', [], [u'string', u'string*'], u'1.0'], [u'getAvailableWhiteBalance', [], [u'{"whiteBalanceMode":"string", "colorTemperature":"int"}', u'{"whiteBalanceMode":"string", "colorTemperatureRange":"int*"}*'], u'1.0'], [u'getEvent', [u'bool'], [u'{"type":"string", "names":"string*"}', u'{"type":"string", "cameraStatus":"string"}', u'{"type":"string", "zoomPosition":"int", "zoomNumberBox":"int", "zoomIndexCurrentBox":"int", "zoomPositionCurrentBox":"int"}', u'{"type":"string", "liveviewStatus":"bool"}', u'{"type":"string", "liveviewOrientation":"string"}', u'{"type":"string", "takePictureUrl":"string*"}*', u'{"type":"string", "continuousError":"string", "isContinued":"bool"}*', u'{"type":"string", "triggeredError":"string*"}', u'{"type":"string", "sceneRecognition":"string", "steadyRecognition":"string", "motionRecognition":"string"}', u'{"type":"string", "formatResult":"string"}', u'{"type":"string", "storageID":"string", "recordTarget":"bool", "numberOfRecordableImages":"int", "recordableTime":"int", "storageDescription":"string"}*', u'{"type":"string", "currentBeepMode":"string", "beepModeCandidates":"string*"}', u'{"type":"string", "currentCameraFunction":"string", "cameraFunctionCandidates":"string*"}', u'{"type":"string", "currentMovieQuality":"string", "movieQualityCandidates":"string*"}', u'{"type":"string", "checkAvailability":"bool", "currentAspect":"string", "currentSize":"string"}', u'{"type":"string", "cameraFunctionResult":"string"}', u'{"type":"string", "currentSteadyMode":"string", "steadyModeCandidates":"string*"}', u'{"type":"string", "currentViewAngle":"int", "viewAngleCandidates":"int*"}', u'{"type":"string", "currentExposureMode":"string", "exposureModeCandidates":"string*"}', u'{"type":"string", "currentPostviewImageSize":"string", "postviewImageSizeCandidates":"string*"}', u'{"type":"string", "currentSelfTimer":"int", "selfTimerCandidates":"int*"}', u'{"type":"string", "currentShootMode":"string", "shootModeCandidates":"string*"}', u'{"type":"string", "currentAELock":"bool", "aeLockCandidates":"bool*"}', u'{"type":"string", "checkAvailability":"bool", "currentBracketShootMode":"string", "currentBracketShootModeOption":"string"}', u'{"type":"string", "checkAvailability":"bool", "currentCreativeStyle":"string", "currentCreativeStyleContrast":"int", "currentCreativeStyleSaturation":"int", "currentCreativeStyleSharpness":"int"}', u'{"type":"string", "currentExposureCompensation":"int", "maxExposureCompensation":"int", "minExposureCompensation":"int", "stepIndexOfExposureCompensation":"int"}', u'{"type":"string", "currentFlashMode":"string", "flashModeCandidates":"string*"}', u'{"type":"string", "currentFNumber":"string", "fNumberCandidates":"string*"}', u'{"type":"string", "currentFocusMode":"string", "focusModeCandidates":"string*"}', u'{"type":"string", "currentIsoSpeedRate":"string", "isoSpeedRateCandidates":"string*"}', u'{"type":"string", "checkAvailability":"bool", "currentPictureEffect":"string", "currentPictureEffectOption":"string"}', u'{"type":"string", "isShifted":"bool"}', u'{"type":"string", "currentShutterSpeed":"string", "shutterSpeedCandidates":"string*"}', u'{"type":"string", "checkAvailability":"bool", "currentWhiteBalanceMode":"string", "currentColorTemperature":"int"}', u'{"type":"string", "currentSet":"bool", "currentTouchCoordinates":"double*"}'], u'1.0'], [u'getExposureCompensation', [], [u'int'], u'1.0'], [u'getExposureMode', [], [u'string'], u'1.0'], [u'getFNumber', [], [u'string'], u'1.0'], [u'getFlashMode', [], [u'string'], u'1.0'], [u'getFocusMode', [], [u'string'], u'1.0'], [u'getIsoSpeedRate', [], [u'string'], u'1.0'], [u'getLiveviewSize', [], [u'string'], u'1.0'], [u'getPostviewImageSize', [], [u'string'], u'1.0'], [u'getSelfTimer', [], [u'int'], u'1.0'], [u'getShootMode', [], [u'string'], u'1.0'], [u'getShutterSpeed', [], [u'string'], u'1.0'], [u'getSupportedExposureCompensation', [], [u'int*', u'int*', u'int*'], u'1.0'], [u'getSupportedExposureMode', [], [u'string*'], u'1.0'], [u'getSupportedFNumber', [], [u'string*'], u'1.0'], [u'getSupportedFlashMode', [], [u'string*'], u'1.0'], [u'getSupportedFocusMode', [], [u'string*'], u'1.0'], [u'getSupportedIsoSpeedRate', [], [u'string*'], u'1.0'], [u'getSupportedLiveviewSize', [], [u'string*'], u'1.0'], [u'getSupportedPostviewImageSize', [], [u'string*'], u'1.0'], [u'getSupportedProgramShift', [], [u'int*'], u'1.0'], [u'getSupportedSelfTimer', [], [u'int*'], u'1.0'], [u'getSupportedShootMode', [], [u'string*'], u'1.0'], [u'getSupportedShutterSpeed', [], [u'string*'], u'1.0'], [u'getSupportedWhiteBalance', [], [u'{"whiteBalanceMode":"string", "colorTemperatureRange":"int*"}*'], u'1.0'], [u'getTouchAFPosition', [], [u'{"set":"bool", "touchCoordinates":"double*"}'], u'1.0'], [u'getWhiteBalance', [], [u'{"whiteBalanceMode":"string", "colorTemperature":"int"}'], u'1.0'], [u'setExposureCompensation', [u'int'], [u'int'], u'1.0'], [u'setExposureMode', [u'string'], [u'int'], u'1.0'], [u'setFNumber', [u'string'], [u'int'], u'1.0'], [u'setFlashMode', [u'string'], [u'int'], u'1.0'], [u'setFocusMode', [u'string'], [u'int'], u'1.0'], [u'setIsoSpeedRate', [u'string'], [u'int'], u'1.0'], [u'setPostviewImageSize', [u'string'], [u'int'], u'1.0'], [u'setProgramShift', [u'int'], [u'int'], u'1.0'], [u'setSelfTimer', [u'int'], [u'int'], u'1.0'], [u'setShootMode', [u'string'], [u'int'], u'1.0'], [u'setShutterSpeed', [u'string'], [u'int'], u'1.0'], [u'setTouchAFPosition', [u'double', u'double'], [u'int', u'{"AFResult":"bool", "AFType":"string"}'], u'1.0'], [u'setWhiteBalance', [u'string', u'bool', u'int'], [u'int'], u'1.0'], [u'startLiveview', [], [u'string'], u'1.0'], [u'startLiveviewWithSize', [u'string'], [u'string'], u'1.0'], [u'startMovieRec', [], [u'int'], u'1.0'], [u'startRecMode', [], [u'int'], u'1.0'], [u'stopLiveview', [], [u'int'], u'1.0'], [u'stopMovieRec', [], [u'string'], u'1.0'], [u'stopRecMode', [], [u'int'], u'1.0'], [u'getMethodTypes', [u'string'], [u'string', u'string*', u'string*', u'string'], u'1.0'], [u'getVersions', [], [u'string*'], u'1.0']]

    if camera:
        status, api_list = remote_api.getAvailableApiList()
        if "startRecMode" in api_list[0]:
            remote_api.startRecMode()

        #get shutter speed
        status, shutter_speed = remote_api.getShutterSpeed()
        print status
        if len(shutter_speed) == 1:
            print "Shutter speed : " + shutter_speed[0]
        else:
            print "No shutter speed available"
        status, shutter_speed = remote_api.getAvailableShutterSpeed()
        print "Available shutter speed : " + str(shutter_speed[1])
        status, shutter_speed = remote_api.getSupportedShutterSpeed()
        print "Supported shutter speed : " + str(shutter_speed[0])

        time.sleep(5)

        #take a picture
        remote_api.set_timeout(10)
        status, preview_url = remote_api.actTakePicture()
        preview_image = urllib2.urlopen(preview_url[0][0]).read()
        image = Image.open(BytesIO(preview_image))
        image.show()

        #event loops
        remote_api.set_timeout(None)
        status, events = remote_api.getEvent(longPollingFlag=False)
#[{u'type': u'availableApiList', u'names': [u'getVersions', u'getMethodTypes', u'getApplicationInfo', u'getAvailableApiList', u'getEvent', u'actTakePicture', u'stopRecMode', u'startLiveview', u'stopLiveview', u'startLiveviewWithSize', u'awaitTakePicture', u'setSelfTimer', u'getSelfTimer', u'getAvailableSelfTimer', u'getSupportedSelfTimer', u'setExposureMode', u'getAvailableExposureMode', u'getExposureMode', u'getSupportedExposureMode', u'setExposureCompensation', u'getExposureCompensation', u'getAvailableExposureCompensation', u'getSupportedExposureCompensation', u'getFNumber', u'getAvailableFNumber', u'getSupportedFNumber', u'setIsoSpeedRate', u'getIsoSpeedRate', u'getAvailableIsoSpeedRate', u'getSupportedIsoSpeedRate', u'getLiveviewSize', u'getAvailableLiveviewSize', u'getSupportedLiveviewSize', u'setPostviewImageSize', u'getPostviewImageSize', u'getAvailablePostviewImageSize', u'getSupportedPostviewImageSize', u'getSupportedProgramShift', u'setShootMode', u'getShootMode', u'getAvailableShootMode', u'getSupportedShootMode', u'setShutterSpeed', u'getShutterSpeed', u'getAvailableShutterSpeed', u'getSupportedShutterSpeed', u'setWhiteBalance', u'getWhiteBalance', u'getSupportedWhiteBalance', u'getAvailableWhiteBalance', u'getSupportedFlashMode', u'getFocusMode', u'getAvailableFocusMode', u'getSupportedFocusMode']}, {u'type': u'cameraStatus', u'cameraStatus': u'IDLE'}, {u'zoomPositionCurrentBox': -1, u'zoomNumberBox': -1, u'zoomIndexCurrentBox': -1, u'type': u'zoomInformation', u'zoomPosition': -1}, {u'liveviewStatus': False, u'type': u'liveviewStatus'}, None, [], [], None, None, None, [], None, None, None, None, None, None, None, {u'currentExposureMode': u'Manual', u'type': u'exposureMode', u'exposureModeCandidates': []}, {u'currentPostviewImageSize': u'2M', u'type': u'postviewImageSize', u'postviewImageSizeCandidates': [u'Original', u'2M']}, {u'type': u'selfTimer', u'selfTimerCandidates': [0, 2], u'currentSelfTimer': 2}, {u'currentShootMode': u'still', u'type': u'shootMode', u'shootModeCandidates': [u'still']}, None, None, None, {u'maxExposureCompensation': 15, u'type': u'exposureCompensation', u'currentExposureCompensation': 0, u'minExposureCompensation': -15, u'stepIndexOfExposureCompensation': 1}, {u'currentFlashMode': u'on', u'type': u'flashMode', u'flashModeCandidates': []}, {u'fNumberCandidates': [], u'type': u'fNumber', u'currentFNumber': u'--'}, {u'focusModeCandidates': [], u'type': u'focusMode', u'currentFocusMode': u'MF'}, {u'currentIsoSpeedRate': u'AUTO', u'type': u'isoSpeedRate', u'isoSpeedRateCandidates': [u'AUTO', u'100', u'125', u'160', u'200', u'250', u'320', u'400', u'500', u'640', u'800', u'1000', u'1250', u'1600', u'2000', u'2500', u'3200', u'4000', u'5000', u'6400', u'8000', u'10000', u'12800', u'16000', u'20000', u'25600']}, None, {u'type': u'programShift', u'isShifted': False}, {u'shutterSpeedCandidates': [u'30"', u'25"', u'20"', u'15"', u'13"', u'10"', u'8"', u'6"', u'5"', u'4"', u'3.2"', u'2.5"', u'2"', u'1.6"', u'1.3"', u'1"', u'0.8"', u'0.6"', u'0.5"', u'0.4"', u'1/3', u'1/4', u'1/5', u'1/6', u'1/8', u'1/10', u'1/13', u'1/15', u'1/20', u'1/25', u'1/30', u'1/40', u'1/50', u'1/60', u'1/80', u'1/100', u'1/125', u'1/160', u'1/200', u'1/250', u'1/320', u'1/400', u'1/500', u'1/640', u'1/800', u'1/1000', u'1/1250', u'1/1600', u'1/2000', u'1/2500', u'1/3200', u'1/4000'], u'currentShutterSpeed': u'1.6"', u'type': u'shutterSpeed'}, {u'checkAvailability': True, u'currentColorTemperature': -1, u'type': u'whiteBalance', u'currentWhiteBalanceMode': u'Auto WB'}, {u'currentTouchCoordinates': [], u'currentSet': False, u'type': u'touchAFPosition'}]
        print "Initial event = " + str(events)
        for _ in range(10):
            status, events = remote_api.getEvent(longPollingFlag=True)
            print "Next event = " + str(events)
#[None, None, None, None, None, [], [], None, None, None, [], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
#[{u'type': u'availableApiList', u'names': [u'getVersions', u'getMethodTypes', u'getApplicationInfo', u'getAvailableApiList', u'getEvent', u'stopRecMode', u'startLiveview', u'stopLiveview', u'startLiveviewWithSize', u'awaitTakePicture', u'getSelfTimer', u'getAvailableSelfTimer', u'getSupportedSelfTimer', u'getAvailableExposureMode', u'getExposureMode', u'getSupportedExposureMode', u'getExposureCompensation', u'getAvailableExposureCompensation', u'getSupportedExposureCompensation', u'getFNumber', u'getAvailableFNumber', u'getSupportedFNumber', u'getIsoSpeedRate', u'getAvailableIsoSpeedRate', u'getSupportedIsoSpeedRate', u'getLiveviewSize', u'getAvailableLiveviewSize', u'getSupportedLiveviewSize', u'getPostviewImageSize', u'getAvailablePostviewImageSize', u'getSupportedPostviewImageSize', u'getSupportedProgramShift', u'getShootMode', u'getAvailableShootMode', u'getSupportedShootMode', u'getShutterSpeed', u'getAvailableShutterSpeed', u'getSupportedShutterSpeed', u'getWhiteBalance', u'getSupportedWhiteBalance', u'getAvailableWhiteBalance', u'getSupportedFlashMode', u'getFocusMode', u'getAvailableFocusMode', u'getSupportedFocusMode']}, None, None, None, None, [], [], None, None, None, [], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]

        status, api_list = remote_api.getAvailableApiList()
        if "stopRecMode" in api_list[0]:
            remote_api.stopRecMode()

if __name__ == "__main__":
    try:
        main()
        print "fin"
    except KeyboardInterrupt:
        print "interrupted by user"