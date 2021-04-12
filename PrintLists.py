from save_load import *

def flight_list():
    flights = LoadFlightList()
    string = ""
    number = 1
    
    for flight in flights:
        string += str(number)
        string += ": "
        string += flight.getflightid()
        string += "Start Lat/Lon:"
        string += str(flight.getstartlatitude())
        string += "/"
        string += str(flight.getstartlongitude())
        string += " End Lat/Lon:"
        string += str(flight.getdestinationlatitude())
        string += "/"
        string += str(flight.getdestinationlongitude())
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
        string += str(location.getlocationlatitude())
        string += " Lon:"
        string += str(location.getlocationlongitude())
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
        string += str(drone.gethomelatitude())
        string += " Lon:"
        string += str(drone.gethomelongitude())
        string += "\n"
        number += 1
        
    return string
