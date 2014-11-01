#!/usr/bin/env python
'''
Simple script to test Sony camera WiFi interface. Tested on a QX10.

Started by Andrew Tridgell October 2014
Released under GNU GPLv3 or later
'''

import requests, json, time, sys
from optparse import OptionParser

# parse command line options
parser = OptionParser()
parser.add_option("--camera", help="camera IP", default="http://10.0.0.1:10000")

(opts, args) = parser.parse_args()

def make_call(service, payload):
    '''make a call to camera'''
    url = "%s/sony/%s" % (opts.camera, service)
    headers = {"content-type": "application/json"}
    data = json.dumps(payload)
    response = requests.post(url,
                             data=data,
                             headers = headers).json()
    return response

def simple_call(method, target="camera", params=[], id=1, version="1.0"):
    '''make a simple call'''
    print("Calling %s" % method)
    return make_call(target,
                     { "method" : method,
                       "params" : params,
                       "id"     : id,
                       "version" : version })

def show_version():
    '''show API version'''
    return simple_call("getApplicationInfo")

def get_available_shutter_speeds():
    '''show shutter speeds'''
    return simple_call("getAvailableShutterSpeed")

def set_shutter_speed(speed):
    '''set shutter speed'''
    return simple_call("setShutterSpeed", params=[speed])

def enable_methods():
    '''enable some more API methods. Thanks to https://github.com/erik-smit/sony-camera-api for the approach!'''
    import hashlib, base64
    response = simple_call("actEnableMethods",
                           target="accessControl",
                           params=[{"developerID" : "",
                                    "developerName" : "",
                                    "methods" : "",
                                    "sg" : ""}])
    dg = response['result'][0]['dg']
    key="90adc8515a40558968fe8318b5b023fdd48d3828a2dda8905f3b93a3cd8e58dc" + dg
    h = hashlib.sha256()
    h.update(key)
    digest = h.digest()
    sg = base64.b64encode(digest)
    response = simple_call("actEnableMethods",
                           target="accessControl",
                           params=[{"developerID" : "7DED695E-75AC-4ea9-8A85-E5F8CA0AF2F3",
                                    "developerName" : "Sony Corporation",
                                    "methods" : "camera/setFlashMode:camera/getFlashMode:camera/getSupportedFlashMode:camera/getAvailableFlashMode:camera/setExposureCompensation:camera/getExposureCompensation:camera/getSupportedExposureCompensation:camera/getAvailableExposureCompensation:camera/setSteadyMode:camera/getSteadyMode:camera/getSupportedSteadyMode:camera/getAvailableSteadyMode:camera/setViewAngle:camera/getViewAngle:camera/getSupportedViewAngle:camera/getAvailableViewAngle:camera/setMovieQuality:camera/getMovieQuality:camera/getSupportedMovieQuality:camera/getAvailableMovieQuality:camera/setFocusMode:camera/getFocusMode:camera/getSupportedFocusMode:camera/getAvailableFocusMode:camera/setStillSize:camera/getStillSize:camera/getSupportedStillSize:camera/getAvailableStillSize:camera/setBeepMode:camera/getBeepMode:camera/getSupportedBeepMode:camera/getAvailableBeepMode:camera/setCameraFunction:camera/getCameraFunction:camera/getSupportedCameraFunction:camera/getAvailableCameraFunction:camera/setLiveviewSize:camera/getLiveviewSize:camera/getSupportedLiveviewSize:camera/getAvailableLiveviewSize:camera/setTouchAFPosition:camera/getTouchAFPosition:camera/cancelTouchAFPosition:camera/setFNumber:camera/getFNumber:camera/getSupportedFNumber:camera/getAvailableFNumber:camera/setShutterSpeed:camera/getShutterSpeed:camera/getSupportedShutterSpeed:camera/getAvailableShutterSpeed:camera/setIsoSpeedRate:camera/getIsoSpeedRate:camera/getSupportedIsoSpeedRate:camera/getAvailableIsoSpeedRate:camera/setExposureMode:camera/getExposureMode:camera/getSupportedExposureMode:camera/getAvailableExposureMode:camera/setWhiteBalance:camera/getWhiteBalance:camera/getSupportedWhiteBalance:camera/getAvailableWhiteBalance:camera/setProgramShift:camera/getSupportedProgramShift:camera/getStorageInformation:camera/startLiveviewWithSize:camera/startIntervalStillRec:camera/stopIntervalStillRec:camera/actFormatStorage:system/setCurrentTime",
                                    "sg" : sg}])
    print(response)
    
    

def take_photo(filename):
    '''take a photo and put result in filename'''
    response = simple_call("actTakePicture")
    if 'result' in response:
        url = response['result'][0][0]
        req = requests.request('GET', url)
        open(filename, 'w').write(req.content)
        return True
    return False

def frame_time(t):
    '''return a time string for a filename with 0.01 sec resolution'''
    # round to the nearest 100th of a second
    t += 0.005
    hundredths = int(t * 100.0) % 100
    return "%s%02uZ" % (time.strftime("%Y%m%d%H%M%S", time.gmtime(t)), hundredths)

def continuous_capture():
    '''capture photos continuously'''
    while True:
        filename = 'photo%s.jpg' % frame_time(time.time())
        if take_photo(filename):
            print(filename)

enable_methods()
print(show_version())
print(get_available_shutter_speeds())
print(set_shutter_speed("1/2"))
print(simple_call("getShutterSpeed"))
print(simple_call("getAvailableShutterSpeed"))
print(simple_call("getAvailableApiList"))
print(simple_call("getSupportedExposureMode"))
print(simple_call("getAvailableExposureMode"))
print(simple_call("getAvailableCameraFunction"))
print(simple_call("getAvailableShootMode"))
print(simple_call("getStorageInformation"))
print(simple_call("getAvailableExposureMode"))
print(simple_call("getExposureMode"))
print(simple_call("setExposureMode", params=['Program Auto']))
print(simple_call("getExposureMode"))
print(simple_call("getAvailableShutterSpeed"))
print(simple_call("getSupportedShutterSpeed"))
print(simple_call("getSupportedStillSize"))
print(simple_call("getAvailableStillSize"))
print(simple_call("setStillSize", params=['4:3', '18M']))

try:
    continuous_capture()
except KeyboardInterrupt:
    pass
