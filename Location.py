# -*- coding: UTF-8 -*-

class Location():

    def __init__(self, name, latitude, longitude, altitude):
        self.location_name = name
        self.location_latitude = latitude
        self.location_longitude = longitude
        self.location_altitude = altitude
        
    def setlocationname(self, name):
        self.location_name = name
        
    def getlocationname(self):
        name = self.location_name
        return name
        
    def setlocationlatitude(self, latitude):
        self.location_latitude = latitude
        
    def getlocationlatitude(self):
        latitude = self.location_latitude
        return latitude
        
    def setlocationlongitude(self, longitude):
        self.location_longitude = longitude
        
    def getlocationlongitude(self):
        longitude = self.location_longitude
        return longitude
        
    def setlocationaltitude(self, altitude):
        self.location_altitude = altitude
        
    def getlocationaltitude(self):
        altitude = self.location_altitude
        return altitude
