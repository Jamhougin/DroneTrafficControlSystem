import os
import random
from math import *
from kivy.garden.mapview.mapview.utils import clamp
import time
import pickle
import threading
from DroneController import *
from AbstractDrone import AbstractDrone
from VirtualDrone import VirtualDrone
from Location import Location
from Flight import Flight
from save_load import *
from PrintLists import *
from FloatInput import FloatInput

from kivy.config import Config
Config.set('graphics','maxfps','60')

from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.uix.recycleview import RecycleView

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.graphics.transformation import Matrix
from kivy.graphics.context_instructions import Translate, Scale
from kivy.garden.mapview.mapview import MapView, MapLayer, MapMarker, MarkerMapLayer, MIN_LONGITUDE, MIN_LATITUDE, MAX_LATITUDE, MAX_LONGITUDE

from functools import partial

drones = LoadDroneList()
locations = LoadLocationList()
flights = LoadFlightList()
threads = []      
coordinates = []
corridors = []
network = []
drone_hidden = True
location_hidden = True
 
class MapViewApp(App):
    mapview = None
 
    def __init__(self, **kwargs):
        super(MapViewApp, self).__init__(**kwargs)
        Clock.schedule_once(self.post, 0)
 
    def build(self):
        self.title = "Drone Air Traffic Control"
        layout = BoxLayout(orientation='vertical')
        return layout
 
    def post(self, *args):
        layout = FloatLayout()
        self.mapview = MapView(zoom=18, lat=52.824725, lon=-6.935661)
        line = LineMapLayer()
        self.mapview.add_layer(line, mode="scatter")  # window scatter
        drone_layer = DroneMarkerLayer()
        self.mapview.add_layer(drone_layer, mode="scatter")
        location_layer = LocationMarkerLayer()
        self.mapview.add_layer(location_layer, mode="scatter")
        flights_layer = FlightLayer()
        self.mapview.add_layer(flights_layer, mode="scatter")
        layout.add_widget(self.mapview)
        
        dronebuttoncolor = [.3,1,0,1] #Green
        locationbuttoncolor = [.5,1,1,1] #Blue
        flightbuttoncolor = [1,1,.5,1] #Yellow

        buttonrow1 = BoxLayout(orientation='horizontal',height='30dp',size_hint_y=None)
        buttonrow2 = BoxLayout(orientation='horizontal',height='30dp',size_hint_y=None)
        buttonrow3 = BoxLayout(orientation='horizontal',height='30dp',size_hint_y=None)
        
        buttonrow1.add_widget(Button(text="Zoom in",on_press=lambda a: setattr(self.mapview,'zoom',self.mapview.zoom+1)))
        buttonrow1.add_widget(Button(text="RemoveDrone",on_press=lambda a: drone_layer.remove_drone_popup(), background_color = dronebuttoncolor))
        buttonrow1.add_widget(Button(text="ViewLocationsList",on_press=lambda a: location_layer.view_locations_popup(), background_color = locationbuttoncolor))
        buttonrow1.add_widget(Button(text="ViewLocationMarkers", background_color = locationbuttoncolor, on_press=lambda a: show_locations_button(self.mapview, location_layer, drone_layer)))
        
        buttonrow2.add_widget(Button(text="ViewDrones", background_color = dronebuttoncolor,on_press=lambda a: show_drones_button(self.mapview, drone_layer, location_layer)))
        buttonrow2.add_widget(Button(text="AddVirtualDrone",on_press=lambda a: drone_layer.add_virtual_drone_popup(), background_color = dronebuttoncolor))
        buttonrow2.add_widget(Button(text="AddLocation",on_press=lambda a: location_layer.add_point_popup(), background_color = locationbuttoncolor))
        buttonrow2.add_widget(Button(text="RemoveLocation",on_press=lambda a: location_layer.remove_location_popup(), background_color = locationbuttoncolor))
        buttonrow3.add_widget(Button(text="ViewFlightsList",on_press=lambda a: flights_layer.view_flights_popup(), background_color = flightbuttoncolor))
        buttonrow3.add_widget(Button(text="CreateFlight",on_press=lambda a: flights_layer.create_flight_popup(), background_color = flightbuttoncolor))
        buttonrow3.add_widget(Button(text="RemoveFlight",on_press=lambda a: flights_layer.remove_flight_popup(), background_color = flightbuttoncolor))
        buttonrow3.add_widget(Button(text="StartFlight",on_press=lambda a: flights_layer.start_flight_popup(), background_color = flightbuttoncolor))
        #First button row
        self.root.add_widget(buttonrow1)
        #Second button row
        self.root.add_widget(buttonrow2)
        #Third button row
        self.root.add_widget(buttonrow3)
        self.root.add_widget(layout)
        
        def show_locations_button(mapview, locationslayer, droneslayer):
            global location_hidden
            global drone_hidden
            global threads
            mapv = mapview 
            locationsl = locationslayer 
            dronesl = droneslayer 

            if location_hidden == True:
                location_hidden = False                
                locationsl.draw_locations()
            elif location_hidden == False:
                location_hidden = True
                for child in mapv.children:
                    if type(child) is MarkerMapLayer:
                        #Remove all marker widgets and add back in Drone markers if not hidden
                        child.clear_widgets()
                        #print(child.children)
                        if drone_hidden == False:
                            threads.append(Thread(target = dronesl.draw_drones, args = (dronesl, locationsl), daemon = True))
                            threads[len(threads)-1].start()
                        break

        def show_drones_button(mapview, droneslayer, locationslayer):
            global drone_hidden
            global location_hidden
            global threads
            mapv = mapview
            dronesl = droneslayer
            locationsl = locationslayer
            
            if drone_hidden == True:
                drone_hidden = False                
                threads.append(Thread(target = dronesl.draw_drones, args = (dronesl, locationsl), daemon = True))
                threads[len(threads)-1].start()                    
            elif drone_hidden == False:
                drone_hidden = True
                for child in mapv.children:
                    if type(child) is MarkerMapLayer:
                        #Remove all marker widgets and add back in Location markers if not hidden
                        child.clear_widgets()
                        if location_hidden == False:
                            locationsl.draw_locations()
                        break

###Class related to displaying locations on screen
class LocationMarkerLayer(MapLayer):
    locationview = None
    
    def __init__(self, **kwargs):
        super(LocationMarkerLayer, self).__init__(**kwargs)
        self.zoom = 0
        locationview = self.parent
        
    def draw_locations(self, *args):
        locationview = self.parent
        self.zoom = locationview.zoom
        global locations

        for location in locations:  
            # Draw new Location markers
            locationview.add_marker(MapMarker(lat=location.getlocationlatitude(), lon=location.getlocationlongitude(), source='images/MapMarker.png'))
           
    def add_point(self, name, lat, lon, alt):
        global locations
        newlocation = Location(name, lat, lon, alt)
        #: Add a point a chosen coordinates
        print("location to add:")
        print (newlocation.getlocationname())
        locations.append(newlocation)
        SaveLocationList(locations)
       
    def add_point_popup(self):
        global locations

        self.root = BoxLayout(orientation='vertical')
        nameinput = TextInput(hint_text="name", multiline=False)
        
        latinput = FloatInput(hint_text="latitude", multiline=False)

        loninput = FloatInput(hint_text="longitude", multiline=False)
        
        #Text boxes to add location info
        self.root.add_widget(nameinput, index=0)
        self.root.add_widget(latinput, index=0)
        self.root.add_widget(loninput, index=0)

        self.root.add_widget(Button(text="AddPoint",on_press=lambda a: self.add_point(nameinput.text, latinput.text, loninput.text, 0)))
        self.popup = Popup(title="Add Location", auto_dismiss=True, size_hint=(.5,.5))
        self.root.add_widget(Button(text="Close window",on_press=lambda a: self.popup.dismiss()))
        self.popup.add_widget(self.root)    
        self.popup.open()
        
    def view_locations_popup(self):
           
        self.root = BoxLayout(orientation='vertical')
        
        
        self.root.add_widget(Label(text= location_list()))
        self.root.add_widget(Button(text="Close window",on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="View Location List", auto_dismiss=True, size_hint=(.5,.5))
        self.popup.add_widget(self.root)
        self.popup.open()
  
    def remove_location_popup(self):
        def buttonPressRemoveLocation(selection):
            global locations
            if int(selection) < 1 or int(selection) > len(locations):
                return
            
            del locations[int(selection)-1]
            SaveLocationList(locations)
        
        self.root = BoxLayout(orientation='vertical')
        
        self.root.add_widget(Label(text= location_list()))
        
        location = FloatInput(hint_text="Enter Number corresponding to location", multiline=False)
        self.root.add_widget(location)
        self.root.add_widget(Button(text="RemoveLocation",on_press=lambda a: buttonPressRemoveLocation(location.text)))
        
        self.root.add_widget(Button(text="Close window",on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="Remove Location", auto_dismiss=True, size_hint=(.5,.5))
        self.popup.add_widget(self.root)
        self.popup.open()
                          
###Class related to displaying drones on screen
class DroneMarkerLayer(MapLayer):
    droneview = None
    
    def __init__(self, **kwargs):
        super(DroneMarkerLayer, self).__init__(**kwargs)
        self.zoom = 0
        droneview = self.parent
    
    def add_virtual_drone(self, name, home):
        global locations
        for location in locations:
            if location.getlocationname() == home:
                home_loc = location
                
                global drones
                newdrone = VirtualDrone(name, "Virtual", home_loc.getlocationlatitude(), home_loc.getlocationlongitude(), home_loc.getlocationlatitude(), home_loc.getlocationlongitude(), 0, 100, 0, "Grounded", 0)
                break
        

        drones.append(newdrone)
        SaveDroneList(drones)
        
    def add_virtual_drone_popup(self):
        global drones
        global locations
        self.root = BoxLayout(orientation='vertical')
        nameinput = TextInput(hint_text="drone name", multiline=False)
        
        homeinput = TextInput(hint_text="home location name", multiline=False)

        
        #Text boxes to add location info
        self.root.add_widget(nameinput, index=0)
        self.root.add_widget(Label(text= location_list()))
        self.root.add_widget(homeinput, index=0)

        self.root.add_widget(Button(text="AddDrone",on_press=lambda a: self.add_virtual_drone(nameinput.text, homeinput.text)))
        self.popup = Popup(title="Add Drone", auto_dismiss=True, size_hint=(.5,.5))
        self.root.add_widget(Button(text="Close window",on_press=lambda a: self.popup.dismiss()))
        self.popup.add_widget(self.root)    
        self.popup.open()
        
    def remove_drone_popup(self):
        def buttonPressRemoveDrone(selection):
            global drones
            if int(selection) < 1 or int(selection) > len(drones):
                return
            
            del drones[int(selection)-1]
            SaveDroneList(drones)
        
        self.root = BoxLayout(orientation='vertical')
        
        self.root.add_widget(Label(text= drone_list()))
        
        location = FloatInput(hint_text="Enter Number corresponding to drone", multiline=False)
        self.root.add_widget(location)
        self.root.add_widget(Button(text="RemoveDrone",on_press=lambda a: buttonPressRemoveDrone(location.text)))
        
        self.root.add_widget(Button(text="Close window",on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="Remove Drone", auto_dismiss=True, size_hint=(.5,.5))
        self.popup.add_widget(self.root)
        self.popup.open()
        
    def insert_drone_image(self, drone, *largs):
        droneview = self.parent
        droneview.add_marker(MapMarker(lat=drone.getcurrentlatitude(), lon=drone.getcurrentlongitude(), source="images/Drone.png"))
        
    def draw_drones(self, dronel, locationl):
        dronel = dronel
        locationl = locationl
        droneview = self.parent
        self.zoom = droneview.zoom
        global drones
        global drone_hidden
        global flights
        
        flightinprogress = False
        for drone in drones:
            if drone.getdronestate() != "Grounded":
                flightinprogress = True
                break
        i = 1 #Used to draw the drones once when not in flight
        while (drone_hidden == False and flightinprogress == True) or i == 1:
            for child in droneview.children:
                if type(child) is MarkerMapLayer:
                    child.clear_widgets()
                    break
            #Draw location markers if they should be seen        
            if location_hidden == False:
                Clock.schedule_once(partial(locationl.draw_locations))
            for drone in drones:  
                #Draw Drone markers
                Clock.schedule_once(partial(self.insert_drone_image, drone))
            
            time.sleep(.05)
            i = i+1
                
###Class related to flight CRUD operations
class FlightLayer(MapLayer):

    def __init__(self, **kwargs):
        super(FlightLayer, self).__init__(**kwargs)
        self.zoom = 0
        droneview = self.parent

    def view_flights_popup(self):
           
        self.root = BoxLayout(orientation='vertical')
        
        
        self.root.add_widget(Label(text= flight_list()))
        self.root.add_widget(Button(text="Close window",on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="View Flight List", auto_dismiss=True, size_hint=(.9,.7))
        self.popup.add_widget(self.root)
        self.popup.open()  
    
    def create_flight_popup(self):
        mapview = self.parent
        global flights
        global locations
        global drones
        new_flight = Flight("F", 0, 0, 0, 0, "D", False)
        
        def buttonPressAddFlightName(newflight, name):
            newflight.setflightid(name)
        
        def buttonPressAddDrone(newflight, drones, selection):
            for drone in drones:
                if drone.drone_id == selection:
                    newflight.setdrone(drone.drone_id)
                    newflight.setstartlatitude(drone.gethomelatitude())
                    newflight.setstartlongitude(drone.gethomelongitude())
        
        def buttonPressAddDestination(newflight, locations, selection):
            for location in locations:
                if location.getlocationname() == selection:
                    newflight.setdestinationlatitude(location.getlocationlatitude())
                    newflight.setdestinationlongitude(location.getlocationlongitude())
            
        def buttonPressAddFlight(newflight, flights):
            flights.append(newflight)
            SaveFlightList(flights)

        
        self.root = BoxLayout(orientation='vertical', spacing =5)
        
        flightname = TextInput(hint_text="Flight Name", multiline=False)
        self.root.add_widget(flightname)
                
        self.root.add_widget(Label(text= drone_list()))
        
        drone = TextInput(hint_text="Drone choice", multiline=False)
        self.root.add_widget(drone)
        
        self.root.add_widget(Label(text= location_list()))
        
        location = TextInput(hint_text="Destination Choice", multiline=False)
        self.root.add_widget(location)
        
        self.root.add_widget(Button(text="AddFlightName",on_press=lambda a: buttonPressAddFlightName(new_flight, flightname.text)))
        self.root.add_widget(Button(text="AddDrone",on_press=lambda a: buttonPressAddDrone(new_flight, drones, drone.text)))
        self.root.add_widget(Button(text="AddDestination",on_press=lambda a: buttonPressAddDestination(new_flight, locations, location.text)))
        self.root.add_widget(Button(text="AddFlight",on_press=lambda a: buttonPressAddFlight(new_flight, flights)))
        
        self.root.add_widget(Button(text="Close window",on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="Add Flight", auto_dismiss=True, size_hint=(.9,.8))
        self.popup.add_widget(self.root)
        self.popup.open()  
        
    def remove_flight_popup(self):
        def buttonPressRemoveFlight(selection):
            global flights
            del flights[int(selection)-1]
            SaveFlightList(flights)
        
        self.root = BoxLayout(orientation='vertical')
        
        self.root.add_widget(Label(text= flight_list()))
        
        flight = FloatInput(hint_text="Enter Number corresponding to flight", multiline=False)
        self.root.add_widget(flight)
        self.root.add_widget(Button(text="CancelFlight",on_press=lambda a: buttonPressRemoveFlight(flight.text)))
        
        self.root.add_widget(Button(text="Close window",on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="Cancel Flight", auto_dismiss=True, size_hint=(.9,.5))
        self.popup.add_widget(self.root)
        self.popup.open() 
        
    def start_flight_popup(self):
        def buttonPressBeginFlight(selection):
            global flights
            global drones
            global threads
            
            for drone in drones:
                if drone.drone_id == flights[int(selection)-1].getdrone():
                    flight_drone = drone
            threads.append(Thread(target = TakeOffFlyLand,  args = (flight_drone, flights[int(selection)-1], drones), daemon = True))
            threads[len(threads)-1].start()
        
        self.root = BoxLayout(orientation='vertical')

        self.root.add_widget(Label(text= flight_list()))
        
        flight = FloatInput(hint_text="Enter Number corresponding to flight", multiline=False)
        self.root.add_widget(flight)
        self.root.add_widget(Button(text="BeginFlight",on_press=lambda a: buttonPressBeginFlight(flight.text)))
        
        self.root.add_widget(Button(text="Close window",on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="Start Flight", auto_dismiss=True, size_hint=(.9,.5))
        self.popup.add_widget(self.root)
        self.popup.open()                        
            
###Class related to displaying lines between destinations !Currently unused           
class LineMapLayer(MapLayer):
    
    def __init__(self, **kwargs):
        super(LineMapLayer, self).__init__(**kwargs)
        self.zoom = 0
        mapview = self.parent
        global coordinates
        
    
    def reposition(self):
        mapview = self.parent
        global corridors
        
        #: Must redraw when the zoom changes 
        #: as the scatter transform resets for the new tiles
        if (self.zoom != mapview.zoom):
            self.draw_line()           

    def create_corridor_popup(self):
        mapview = self.parent
        global coordinates
        global locations
        global corridors
        corridortoadd = []
        
        def buttonPressAddLocation(coord, corr, corridortoadd, selection):
            corridortoadd.append(coord[int(selection)-1])
            print(coord[int(selection)-1])
            print(corridortoadd)
            
        def buttonPressAddCorridor(corr):
            global corridors
            corridors.append(corridortoadd)
            #self.draw_line(corr)
            self.draw_line()
            print("Full corridors list:")
            print(corridors)

        
        self.root = BoxLayout(orientation='vertical', spacing =5)
                
        self.root.add_widget(Label(text= self.location_list()))
        
        location = TextInput(hint_text="Enter Number corresponding to flight", multiline=False)
        self.root.add_widget(location, index=0)
        
        self.root.add_widget(Label(text= str(corridortoadd)))
        
        self.root.add_widget(Button(text="AddLocation",on_press=lambda a: buttonPressAddLocation(coordinates, corridors, corridortoadd, location.text)))
        self.root.add_widget(Button(text="AddCorridor",on_press=lambda a: buttonPressAddCorridor(corridortoadd)))
        
        self.root.add_widget(Button(text="Close window",on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="Add Corridor", auto_dismiss=True, size_hint=(.5,.5))
        self.popup.add_widget(self.root)
        self.popup.open()
        
                   
        
    def get_x(self, lon):
        """Get the x position on the map using this map source's projection
        (0, 0) is located at the top left.
        """
        return clamp(lon, MIN_LONGITUDE, MAX_LONGITUDE)
 
    def get_y(self, lat):
        """Get the y position on the map using this map source's projection
        (0, 0) is located at the top left.
        """
        lat = clamp(-lat, MIN_LATITUDE, MAX_LATITUDE)
        lat = lat * pi / 180.
        return ((1.0 - log(tan(lat) + 1.0 / cos(lat)) / pi))
    
    def draw_line(self, *args):
        mapview = self.parent
        self.zoom = mapview.zoom
        global coordinates
        global corridors
        #corridor = corr
       
        # When zooming we must undo the current scatter transform
        # or the animation distorts it
        scatter = mapview._scatter
        map_source = mapview.map_source
        sx,sy,ss = scatter.x, scatter.y, scatter.scale
        vx,vy,vs = mapview.viewport_pos[0], mapview.viewport_pos[1], mapview.scale       
        # Account for map source tile size and mapview zoom
        ms = pow(2.0,mapview.zoom) * map_source.dp_tile_size        
        #: Since lat is not a linear transform we must compute manually 
               
        #line_points = []
        with self.canvas:
                # Clear old line
                self.canvas.clear()
        
        for corridor in corridors:
            line_points = []
            for lat,lon in corridor:
                line_points.extend((self.get_x(lon),self.get_y(lat)))
                print("linepointslist:")
                print (line_points)
                #line_points.extend(mapview.get_window_xy_from(lat,lon,mapview.zoom))
        
         
            with self.canvas:
                # Clear old line
                #self.canvas.clear()
                # Undo the scatter animation transform
                Scale(1/ss,1/ss,1)
                Translate(-sx,-sy)
                
                # Apply the get window xy from transforms
                Scale(vs,vs,1)
                Translate(-vx,-vy)
                   
                # Apply the what we can factor out
                # of the mapsource long,lat to x,y conversion
                Scale(ms/360.0,ms/2.0,1)
                Translate(180,0)
                 
                # Draw new
                Color(1, 0, 0, 1)
                print("linepointslist Line:")
                print (line_points)
                Line(points=line_points, width=1)#4/ms)#, joint="round",joint_precision=100)
                self.canvas.ask_update()


MapViewApp().run()
