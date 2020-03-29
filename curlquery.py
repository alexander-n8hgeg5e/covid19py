#!/usr/bin/env python3

from urllib.parse import quote,unquote
from time import gmtime
from datetime import datetime
from sys import path
path.append("/var/src")
from covid19py.utils import *
from subprocess import check_output,DEVNULL,PIPE
from json import loads
from os.path import exists
from sys import exit
from pprint import pformat

u5=['A00-A04']
u15=['A05-A14','A00-A04']
u35=['A15-A34','A05-A14','A00-A04']
u60=['A35-A59','A15-A34','A05-A14','A00-A04']
u80=['A60-A79','A35-A59','A15-A34','A05-A14','A00-A04']
ue80=['A80+']

#    where=(Meldedatum>timestamp '2020-03-01 22:59:59' AND NeuerFall IN(0, 1)) AND (IdLandkreis='09"
#    +'resultRecordCount=20&'
#    +" AND (Meldedatum>timestamp '2020-03-01 22:59:59')"

def curlcmd(landkreis_id = 9162):
    curlcmd =   [
                'curl',
                '--silent',
                'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/'
                +'query?f=json&'
                +'where='
                +quote  (
                        "IdLandkreis="+"'{:05}'".format(landkreis_id)
                        )
                +"&"
                +'returnGeometry=false&'
                +'spatialRel=esriSpatialRelIntersects&'
                +'outFields=*&'
                +'resultOffset=0&'
                +'cacheHint=true',
                '-H',
                'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
                '-H',
                'Accept: */*', '-H', 'Accept-Language: en-US,en;q=0.5',
                '--compressed',
                '-H',
                'Referer: https://npgeo-de.maps.arcgis.com/apps/opsdashboard/index.html',
                '-H',
                'Origin: https://npgeo-de.maps.arcgis.com',
                '-H',
                'Connection: keep-alive',
                '-H',
                'TE: Trailers'
                ]
    return curlcmd

def curlcmd_1(result_count=2000,objectid_range=None):
    if not objectid_range is None:
        objectid_lb = objectid_range[0]
        objectid_hb = objectid_range[-1]
        objectid_query_string = "((ObjectId >= "+str(objectid_lb)+")  AND (ObjectId <= "+str(objectid_hb)+"))"
    else:
        objectid_query_string=""
    max_result_count=2000
    curlcmd =   [
                'curl',
                '--silent',
                'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/'
                +'query?f=json&'
                +'where='
                +quote  (
                        objectid_query_string
                        )
                +"&"
                +'resultRecordCount='+str(min(max_result_count,result_count))+'&'
                +'returnGeometry=false&'
                +'spatialRel=esriSpatialRelIntersects&'
                +'outFields=*&'
                +'resultOffset=0&'
                +'cacheHint=true',
                '-H',
                'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
                '-H',
                'Accept: */*', '-H', 'Accept-Language: en-US,en;q=0.5',
                '--compressed',
                '-H',
                'Referer: https://npgeo-de.maps.arcgis.com/apps/opsdashboard/index.html',
                '-H',
                'Origin: https://npgeo-de.maps.arcgis.com',
                '-H',
                'Connection: keep-alive',
                '-H',
                'TE: Trailers'
                ]
    return curlcmd

def get(lk=load_kreise()):
    data=[]
    for i,j in lk:
        cmd=curlcmd(landkreis_id=i)
        print('fetching lk:'+str(i)+" ...")
        try:
            outp=check_output(cmd)
            d=loads(outp)['features']
            for thing in d:
                data.append(thing['attributes'])
        except KeyError:
            print(outp)
            print(cmd)
            print(unquote(cmd[2]))
            raise
    return data

def get_1(curlcmd=curlcmd_1,**curlcmd_kwargs):
    data=[]
    cmd=curlcmd(**curlcmd_kwargs)
    try:
        outp=check_output(cmd)
        d=loads(outp)['features']
        for thing in d:
            data.append(thing['attributes'])
    except KeyError:
        print(outp)
        print(cmd)
        print(unquote(cmd[2]))
        raise
    return data

def get_all(start_object_id=670153):
    data=[]
    start=start_object_id
    len0count=0
    i=0
    try:
        while len0count < 5:
            d=get_1(curlcmd=curlcmd_1,objectid_range=range(start+(i*2000),start+((i+1)*2000)))
            i+=1
            l=len(d)
            print("fetching part len="+str(l))
            if l==0:
                len0count+=1
            data+=d
    except:
        raise
    finally:
        return data

def load_data():
    if not exists("data"):
        inp=input("load data from internet and save to file \"data\" ? (y/n)")
        if inp == "y":
            data=get_all()
            with open('data',"wt") as f:
                f.write(pformat(data))
        else:
            print("quitting, no data")
            exit(0)
    else:
        with open('data') as f:
            data=eval(f.read())
    data=convtime(data)
    data=conv_lk_id(data)
    return data

def conv_lk_id(data):
    for d in data:
        if 'IdLandkreis' in d.keys():
            d['IdLandkreis']=int(d['IdLandkreis'])
    return data

def convtime(data):
    for d in data:
        if 'Meldedatum' in d.keys():
            tm_year, tm_mon, tm_mday, tm_hour, tm_min,tm_sec, tm_wday, tm_yday, tm_isdst=gmtime(d['Meldedatum']/1000)
            d['Meldedatum']=datetime(tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec)
    return data

# vim: set foldmethod=indent foldlevel=0 :
