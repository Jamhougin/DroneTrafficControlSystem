# -*- coding: UTF-8 -*-

import pickle
import math
import time
import threading
import multiprocessing
from threading import Thread
from AbstractDrone import AbstractDrone
from VirtualDrone import VirtualDrone
from Location import Location
from Flight import Flight

#Global thread variables used to kill threads
takeoffThread = False
moveThread = False
altitudeThread = False
hoverThread = False
landThread = False

def MoveDrone(drone, flight, dronelist, lat, lon):
    global moveThread
    drone.destination_latitude = lat
    drone.destination_longitude = lon
    #Following variable needed to know when to stop
    distancetodest = getdistancetodestination(drone, flight)
    
    #While destination latitude and longitude not reached and distance from origin to destination not exceeded
    while ((drone.getdistancetoposition(drone.home_latitude, drone.home_longitude) <= distancetodest)):
        canmove = True
        for d in dronelist:
            if (CollisionDetection(drone, d) and d.getdronestate() != "Grounded" and flight.flight_drone != d.drone_id and drone.gethomelatitude()>d.gethomelatitude() and drone.gethomelongitude()>d.gethomelongitude()):
                canmove = False
                break
        if(canmove):
            drone.moveto(flight.getdestinationlongitude(), flight.getdestinationlatitude(), drone.getaltitude(), .0001)
            time.sleep(1)
        else:
            ChangeAltitude(drone,drone.getaltitude()-10)
            for i in range(10):
                Hover(drone)
            ChangeAltitude(drone,drone.getaltitude()+10)
            time.sleep(1)
    drone.sethomelatitude(drone.getcurrentlatitude())
    drone.sethomelongitude(drone.getcurrentlongitude())

def ChangeAltitude(drone,newalt):
    global altitudeThread
    while drone.getaltitude() != newalt:
        if (newalt < drone.getaltitude()):
            drone.changealtitude(drone.getaltitude() - 1)
            drone.setbatterychange(.225)
            time.sleep(.5)
        elif (newalt > drone.getaltitude()):
            drone.changealtitude(drone.getaltitude() + 1)
            drone.setbatterychange(.225)
            time.sleep(.5)
    #Hover when change complete
    '''while altitudeThread:
        drone.hover()
        drone.setbatteryinflight()
        time.sleep(1)'''

def Hover(Drone):
    global hoverThread
    global takeoffThread
    while hoverThread or takeoffThread:
        Drone.hover()
        Drone.setbatteryinflight()
        time.sleep(1)

#Function to land the drone
def LandDrone(Drone):
    #global landThread
    while Drone.getaltitude() != 0:
        Drone.changealtitude(Drone.getaltitude() - 1)
        Drone.setbatterychange(.225)
        time.sleep(.5)
    Drone.setdronestate("Grounded")

def getdistancetodestination(drone, flight):
        #Get travel distance from point to point
        #Formula adopted from top answer and source of answer:
        #https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
        #http://www.movable-type.co.uk/scripts/latlong.html
        
        radius = 6371 #Radius in km of Earth

        deg_latitude = math.radians(flight.getdestinationlatitude() - drone.current_latitude)
        deg_longitude = math.radians(flight.getdestinationlongitude() - drone.current_longitude)

        #a = Square of half the chord length between two points
        a = math.sin(deg_latitude/2) * math.sin(deg_latitude/2) + math.cos(math.radians(drone.current_latitude)) * math.cos(math.radians(flight.getdestinationlatitude())) * math.sin(deg_longitude/2) * math.sin(deg_longitude/2)
        #c = Angular distance in radians
        c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        d = radius * c

        return d
        
def getdistancetoposition(drone,poslat,poslon):
        #Get travel distance from point to point
        #Formula adopted from top answer and source of answer:
        #https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
        #http://www.movable-type.co.uk/scripts/latlong.html
        
        radius = 6371 #Average Radius in km of Earth

        deg_latitude = math.radians(poslat - drone.current_latitude)
        deg_longitude = math.radians(poslon - drone.current_longitude)

        #a = Square of half the chord length between two points
        a = math.sin(deg_latitude/2) * math.sin(deg_latitude/2) + math.cos(math.radians(drone.current_latitude)) * math.cos(math.radians(drone.destination_latitude)) * math.sin(deg_longitude/2) * math.sin(deg_longitude/2)
        #c = Angular distance in radians
        c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        d = radius * c

        return d
        
def getdistancetodrone(drone,otherdrone):
        #Get travel distance from point to point
        #Formula adopted from top answer and source of answer:
        #https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
        #http://www.movable-type.co.uk/scripts/latlong.html
        
        radius = 6371 #Average Radius in km of Earth

        deg_latitude = math.radians(otherdrone.current_latitude - drone.current_latitude)
        deg_longitude = math.radians(otherdrone.current_longitude - drone.current_longitude)

        #a = Square of half the chord length between two points
        a = math.sin(deg_latitude/2) * math.sin(deg_latitude/2) + math.cos(math.radians(drone.current_latitude)) * math.cos(math.radians(otherdrone.current_latitude)) * math.sin(deg_longitude/2) * math.sin(deg_longitude/2)
        #c = Angular distance in radians
        c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        d = radius * c

        return d

def TakeOffFlyLand(drone, flight, dronelist):
    drone.takeoff()
    destlat = flight.getdestinationlatitude()
    destlong = flight.getdestinationlongitude()
    
    ChangeAltitude(drone, 50)
    MoveDrone(drone, flight, dronelist, destlat, destlong,)
    LandDrone(drone)

    if drone.flying_state == "Grounded":
        flight.setflightcomplete(True) 

def CollisionDetection(drone, otherdrone):
    if (getdistancetodrone(drone,otherdrone)<=.02):
        return True
    else:
        return False    
            
            


