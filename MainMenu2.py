# -*- coding: UTF-8 -*-


#Name:        James Hall
#Student No.: C00007006
#Institute:   Institute of Technology Carlow
#Project:     Drone Traffic Control System     
#Date:        April 2021 
#License:     GNU Affero General Public License v3.0
"""
Original command line script #deprecated
"""

import pickle
import math
import time
import threading
import multiprocessing
import DroneController
from threading import Thread
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

##########CRUD Drones methods
def CreateDrone(dronelist, locationlist):
    dronename = input("\nEnter drone name:")
    dronetype = input("\nEnter drone type:")
    homelocation = input("\n Enter drone home location:")
    for i in range(len(locationlist)):
        if locationlist[i].getlocationname() == homelocation:
            homelatitude = locationlist[i].getlocationlatitude()
            homelongitude = locationlist[i].getlocationlongitude()
    
    dronelist.append(VirtualDrone(dronename, dronetype, homelatitude, homelongitude, homelatitude, homelongitude, 0, 100, 0, "Grounded", 0))

def ViewSystemDrones(dronelist):
    for i in range(len(dronelist)):
        print(" " + dronelist[i].drone_id +"," + dronelist[i].getdronetype() + " Lat:" + str(dronelist[i].current_latitude) + " Lon:" + str(dronelist[i].current_longitude) + " State:" + str(dronelist[i].getdronestate()) + " Altitude:" + str(dronelist[i].getaltitude()) + "\n")
        
def ViewActiveDrones(dronelist):
    for i in range(len(dronelist)):
        if dronelist[i].flying_state != "Grounded":
            print(" " + dronelist[i].drone_id + " Lat:" + str(dronelist[i].current_latitude) + " Lon:" + str(dronelist[i].current_longitude) + "\n")

def RemoveDrone(dronelist):
    for i in range(len(dronelist)):
        print(" " + dronelist[i].drone_id)
    dronename = input("\nEnter drone name to remove:") 
    
    for i in range(len(dronelist)):
        if dronelist[i].drone_id == dronename:
            dronelist.remove(dronelist[i])
            print(" " + dronename + " removed from Drone List")
            break

##########CRUD Location methods
def CreateLocation(locationlist):
    locationname = input("\nEnter Location Name:")
    locationlatitude = float(input("\nEnter Location Latitude:"))
    locationlongitude = float(input("\nEnter Location Longitude:"))
    
    locationlist.append(Location(locationname, locationlatitude, locationlongitude, 0))

def ViewLocations(locationlist):
    for i in range(len(locationlist)):
        print(" " + locationlist[i].getlocationname() + " Lat:" + str(locationlist[i].getlocationlatitude()) + " Lon:" + str(locationlist[i].getlocationlongitude()) + "\n")

def RemoveLocation(locationlist):
    for i in range(len(locationlist)):
        print(" " + locationlist[i].getlocationname())
    locationname = input("\nEnter location name to remove:") 
    
    for i in range(len(locationlist)):
        if locationlist[i].getlocationname() == locationname:
            locationlist.remove(locationlist[i])
            print(" " + locationname + " removed from Locations")
            break
            
##########CRUD Flight methods
def CreateFlight(flightlist, locationlist, dronelist):
    flightname = input("\nEnter Flight Name:")
    dronename = input("\nEnter Drone Name:")

    for i in range(len(dronelist)):
        if dronelist[i].drone_id == dronename:
            drone = dronelist[i].drone_id
            startlatitude = dronelist[i].gethomelatitude()
            startlongitude = dronelist[i].gethomelongitude()

    destlocation = input("\nEnter Destination Location:")

    for i in range(len(locationlist)):
        if locationlist[i].getlocationname() == destlocation:
            destlatitude = locationlist[i].getlocationlatitude()
            destlongitude = locationlist[i].getlocationlongitude()
    
    flightlist.append(Flight(flightname, startlatitude, startlongitude, destlatitude, destlongitude, drone, False))

def ViewFlights(flightlist):
    for i in range(len(flightlist)):
        print(" " + flightlist[i].getflightid() + " Start Lat:" + str(flightlist[i].getstartlatitude()) + " Start Lon:" + str(flightlist[i].getstartlongitude()) + " Dest Lat:" + str(flightlist[i].getdestinationlatitude()) + " Dest Lon:" + str(flightlist[i].getdestinationlongitude()) + " Complete:" + str(flightlist[i].getflightcomplete()) +"\n")

def RemoveFlight(flightlist):
    for i in range(len(flightlist)):
        print(" " + flightlist[i].getflightid())
    flightname = input("\nEnter location name to remove:") 
    
    for i in range(len(flightlist)):
        if flightlist[i].getflightid() == flightname:
            flightlist.remove(flightlist[i])
            print(" " + flightname + " removed from Flights")
            break

##########BeginFlight uses TakeOffFlyLand as thread                     
def BeginFlight(flightlist, locationlist, dronelist, threads):
    takeoffThread = False
    global moveThread
    altitudeThread = False
    hoverThread = False
    global landThread
    
    for i in range(len(flightlist)):
        print(" " + flightlist[i].getflightid())
    flightname = input("\nEnter flight you want to start:")

    for i in range(len(flightlist)):
        if flightlist[i].getflightid() == flightname:
            for j in range(len(dronelist)):
                if flightlist[i].getdrone() == dronelist[j].drone_id:
                    threads.append(Thread(target = DroneController.TakeOffFlyLand,  args = (dronelist[j], flightlist[i],dronelist)))
                    threads[len(threads)-1].start()
                    return None

##########Main Menu
def MainMenu():

    DronesList = LoadDroneList()
    LocationList = LoadLocationList()
    FlightList = LoadFlightList()
    
    threads = []
    
    loop_true = True

    
    '''init of game;
   
    game loop start
        check for inputs
        //update all game objects
        for d in drones
            d.moveTo
        for a certain frame rate
            render all game objects
    end loop'''
   
    
    while loop_true == True:
        print(" Enter Number corresponding to your choice:\n")
        print(" 1 Create Drone (Must have location to add to home)")
        print(" 2 View System Drones")
        print(" 3 View Active Drones")
        print(" 4 Remove Drone")
        print(" 5 Create Location")
        print(" 6 View Locations")
        print(" 7 Remove Location")
        print(" 8 Create Flight (Must have minimum 2 locations and 1 drone created)")
        print(" 9 View Flights")
        print(" 10 Cancel Flight")
        print(" 11 Begin Flight")
        print(" 12 exit program")
        
        loopinput = int(input("\nEnter number choice:"))
        
        if loopinput == 12:
            SaveDroneList(DronesList)
            SaveLocationList(LocationList)
            SaveFlightList(FlightList)
            break
        elif loopinput == 1:
            CreateDrone(DronesList, LocationList)
        elif loopinput == 2:
            ViewSystemDrones(DronesList)
        elif loopinput == 3:
            ViewActiveDrones(DronesList)
        elif loopinput == 4:
            RemoveDrone(DronesList)
        elif loopinput == 5:
            CreateLocation(LocationList)
        elif loopinput == 6:
            ViewLocations(LocationList)
        elif loopinput == 7:
            RemoveLocation(LocationList)
        elif loopinput == 8:
            CreateFlight(FlightList, LocationList, DronesList)
        elif loopinput == 9:
            ViewFlights(FlightList)
        elif loopinput == 10:
            RemoveFlight(FlightList)
        elif loopinput == 11:
            BeginFlight(FlightList, LocationList, DronesList, threads)
        

if __name__ == "__main__":
    
    M = Thread(target = MainMenu)
    M.start()



