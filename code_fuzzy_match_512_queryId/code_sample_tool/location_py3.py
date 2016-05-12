#!/usr/bin/env python3
import requests


"""http://www.cnblogs.com/aeropig/p/py_baidumap_location.html"""

def locatebyAddr(address, city=None):
    '''
    根据地址确定经纬度，城市为可选项
    '''
    mykey='A9f77664caa0b87520c3708a6750bbdb'
     
    items = {'output': 'json', 'ak': mykey, 'address': address}
    if city:
        items['city'] = city
    
    r = requests.get('http://api.map.baidu.com/geocoder/v2/', params=items)
    dictResult = r.json()
    return dictResult['result']['location'] if not dictResult['status'] else None


def locatebyLatLon(lat, lon, pois=0):
    '''
    根据经纬度确定地址
    '''
    items = {'location': str(lat) + ',' + str(lon), 'ak': 'A9f77664caa0b87520c3708a6750bbdb', 'output': 'json'}
    if pois:
        items['pois'] = 1
    r = requests.get('http://api.map.baidu.com/geocoder/v2/', params=items)
    dictResult = r.json()
    return dictResult['result'] if not dictResult['status'] else None


def main():
    #address = input('输入地址： ')
    #city = input('输入城市：（可选）')
    address="湖南省长沙市"#"西安市观象台"
    city=''#"西安市"
    result = locatebyAddr(address, city)
    print(result)

if __name__ == '__main__':
    main()
