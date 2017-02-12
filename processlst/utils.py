# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import urllib2, base64
import os
from osgeo import gdal,osr
import tarfile

class earthDataHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
    

def getHTTPdata(url,outFN,auth):
    username = auth[0]
    password = auth[1]
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)  
    cookieprocessor = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(earthDataHTTPRedirectHandler, cookieprocessor)
    urllib2.install_opener(opener) 
    r = opener.open(request)
    result = r.read()
    
    with open(outFN, 'wb') as f:
        f.write(result)


def writeArray2Tiff(data,lats,lons,outfile):
    Projection = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    xres = lons[1] - lons[0]
    yres = lats[1] - lats[0]

    ysize = len(lats)
    xsize = len(lons)

    ulx = lons[0] #- (xres / 2.)
    uly = lats[0]# - (yres / 2.)
    driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(outfile, xsize, ysize, 1, gdal.GDT_Float32)
    
    srs = osr.SpatialReference()
    if isinstance(Projection, basestring):        
        srs.ImportFromProj4(Projection)
    else:
        srs.ImportFromEPSG(Projection)        
    ds.SetProjection(srs.ExportToWkt())
    
    gt = [ulx, xres, 0, uly, 0, yres ]
    ds.SetGeoTransform(gt)
    
    outband = ds.GetRasterBand(1)
    outband.WriteArray(data)    
    ds.FlushCache()  
    
    ds = None

def folders(base):
    dataBase = os.path.join(base,'data')
    landsatDataBase = os.path.join(dataBase,'Landsat-8')
    asterDataBase = os.path.join(dataBase,'ASTER')
    landsatSR = os.path.join(landsatDataBase,'SR')
    if not os.path.exists(landsatSR):
        os.makedirs(landsatSR)
    landsatBT = os.path.join(landsatDataBase,'BT')
    if not os.path.exists(landsatBT):
        os.makedirs(landsatBT)
    landsatLST = os.path.join(landsatDataBase,'LST')
    if not os.path.exists(landsatLST):
        os.makedirs(landsatLST)
    asterEmissivityBase = os.path.join(asterDataBase,'asterEmissivity')
    if not os.path.exists(asterEmissivityBase):
        os.makedirs(asterEmissivityBase)
    landsatEmissivityBase = os.path.join(asterDataBase,'landsatEmissivity')
    if not os.path.exists(landsatEmissivityBase):
        os.makedirs(landsatEmissivityBase)
    ASTERmosaicTemp = os.path.join(asterDataBase,'mosaicTemp')    
    if not os.path.exists(ASTERmosaicTemp):
        os.makedirs(ASTERmosaicTemp)
    out = {'landsatLST':landsatLST,'landsatSR':landsatSR,'landsatBT':landsatBT,
    'asterEmissivityBase':asterEmissivityBase,'ASTERmosaicTemp':ASTERmosaicTemp,
    'landsatDataBase':landsatDataBase, 'landsatEmissivityBase':landsatEmissivityBase}
    return out

        
def untar(fname, fpath):

    tar = tarfile.open(fname)
    tar.extractall(path = fpath)
    tar.close()
    os.remove(fname)