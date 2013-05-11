from map.models import Boat
import xml.etree.ElementTree as ET
import urllib2

class TBoat:
    def __init__(self, name=None):
        if name is None:
            self.name=''
            self.image=''
            self.popup=''
        else:
            try:
                b = Boat.objects.get(tpname=name)
                self.name = b.name
                self.image = b.image
                self.popup='<b>'+b.name+'</b>'
                if b.image != '':
                    self.popup = self.popup + "</br><img width='50' height='50' src='/map/static/map/"+b.image+"'/>"
            except Boat.DoesNotExist:
                self.name = name
                self.image=''
                self.popup=''
        self.lat = 0.0
        self.lng = 0.0

def mt():
    r = urllib2.urlopen("http://services.marinetraffic.com/api/exportvessels/f0458439888b8e2eec63b8e8ae02b170d45790c4/timespan:5")
    xml = r.read()
    root = ET.fromstring(xml)
    return root 

