# -*- coding: utf-8 -*-

 



import urllib
import hashlib
import requests


ak='TjQqVP9gwVBe8eYFPEDVR5N4GhIeEWqH'
sk='juv2nIscPd11fzIgm77sqRpjOeFYoOFF'

#ak='ALgqDb6x5jN2QBefmRjpuICv'
#sk='ExBUL5iaO8z5gWPI0R03Z9FWLbhreKsI'

add='湖南省长沙市'#'西安市观象台'#百度大厦 only work
queryStr = '/geocoder/v2/?address='+add+'&output=json&ak='+ak  
encodedStr = urllib.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
rawStr = encodedStr + sk
snStr = hashlib.md5(urllib.quote_plus(rawStr)).hexdigest()

reqStr = 'http://api.map.baidu.com/geocoder/v2/?address='+add+'&output=json&ak='+ak+'&sn=' + snStr

r = requests.get(reqStr)
dictResult = r.json()
print (dictResult['result']['location'] if not dictResult['status'] else None)

