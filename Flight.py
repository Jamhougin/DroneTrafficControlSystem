# -*- coding: UTF-8 -*-

class Flight():

    def __init__(self, name, startlatitude, startlongitude, destlatitude, destlongitude, drone, flightcomplete, flightabort):
        self.flight_id = name
        self.start_latitude = startlatitude
        self.start_longitude = startlongitude
        self.destination_latitude = destlatitude
        self.destination_longitude = destlongitude
        self.flight_drone = drone
        self.flight_complete = flightcomplete
        self.flight_abort = flightabort
        
    def setflightid(self, name):
        self.flight_id = name
        
    def getflightid(self):
        name = self.flight_id
        return name
        
    def setstartlatitude(self, startlatitude):
        self.start_latitude = startlatitude
        
    def getstartlatitude(self):
        startlatitude = self.start_latitude
        return startlatitude
        
    def setstartlongitude(self, startlongitude):
        self.start_longitude = startlongitude
        
    def getstartlongitude(self):
        startlongitude = self.start_longitude
        return startlongitude
        
    def setdestinationlatitude(self, destlatitude):
        self.destination_latitude = destlatitude
        
    def getdestinationlatitude(self):
        destlatitude = self.destination_latitude
        return destlatitude
        
    def setdestinationlongitude(self, destlongitude):
        self.destination_longitude = destlongitude
        
    def getdestinationlongitude(self):
        destlongitude = self.destination_longitude
        return destlongitude
        
    def setdrone(self, drone):
        self.flight_drone = drone
        
    def getdrone(self):
        drone = self.flight_drone
        return drone
        
    def setflightcomplete(self, flightcomplete):
        self.flight_complete = flightcomplete
        
    def getflightcomplete(self):
        flightcomplete = self.flight_complete
        return flightcomplete
        
    def setflightabort(self, flightabort):
        self.flight_abort = flightabort
        
    def getflightabort(self):
        flightabort = self.flight_abort
        return flightabort
