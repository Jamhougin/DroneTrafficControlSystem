# -*- coding: UTF-8 -*-


#Name:        James Hall
#Student No.: C00007006
#Institute:   Institute of Technology Carlow
#Project:     Drone Traffic Control System     
#Date:        April 2021 
#License:     GNU Affero General Public License v3.0
"""
Used to store functions for printing drone/location/flight lists
"""

from save_load import *

def flight_list():
    flights = LoadFlightList()
    string = ""
    number = 1
    
    for flight in flights:
        string += str(number)
        string += ": "
        string += flight.getflightid()
        string += "  Start Lat/Lon:"
        string += str(round(flight.getstartlatitude(), 4))
        string += "/"
        string += str(round(flight.getstartlongitude(), 4))
        string += "  End Lat/Lon:"
        string += str(round(flight.getdestinationlatitude(), 4))
        string += "/"
        string += str(round(flight.getdestinationlongitude(), 4))
        string += " Drone:"
        string += flight.getdrone()
        string += " Complete:"
        string += str(flight.getflightcomplete())
        string += "\n"
        number += 1
        
    return string 

def location_list():
    locations = LoadLocationList()
    string = ""
    number = 1
    
    for location in locations:
        string += str(number)
        string += ": "
        string += location.getlocationname()
        string += " Lat:"
        string += str(round(location.getlocationlatitude(),4))
        string += " Lon:"
        string += str(round(location.getlocationlongitude(),4))
        string += "\n"
        number += 1
        
    return string
    
def drone_list():
    drones = LoadDroneList()
    string = ""
    number = 1
    
    for drone in drones:
        string += str(number)
        string += ": Name:"
        string += drone.drone_id
        string += " Lat:"
        string += str(round(drone.gethomelatitude(),4))
        string += " Lon:"
        string += str(round(drone.gethomelongitude(),4))
        string += "\n"
        number += 1
        
    return string
