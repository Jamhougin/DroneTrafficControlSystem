# -*- coding: UTF-8 -*-

'''
Name:        James Hall
Student No.: C00007006
Institute:   Institute of Technology Carlow
Project:     Drone Traffic Control System     
Date:        April 2021 
License:     GNU Affero General Public License v3.0

Bebop Drone class
'''

import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, moveBy, moveTo, Landing
from olympe.messages.ardrone3.PilotingState import GpsLocationChanged, FlyingStateChanged, moveToChanged, PositionChanged

DRONE_IP = "10.202.0.1"
def getgpsposition(drone):
    lat = drone.get_state(PositionChanged)["latitude"]
    lon = drone.get_state(PositionChanged)["longitude"]
    alt = drone.get_state(PositionChanged)["altitude"]

    print("Latitude:", lon)
    print("Longitude:", lat)
    print("Altitude:", alt)

def takeoff(drone):
    drone(TakeOff()
    >> FlyingStateChanged(state="hovering", _timeout=5)).wait()
    getgpsposition(drone)

def moveto(drone, longt, lati, alti):
    drone(moveTo(longt,lati,alti,0,0)
    >> FlyingStateChanged(state="hovering", _timeout=5)).wait()
    getgpsposition(drone)

def changealtitude(drone, alt):
    lat = drone.get_state(PositionChanged)["latitude"]
    lon = drone.get_state(PositionChanged)["longitude"]

    drone(moveTo(lon,lat,alt,0,0)
    >> FlyingStateChanged(state="hovering", _timeout=5)).wait()
    getgpsposition(drone)

def land(drone):
    assert drone(Landing()).wait().success()
    getgpsposition(drone)


if __name__ == "__main__":
    with olympe.Drone(DRONE_IP,) as drone:
        drone.connect()

        #drone.FlyingStateChanged(state="hovering", _policy="check")
        #TakeOffLocation = drone.get_state(GpsLocationChanged)

        takeoff(drone)
        TakeOffLocation = drone.get_state(GpsLocationChanged)

        getgpsposition(drone)
        moveto(drone, .00001, 0, 1)
        getgpsposition(drone)
        changealtitude(drone, 5)
        getgpsposition(drone)
        moveto(drone, TakeOffLocation["latitude"], TakeOffLocation["longitude"], 1)
        getgpsposition(drone)
        land(drone)

        # Leaving the with statement scope: implicit drone.disconnect() but that
        # is still a good idea to perform the drone disconnection explicitly
        drone.disconnect()

