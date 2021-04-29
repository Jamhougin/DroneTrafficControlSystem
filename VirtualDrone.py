# -*- coding: UTF-8 -*-


#Name:        James Hall
#Student No.: C00007006
#Institute:   Institute of Technology Carlow
#Project:     Drone Traffic Control System     
#Date:        April 2021 
#License:     GNU Affero General Public License v3.0


import math
import time
import threading
from geographiclib.geodesic import Geodesic
from threading import Thread
from AbstractDrone import AbstractDrone


battery_drain = .055

class VirtualDrone(AbstractDrone):
    """   
    Virtual Drone class
    """
    def __init__(self, drone_id, dronetype, home_latitude, home_longitude, destination_latitude, destination_longitude, altitude, battery, speed, flying_state, heading):
        self.home_latitude = home_latitude
        self.home_longitude = home_longitude
        self.current_latitude = home_latitude
        self.current_longitude = home_longitude
        self.destination_latitude = destination_latitude
        self.destination_longitude = destination_longitude
        self.altitude = altitude
        self.battery = battery
        self.speed = speed
        self.flying_state = flying_state
        self.drone_id = drone_id
        self.drone_type = dronetype
        self.heading = heading

    def takeoff(self):
        self.altitude = 2
        self.flying_state = "Hovering"

    def hover(self):
        self.flying_state = "Hovering"

    def moveto(self, longitude, latitude, altitude, spe):
        self.altitude = altitude
        self.destination_latitude = latitude
        self.destination_longitude = longitude
        self.speed = spe
        self.createvector()#better name?
        self.updatecurrentposition()
        self.flying_state = "MovingTo"
        self.setbatteryinflight()

    def changealtitude(self, alt):
        self.altitude = alt
        #self.flying_state = "Changing Altitude"

    def land(self):
        self.altitude = 0
        self.flying_state = "Grounded"

    def getgpsposition(self):
        name = self.drone_id
        lat = float(self.current_latitude)
        lon = float(self.current_longitude)
        alt = self.altitude
        
        return name, lat, lon, alt

    def getaltitude(self):
        return self.altitude

    def setdronestate(self, state):
        self.flying_state = state

    def getdronestate(self):
        flystate = self.flying_state
        
        return flystate

    #Set/Get Battery
    def setbatteryinflight(self):
        global battery_drain
        # .055 is estimated drain on battery in flight per second as a %
        self.battery = (self.battery - battery_drain)

    def setbatterytotal(self, percent):
        self.battery = percent

    def setbatterychange(self, percent):
        self.battery = self.battery - percent

    def getbattery(self):
        return self.battery

    #Set/Get home lat and lon
    def sethomelatitude(self,lat):
        self.home_latitude = lat

    def gethomelatitude(self):
        return self.home_latitude

    def sethomelongitude(self,lon):
        self.home_longitude = lon

    def gethomelongitude(self):
        return self.home_longitude

    #Set/Get destination lat and lon
    def setdestinationlatitude(self,lat):
        self.destination_latitude = lat

    def getdestinationlatitude(self):
        return self.destination_latitude

    def setdestinationlongitude(self,lon):
        self.destination_longitude = lon

    def getdestinationlongitude(self):
        return self.destination_longitude

    #Set/Get current lat and lon
    def setcurrentlatitude(self,lat):
        self.current_latitude = lat

    def getcurrentlatitude(self):
        return float(self.current_latitude)

    def setcurrentlongitude(self,lon):
        self.current_longitude = lon

    def getcurrentlongitude(self):
        return float(self.current_longitude)

    def getdistancetodestination(self):
        #Get travel distance from point to point
        #Formula adopted from top answer and source of answer:
        #https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
        #http://www.movable-type.co.uk/scripts/latlong.html
        
        radius = 6371 #Radius in km of Earth

        deg_latitude = math.radians(self.destination_latitude -float(self.current_latitude))
        deg_longitude = math.radians(self.destination_longitude -float(self.current_longitude))

        #a = Square of half the chord length between two points
        a = math.sin(deg_latitude/2) * math.sin(deg_latitude/2) + math.cos(math.radians(self.current_latitude)) * math.cos(math.radians(self.destination_latitude)) * math.sin(deg_longitude/2) * math.sin(deg_longitude/2)
        #c = Angular distance in radians
        c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        d = radius * c

        return d

    def getdistancetoposition(self,poslat,poslon):
        #Get travel distance from point to point
        #Formula adopted from top answer and source of answer:
        #https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
        #http://www.movable-type.co.uk/scripts/latlong.html
        
        radius = 6371 #Average Radius in km of Earth

        deg_latitude = math.radians(poslat - float(self.current_latitude))
        deg_longitude = math.radians(poslon - float(self.current_longitude))

        #a = Square of half the chord length between two points
        a = math.sin(deg_latitude/2) * math.sin(deg_latitude/2) + math.cos(math.radians(float(self.current_latitude))) * math.cos(math.radians(float(self.destination_latitude))) * math.sin(deg_longitude/2) * math.sin(deg_longitude/2)
        #c = Angular distance in radians
        c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        d = radius * c

        return d

    def createvector(self):
        self.vectorlat = float(self.destination_latitude) -float(self.current_latitude)
        self.vectorlon = float(self.destination_longitude) -float(self.current_longitude)

        return self.vectorlat, self.vectorlon

    def getvectorlatitude(self):
        vectorlat = float(self.destination_latitude) - self.home_latitude

        return vectorlat

    def getvectorlongitude(self):
        vectorlon = float(self.destination_longitude )- self.home_longitude

        return vectorlon

    def updatecurrentposition(self):
        direction_length = math.sqrt(math.pow(self.getvectorlatitude(),2) + math.pow(self.getvectorlongitude(),2))
        normalised_vector_lat = self.getvectorlatitude() / direction_length
        normalised_vector_lon = self.getvectorlongitude() / direction_length
        self.current_latitude=float(self.current_latitude)+ (normalised_vector_lat*(self.speed*1))
        self.current_longitude =float(self.current_longitude) + (normalised_vector_lon*(self.speed*1))


    def getbearing(self, startlat, startlong, destlat, destlong):
        heading = Geodesic.WGS84.Inverse(startlat,startlong, destlat, destlong)["azi1"]
        return heading
        
    def getdronetype(self):
        return self.drone_type
        
    def setdronetype(self, dronetype):
        self.drone_type = dronetype


