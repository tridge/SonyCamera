#!/usr/bin/env python
'''
Simple script to test Sony camera WiFi interface. Tested on a QX10.

Started by Andrew Tridgell October 2014
Released under GNU GPLv3 or later
'''

import requests, json, time
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

def show_version():
    '''show API version'''
    print(make_call("camera",
                    {"method": "getApplicationInfo",
                     "params": [],
                     "id": 1,
                     "version": "1.0"}))

def take_photo(filename):
    '''take a photo and put result in filename'''
    response = make_call("camera",
                         {"method": "actTakePicture",
                          "params": [],
                          "id": 1,
                          "version": "1.0"})
    if 'result' in response:
        url = response['result'][0][0]
        req = requests.request('GET', url)
        open(filename, 'w').write(req.content)

def frame_time(t):
    '''return a time string for a filename with 0.01 sec resolution'''
    # round to the nearest 100th of a second
    t += 0.005
    hundredths = int(t * 100.0) % 100
    return "%s%02uZ" % (time.strftime("%Y%m%d%H%M%S", time.gmtime(t)), hundredths)

while True:
    filename = 'photo%s.jpg' % frame_time(time.time())
    take_photo(filename)
    print(filename)
