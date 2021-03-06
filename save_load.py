# -*- coding: UTF-8 -*-


#Name:        James Hall
#Student No.: C00007006
#Institute:   Institute of Technology Carlow
#Project:     Drone Traffic Control System     
#Date:        April 2021 
#License:     GNU Affero General Public License v3.0

#save_load.py
"""
Used for functions relating to saving and loading Item Lists
"""
import pickle

def SaveDroneList(dronelist):
    """
    Saves List of drones using pickle.
    """
    with open("database//config.dronelist", "wb") as config_dronelist_file:
        pickle.dump(dronelist, config_dronelist_file)

def SaveLocationList(locationlist):
    """
    Saves List of locations using pickle
    """
    with open("database//config.locationlist", "wb") as config_locationlist_file:
        pickle.dump(locationlist, config_locationlist_file)

def SaveFlightList(flightlist):
    """
    Save List of flights using pickle
    """
    with open("database//config.flightlist", "wb") as config_flightlist_file:
        pickle.dump(flightlist, config_flightlist_file)

def LoadDroneList():
    """
    Loads list of drones using pickle
    """
    with open("database//config.dronelist", "rb") as drones:
        dronelist = pickle.load(drones)
        return dronelist

def LoadLocationList():
    """
    Loads list of locations using pickle
    """
    with open("database//config.locationlist", "rb") as locations:
        locationlist = pickle.load(locations)
        return locationlist

def LoadFlightList():
    """
    Loads list of flights using pickle
    """
    with open("database//config.flightlist", "rb") as flights:
        flightlist = pickle.load(flights)
        return flightlist
