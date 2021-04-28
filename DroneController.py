# -*- coding: UTF-8 -*-

'''
Name:        James Hall
Student No.: C00007006
Institute:   Institute of Technology Carlow
Project:     Drone Traffic Control System     
Date:        April 2021 
License:     GNU Affero General Public License v3.0

Drone Controller
'''

import pickle
import math
import time
import threading
import multiprocessing
from threading import Thread, Lock
from AbstractDrone import AbstractDrone
from VirtualDrone import VirtualDrone
from Location import Location
from Flight import Flight
from save_load import *

#Global thread variables used to kill threads
takeoffThread = False
moveThread = False
altitudeThread = False
hoverThread = False
landThread = False
data_lock = Lock()

def MoveDrone(drone, flight, dronelist, lat, lon, locations):
    global moveThread
    drone.destination_latitude = lat
    drone.destination_longitude = lon
    #Following variable needed to know when to stop
    distancetodest = getdistancetodestination(drone, flight)
    
    #While destination latitude and longitude not reached and distance from origin to destination not exceeded
    while ((drone.getdistancetoposition(float(drone.home_latitude), float(drone.home_longitude)) <= distancetodest)):
        canmove = True
        for d in dronelist:
            if (CollisionDetection(drone, d) and d.getdronestate() != "Grounded" and flight.flight_drone != d.drone_id and float(drone.gethomelatitude())>float(d.gethomelatitude()) and float(drone.gethomelongitude())>float(d.gethomelongitude())):
                canmove = False
                break
        if(canmove and flight.getflightabort() == False):
            drone.moveto(flight.getdestinationlongitude(), flight.getdestinationlatitude(), drone.getaltitude(), .0001)
            time.sleep(1)
        elif(canmove and flight.getflightabort() == True):
            newlat, newlon = findnearestlocation(drone, locations)
            drone.sethomelatitude(drone.getcurrentlatitude())
            drone.sethomelongitude(drone.getcurrentlongitude())
            flight.setdestinationlatitude(newlat)
            drone.setdestinationlatitude(newlat)
            flight.setdestinationlongitude(newlon)
            drone.setdestinationlongitude(newlon)
            drone.moveto(flight.getdestinationlongitude(), flight.getdestinationlatitude(), drone.getaltitude(), .0001)
            distancetodest = getdistancetodestination(drone, flight)
            flight.setflightabort(False)
            time.sleep(1)
        else:
            ChangeAltitude(drone,drone.getaltitude()-10)
            for i in range(10):
                Hover(drone)
            ChangeAltitude(drone,drone.getaltitude()+10)
            time.sleep(1)
    drone.sethomelatitude(float(drone.getcurrentlatitude()))
    drone.sethomelongitude(float(drone.getcurrentlongitude()))

def ChangeAltitude(drone,newalt):
    global altitudeThread
    while drone.getaltitude() != newalt:
        if (newalt < drone.getaltitude()):
            drone.setdronestate("Descending")
            drone.changealtitude(drone.getaltitude() - 1)
            drone.setbatterychange(.225)
            time.sleep(.5)
        elif (newalt > drone.getaltitude()):
            drone.setdronestate("Ascending")
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
    #while Drone.getaltitude() != 0:
    #    Drone.changealtitude(Drone.getaltitude() - 1)
    #    Drone.setbatterychange(.225)
    #    time.sleep(.5)
    ChangeAltitude(Drone,0)
    print("Drone Landed: ", Drone.drone_id)
    Drone.setdronestate("Grounded")

def getdistancetodestination(drone, flight):
        #Get travel distance from point to point
        #Formula adopted from top answer and source of answer:
        #https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
        #http://www.movable-type.co.uk/scripts/latlong.html
        
        radius = 6371 #Radius in km of Earth

        deg_latitude = math.radians(float(flight.getdestinationlatitude()) - float(drone.current_latitude))
        deg_longitude = math.radians(float(flight.getdestinationlongitude()) - float(drone.current_longitude))

        #a = Square of half the chord length between two points
        a = math.sin(deg_latitude/2) * math.sin(deg_latitude/2) + math.cos(math.radians(float(drone.current_latitude))) * math.cos(math.radians(float(flight.getdestinationlatitude()))) * math.sin(deg_longitude/2) * math.sin(deg_longitude/2)
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

        deg_latitude = math.radians(poslat - float(drone.current_latitude))
        deg_longitude = math.radians(poslon - float(drone.current_longitude))

        #a = Square of half the chord length between two points
        a = math.sin(deg_latitude/2) * math.sin(deg_latitude/2) + math.cos(math.radians(float(drone.current_latitude))) * math.cos(math.radians(float(drone.destination_latitude))) * math.sin(deg_longitude/2) * math.sin(deg_longitude/2)
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

        deg_latitude = math.radians(float(otherdrone.current_latitude) - float(drone.current_latitude))
        deg_longitude = math.radians(float(otherdrone.current_longitude) - float(drone.current_longitude))

        #a = Square of half the chord length between two points
        a = math.sin(deg_latitude/2) * math.sin(deg_latitude/2) + math.cos(math.radians(float(drone.current_latitude))) * math.cos(math.radians(float(otherdrone.current_latitude))) * math.sin(deg_longitude/2) * math.sin(deg_longitude/2)
        #c = Angular distance in radians
        c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        d = radius * c

        return d

def TakeOffFlyLand(drone, flight, dronelist, locationlist):
    drone.takeoff()
    destlat = flight.getdestinationlatitude()
    destlong = flight.getdestinationlongitude()
    
    ChangeAltitude(drone, 50)
    MoveDrone(drone, flight, dronelist, destlat, destlong, locationlist)
    LandDrone(drone)
    print(drone.drone_id, 'complete:', flight.getflightcomplete())
    flight.setflightcomplete(True)
    print(drone.drone_id, 'complete:', flight.getflightcomplete())
    with data_lock:
        flights = LoadFlightList()
        for f in flights:
            if f.getflightid() == flight.getflightid():
                print(f.getflightid())
                print(flight.getflightid())
                f.setflightcomplete(True)
                SaveDroneList(dronelist)
                SaveFlightList(flights)
                print('complete:', f.getflightcomplete())
                break

def CollisionDetection(drone, otherdrone):
    if ((getdistancetodrone(drone,otherdrone)<=.03) and (abs(drone.getaltitude()-otherdrone.getaltitude())<=9)):
        return True
    else:
        return False 

def findnearestlocation(drone, locations):
    
    newlocationlat = drone.getdestinationlatitude()
    newlocationlon = drone.getdestinationlongitude()
    
    for location in locations:
        if (getdistancetoposition(drone,float(location.getlocationlatitude()),float(location.getlocationlongitude())) < getdistancetoposition(drone,float(newlocationlat),float(newlocationlon))):
            newlocationlat = location.getlocationlatitude()
            newlocationlon = location.getlocationlongitude()
        
    return newlocationlat, newlocationlon
            


