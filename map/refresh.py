from map.models import Boat
from string import capwords
import xml.etree.ElementTree as ET
import urllib2
from datetime import datetime

def updateBoat(row, pin):
        mmsi = row.get('MMSI','')
        name = capwords(row.get('SHIPNAME','<unknown>'))
        tpname = row.get('TPNAME','')
        timestamp = row.get('TIMESTAMP',datetime.utcnow().isoformat())
        lng = row['LON']
        lat = row['LAT']
        try:
            if mmsi != '':
                b = Boat.objects.get(mmsi=mmsi)
            elif tpname != '':
                b = Boat.objects.get(tpname=tpname)
            else:
                b = Boat.objects.get(name=name)
            if b.last_fix is not None:
                if b.last_fix == '':
                    last_fix = datetime(2013,4,1)
                else:
                    last_fix = datetime.strptime(b.last_fix, "%Y-%m-%dT%H:%M:%S")
            else:
                last_fix = datetime(2013,4,1)
            new_fix = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
            if last_fix < new_fix:
                b.last_fix = new_fix.isoformat()
                b.lng = lng
                b.lat = lat
                if b.pin != 'tkIcon':
                    b.pin = pin
                b.save()
        except Boat.DoesNotExist:
            b = Boat.objects.create(name=name, tpname=tpname, mmsi=mmsi, lat=lat, lng=lng, last_fix=timestamp, pin=pin)
            b.save()

# <POS><row TIMESTAMP="2013-05-12T19:25:00" STATUS="99" COURSE="0" SPEED="0" LON="-5.065115" LAT="50.154209" MMSI="235014887"/></POS>
def mt(key):
    MT_URL="http://services.marinetraffic.com/api/exportvessels/"+key+"/timespan:60"
    r = urllib2.urlopen(MT_URL)
    xml = r.read()
    root = ET.fromstring(xml)
    need_extended = False
    for n in root:
        name = capwords(n.attrib.get('SHIPNAME',''))
        if name == '':
            need_extended = True
    if need_extended:
        r = urllib2.urlopen(MT_URL+"/msgtype:extended")
        xml = r.read()
        root = ET.fromstring(xml)
    for n in root:
        updateBoat(n.attrib, 'mtIcon')

#<?xml version="1.0" encoding="UTF-8"?><publisher><map-params enable-map-type="true" enable-overview="false" enable-pan="true" enable-scale="true"/><devices history-opacity="0.8" history-thickness="4"><device history-colour="#EC5252" icon-anchor-x="-1" icon-anchor-y="-1" icon-height="-1" icon-url="" icon-width="-1" label-content="Barrys Boat Lake District" name="Barrys Boat Lake District"><loc lat="54.235521" lng="-2.726719" time="Wed 15/05/13 17:05:47"/></device></devices></publisher>
def trackaphone(key):
    r = urllib2.urlopen("http://trackaphone.co.uk/callback/publish?id="+key)
    xml = r.read()
    root = ET.fromstring(xml)
    for n in root[1]:
	data = {}
        device = n.attrib
        loc = n[0].attrib
        tpname = device['name']
        data['SHIPNAME'] = capwords(tpname.split(' - ')[0])
        data['TPNAME'] = tpname
        data['LAT']  = loc['lat']
        data['LON'] = loc['lng']
        data['TIMESTAMP'] = datetime.strptime(loc['time'], "%a %d/%m/%y %H:%M:%S").isoformat()
        updateBoat(data, 'tpIcon')

# if a boat is linked to another boat. Give it nearly the same lat/lng
def tokens():
    boats = Boat.objects.all()
    for b in boats:
        if b.link != '':
            host = Boat.objects.get(name=b.link)
            b.lat=host.lat + 0.001
            b.lng=host.lng
            b.last_fix=host.last_fix
            b.save()
