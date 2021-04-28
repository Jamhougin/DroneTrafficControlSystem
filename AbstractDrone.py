# -*- coding: UTF-8 -*-

'''
Name:        James Hall
Student No.: C00007006
Institute:   Institute of Technology Carlow
Project:     Drone Traffic Control System     
Date:        April 2021 
License:     GNU Affero General Public License v3.0

Abstract Drone class
'''
from abc import ABC, abstractmethod

class AbstractDrone(ABC):
    
    home_latitude = 0
    home_longtitude = 0
    current_latitude = 0
    current_longtitude = 0
    destination_latitude = 0
    destination_longtitude = 0
    altitude = 0
    battery = 100
    speed = 0
    flying_state = "Grounded"
    drone_id = 0
    drone_type = "virtual"
    heading = 0
    
    @abstractmethod
    def takeoff(self):
        pass

    @abstractmethod
    def hover(self):
        pass

    @abstractmethod
    def moveto(self):
        pass

    @abstractmethod
    def changealtitude(self):
        pass

    @abstractmethod
    def land(self):
        pass

    @abstractmethod
    def getgpsposition(self):
        pass

    @abstractmethod
    def setdronestate(self, state):
        pass

    @abstractmethod
    def getdronestate(self):
        pass

    @abstractmethod
    def setbatteryinflight(self):
        pass

    @abstractmethod
    def setbatterytotal(self, percent):
        pass

    @abstractmethod
    def setbatterychange(self, percent):
        pass

    @abstractmethod
    def getbattery(self):
        pass

    @abstractmethod
    def sethomelatitude(self,lat):
        pass

    @abstractmethod
    def gethomelatitude(self):
        pass

    @abstractmethod
    def setdestinationlatitude(self,lat):
        pass

    @abstractmethod
    def getdestinationlatitude(self):
        pass

    @abstractmethod
    def setdestinationlongitude(self,lon):
        pass

    @abstractmethod
    def getdestinationlongitude(self):
        pass

    @abstractmethod
    def setcurrentlatitude(self,lat):
        pass

    @abstractmethod
    def getcurrentlatitude(self):
        pass

    @abstractmethod
    def setcurrentlongitude(self,lon):
        pass

    @abstractmethod
    def getcurrentlongitude(self):
        pass

    @abstractmethod
    def getdistancetodestination(self):
        pass

    @abstractmethod
    def getdistancetoposition(self):
        pass

    @abstractmethod
    def createvector(self):
        pass

    @abstractmethod
    def getvectorlatitude(self):
        pass

    @abstractmethod
    def getvectorlongitude(self):
        pass

    @abstractmethod
    def updatecurrentposition(self):
        pass

    @abstractmethod
    def getbearing(self, startlat, startlong, destlat, destlong):
        pass

    @abstractmethod        
    def getdronetype(self):
        pass

    @abstractmethod        
    def setdronetype(self, dronetype):
        pass

