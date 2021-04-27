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
from kivy.lang import Builder

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
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

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
new_location_add = False
name = ''
location_layer = None
 
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
        
        global location_layer
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
        
        buttonrow1.add_widget(Button(text="RemoveDrone",on_press=lambda a: drone_layer.remove_drone_popup(), background_color = dronebuttoncolor))
        buttonrow1.add_widget(Button(text="AddDrone",on_press=lambda a: drone_layer.add_virtual_drone_popup(), background_color = dronebuttoncolor))
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
        buttonrow3.add_widget(Button(text="AbortFlight",on_press=lambda a: flights_layer.abort_flight_popup(), background_color = flightbuttoncolor))
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
    
    #Adds functionality to kivy's on_touch_down() event, specificly for adding new Locations    
    def on_touch_down(self, touch):
            global new_location_add
            global location_layer
            
            if new_location_add == True:
                print(touch.pos[0])
                print(touch.pos[1])
                location_layer.add_point(touch.pos[0],touch.pos[1],0)
            return super(LocationMarkerLayer, self).on_touch_down(touch)

    def draw_locations(self, *args):
        locationview = self.parent
        self.zoom = locationview.zoom
        global locations

        for location in locations:  
            # Draw new Location markers
            locationview.add_marker(MapMarker(lat=location.getlocationlatitude(), lon=location.getlocationlongitude(), source='images/MapMarker.png'))
           
    def add_point(self, lat, lon, alt):
        global locations
        global new_location_add
        global name
        if new_location_add == True:
            newlocation = Location(name, self.parent.get_latlon_at(lat,lon)[0], self.parent.get_latlon_at(lat,lon)[1], alt)
            new_location_add = False
            #: Add a point a chosen coordinates
            print("location to add:")
            print (newlocation.getlocationname())
            locations.append(newlocation)
            self.draw_locations()
            SaveLocationList(locations)
    
    def set_loc_name(self, nname):
        global name
        global new_location_add
        name = nname
        new_location_add = True
        
    def add_point_popup(self):
        mapview = self.parent
        global locations
        global name
        global new_location_add
        self.root = BoxLayout(orientation='vertical',spacing=15)
        
        nameinput = TextInput(hint_text="name", multiline=False, size_hint=(.9, None), pos_hint ={'center_x': .5,'center_y': 1}, height=40)
        self.root.add_widget(nameinput, index=0)

        self.popup = Popup(title="Add Location", auto_dismiss=True, size_hint=(.5,.5))
        self.root.add_widget(Button(text="Add Location Name", size_hint=(.9,.7), pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: (self.popup.dismiss(),self.set_loc_name(nameinput.text))))
        self.root.add_widget(Button(text="Close window", background_color = [1,0,0,1], size_hint=(.9,.7), pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: self.popup.dismiss()))
        self.popup.add_widget(self.root)    
        self.popup.open()
         
    def view_locations_popup(self):
           
        self.root = BoxLayout(orientation='vertical',spacing=15)
        
        #Scrollable location list
        locationlistview = Label(text= location_list(),size_hint=(1.01, None))
        locationlistviewscroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/2),scroll_y=1, do_scroll_x=False, scroll_type=['bars','content'], bar_width = 10, pos_hint ={'center_x': .5,'center_y': 1})
        locationlistviewscroll.add_widget(locationlistview)
        locationlistviewscroll.effect_cls.spring_constant=0
        self.root.add_widget(locationlistviewscroll)
        
        self.root.add_widget(Button(text="Close window", background_color = [1,0,0,1], size_hint=(.9,.7), pos_hint ={'center_x': .5,'center_y': 1}, on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="View Location List", auto_dismiss=True, size_hint=(.9,.8))
        self.popup.add_widget(self.root)
        self.popup.open()
  
    def remove_location_popup(self):
        def buttonPressRemoveLocation(selection):
            global locations
            global drone_hidden
            global location_hidden
            global threads
            if int(selection) < 1 or int(selection) > len(locations):
                return
            
            del locations[int(selection)-1]
            SaveLocationList(locations)

        
        self.root = BoxLayout(orientation='vertical',spacing=15)
        
        locationlistview = Label(text= location_list(),size_hint=(1.01, None))
        locationlistviewscroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/4),scroll_y=1, do_scroll_x=False, scroll_type=['bars','content'], bar_width = 10, pos_hint ={'center_x': .5,'center_y': 1})
        locationlistviewscroll.add_widget(locationlistview)
        locationlistviewscroll.effect_cls.spring_constant=0
        self.root.add_widget(locationlistviewscroll)
        
        location = FloatInput(hint_text="Enter Number corresponding to location", multiline=False, size_hint=(.9, None), pos_hint ={'center_x': .5,'center_y': 1},height=40)
        self.root.add_widget(location)
        self.root.add_widget(Button(text="RemoveLocation", size_hint=(.9,.8), pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: buttonPressRemoveLocation(location.text)))
        
        self.root.add_widget(Button(text="Close window", background_color = [1,0,0,1], size_hint=(.9,.8), pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: self.popup.dismiss()))
        
        #Add popup widget to root
        self.popup = Popup(title="Remove Location", auto_dismiss=True, size_hint=(.9,.8))
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
        if int(home) <= len(locations):
            for location in locations:
                if location.getlocationname() == locations[int(home)-1].getlocationname():
                    home_loc = location
                    
                    global drones
                    newdrone = VirtualDrone(name, "Virtual", float(home_loc.getlocationlatitude()), float(home_loc.getlocationlongitude()), float(home_loc.getlocationlatitude()), float(home_loc.getlocationlongitude()), 0, 100, 0, "Grounded", 0)
                    break
            

            drones.append(newdrone)
            SaveDroneList(drones)
        
    def add_virtual_drone_popup(self):
        global drones
        global locations
        self.root = BoxLayout(orientation='vertical',spacing=15)
        nameinput = TextInput(hint_text="drone name", multiline=False,size_hint=(.9, None),pos_hint ={'center_x': .5,'center_y': 1},height=40)        
        homeinput = FloatInput(hint_text="home location name", multiline=False,size_hint=(.9, None),pos_hint ={'center_x': .5,'center_y': 1},height=40)
        
        #Text boxes to add location info
        self.root.add_widget(nameinput, index=0)
        
        locationlistview = Label(text= location_list(),size_hint=(1, None))        
        locationlistviewscroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/4), do_scroll_x=False, scroll_type=['bars','content'], bar_width = 10, pos_hint ={'center_x': .5,'center_y': 1})
        locationlistviewscroll.add_widget(locationlistview)
        locationlistviewscroll.effect_cls.spring_constant=0
        self.root.add_widget(locationlistviewscroll)
        
        self.root.add_widget(homeinput, index=0)

        self.root.add_widget(Button(text="AddDrone",size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: self.add_virtual_drone(nameinput.text, homeinput.text)))
        self.popup = Popup(title="Add Drone", auto_dismiss=True, size_hint=(.9,.8))
        self.root.add_widget(Button(text="Close window", background_color = [1,0,0,1],size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: self.popup.dismiss()))
        
        #Add popup widget to root
        self.popup.add_widget(self.root)    
        self.popup.open()
        
    def remove_drone_popup(self):
        def buttonPressRemoveDrone(selection):
            global drones
            if int(selection) < 1 or int(selection) > len(drones):
                return
            
            del drones[int(selection)-1]
            SaveDroneList(drones)
        
        self.root = BoxLayout(orientation='vertical',spacing=15)
        
        #Scrollable Drone list
        dronelistview = Label(text= drone_list(),size_hint=(1.01, None))
        dronelistviewscroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/4), do_scroll_x=False, scroll_type=['bars','content'], bar_width = 10, pos_hint ={'center_x': .5,'center_y': 1})
        dronelistviewscroll.add_widget(dronelistview) 
        dronelistviewscroll.effect_cls.spring_constant=0
        self.root.add_widget(dronelistviewscroll)
        
        #Input box
        location = FloatInput(hint_text="Enter Number corresponding to drone", multiline=False, size_hint=(.9,None), pos_hint={'center_x': .5,'center_y': 1},height=40)
        self.root.add_widget(location)
        
        self.root.add_widget(Button(text="RemoveDrone", size_hint=(.9,.7), pos_hint={'center_x': .5,'center_y': 1},on_press=lambda a: buttonPressRemoveDrone(location.text)))
        
        self.root.add_widget(Button(text="Close window", background_color = [1,0,0,1], size_hint=(.9,.7), pos_hint={'center_x': .5,'center_y': 1},on_press=lambda a: self.popup.dismiss()))
        
        #Add popup widget to root
        self.popup = Popup(title="Remove Drone", auto_dismiss=True, size_hint=(.9,.8))
        self.popup.add_widget(self.root)
        self.popup.open()
        
    def insert_drone_image(self, drone, *largs):
        droneview = self.parent
        if drone.getdronestate() == "Descending" and drone.getbattery() > 50:
            droneview.add_marker(MapMarker(lat=drone.getcurrentlatitude(), lon=drone.getcurrentlongitude(), source="images/DroneDescending.png"))
        elif drone.getdronestate() == "Descending" and drone.getbattery() <= 50:
            droneview.add_marker(MapMarker(lat=drone.getcurrentlatitude(), lon=drone.getcurrentlongitude(), source="images/DroneDescending50batt.png"))
        elif drone.getdronestate() == "Descending" and drone.getbattery() <= 10:
            droneview.add_marker(MapMarker(lat=drone.getcurrentlatitude(), lon=drone.getcurrentlongitude(), source="images/DroneDescending10batt.png"))
        elif drone.getdronestate() == "Ascending" and drone.getbattery() > 50:
            droneview.add_marker(MapMarker(lat=drone.getcurrentlatitude(), lon=drone.getcurrentlongitude(), source="images/DroneAscending.png"))
        elif drone.getdronestate() == "Ascending" and drone.getbattery() <= 50:
            droneview.add_marker(MapMarker(lat=drone.getcurrentlatitude(), lon=drone.getcurrentlongitude(), source="images/DroneAscending50batt.png"))
        elif drone.getdronestate() == "Ascending" and drone.getbattery() <= 10:
            droneview.add_marker(MapMarker(lat=drone.getcurrentlatitude(), lon=drone.getcurrentlongitude(), source="images/DroneAscending10batt.png"))
        elif drone.getbattery() > 50:
            droneview.add_marker(MapMarker(lat=drone.getcurrentlatitude(), lon=drone.getcurrentlongitude(), source="images/Drone.png"))
        elif drone.getbattery() <= 50:
            droneview.add_marker(MapMarker(lat=drone.getcurrentlatitude(), lon=drone.getcurrentlongitude(), source="images/Drone50batt.png"))
        else:
            droneview.add_marker(MapMarker(lat=drone.getcurrentlatitude(), lon=drone.getcurrentlongitude(), source="images/Drone10batt.png"))
        
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
           
        self.root = BoxLayout(orientation='vertical',spacing=15)
        
        flightlistview = Label(text= flight_list(),size_hint=(1.01, None))
        flightlistviewscroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/2),scroll_y=1, scroll_type=['bars','content'], bar_width = 10, pos_hint ={'center_x': .5,'center_y': 1})
        flightlistviewscroll.add_widget(flightlistview)
        flightlistviewscroll.effect_cls.spring_constant=0
        self.root.add_widget(flightlistviewscroll)
        
        self.root.add_widget(Button(text="Close window", background_color = [1,0,0,1], size_hint=(.9,.7), pos_hint={'center_x': .5,'center_y': 1},on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="View Flight List", auto_dismiss=True, size_hint=(.9,.7))
        self.popup.add_widget(self.root)
        self.popup.open()  
    
    def create_flight_popup(self):
        mapview = self.parent
        global flights
        global locations
        global drones
        new_flight = Flight("F", 0, 0, 0, 0, "D", False, False)
        
        def buttonPressAddFlightName(newflight, name):
            newflight.setflightid(name)
        
        def buttonPressAddDrone(newflight, drones, selection):
            for drone in drones:
                if drone.drone_id == drones[int(selection)-1].drone_id:
                    newflight.setdrone(drone.drone_id)
                    newflight.setstartlatitude(drone.gethomelatitude())
                    newflight.setstartlongitude(drone.gethomelongitude())
        
        def buttonPressAddDestination(newflight, locations, selection):
            for location in locations:
                if location.getlocationname() == locations[int(selection)-1].getlocationname():
                    newflight.setdestinationlatitude(location.getlocationlatitude())
                    newflight.setdestinationlongitude(location.getlocationlongitude())
            
        def buttonPressAddFlight(newflight, flights):
            flights.append(newflight)
            SaveFlightList(flights)
            self.popup.dismiss()

        
        self.root = BoxLayout(orientation='vertical', spacing =5)
        
        flightname = TextInput(hint_text="Flight Name", multiline=False,size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1})
        self.root.add_widget(flightname)
        
        #Scrollable Drone list
        dronelistview = Label(text= drone_list(),size_hint=(1.01, None))
        dronelistviewscroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/8), do_scroll_x=False, scroll_type=['bars','content'], bar_width = 10, pos_hint ={'center_x': .5,'center_y': 1})
        dronelistviewscroll.add_widget(dronelistview) 
        dronelistviewscroll.effect_cls.spring_constant=0
        self.root.add_widget(dronelistviewscroll)
        
        drone = FloatInput(hint_text="Drone choice", multiline=False,size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1})
        self.root.add_widget(drone)
        
        locationlistview = Label(text= location_list(),size_hint=(1.01, None))
        locationlistviewscroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/8), do_scroll_x=False,scroll_y=1, scroll_type=['bars','content'], bar_width = 10, pos_hint ={'center_x': .5,'center_y': 1})
        locationlistviewscroll.add_widget(locationlistview)
        locationlistviewscroll.effect_cls.spring_constant=0
        self.root.add_widget(locationlistviewscroll)
        
        location = FloatInput(hint_text="Destination Choice", multiline=False,size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1})
        self.root.add_widget(location)
        
        self.root.add_widget(Button(text="AddFlightName",size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: buttonPressAddFlightName(new_flight, flightname.text)))
        self.root.add_widget(Button(text="AddDrone",size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: buttonPressAddDrone(new_flight, drones, drone.text)))
        self.root.add_widget(Button(text="AddDestination",size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: buttonPressAddDestination(new_flight, locations, location.text)))
        self.root.add_widget(Button(text="AddFlight",size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: buttonPressAddFlight(new_flight, flights)))
        
        self.root.add_widget(Button(text="Close window", background_color = [1,0,0,1],size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="Add Flight", auto_dismiss=True, size_hint=(.9,.8))
        self.popup.add_widget(self.root)
        self.popup.open()  
        
    def remove_flight_popup(self):
        def buttonPressRemoveFlight(selection):
            global flights
            if int(selection) <= len(flights):
                del flights[int(selection)-1]
                SaveFlightList(flights)
        
        self.root = BoxLayout(orientation='vertical',spacing=15)
        
        flightlistview = Label(text= flight_list(),size_hint=(1.01, None))
        flightlistviewscroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/4),scroll_y=1, scroll_type=['bars','content'], bar_width = 10, pos_hint ={'center_x': .5,'center_y': 1})
        flightlistviewscroll.add_widget(flightlistview)
        flightlistviewscroll.effect_cls.spring_constant=0
        self.root.add_widget(flightlistviewscroll)
        
        flight = FloatInput(hint_text="Enter Number corresponding to flight", multiline=False, size_hint=(.9, None), pos_hint ={'center_x': .5,'center_y': 1}, height = 40)
        self.root.add_widget(flight)
        self.root.add_widget(Button(text="CancelFlight",size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: buttonPressRemoveFlight(flight.text)))
        
        self.root.add_widget(Button(text="Close window", background_color = [1,0,0,1],size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="Cancel Flight", auto_dismiss=True, size_hint=(.9,.8))
        self.popup.add_widget(self.root)
        self.popup.open() 
        
    def abort_flight_popup(self):
        def buttonPressAbortFlight(selection):
            global flights
            flights[int(selection)-1].setflightabort(True)
            SaveFlightList(flights)
        
        self.root = BoxLayout(orientation='vertical',spacing=15)
        
        #Scrollable list of flights
        flightlistview = Label(text= flight_list(),size_hint=(1.01, None))
        flightlistviewscroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/4),scroll_y=1, scroll_type=['bars','content'], bar_width = 10, pos_hint ={'center_x': .5,'center_y': 1})
        flightlistviewscroll.add_widget(flightlistview)
        flightlistviewscroll.effect_cls.spring_constant=0
        self.root.add_widget(flightlistviewscroll)
        
        #Input Box
        flight = FloatInput(hint_text="Enter Number corresponding to flight", multiline=False, size_hint=(.9, None), pos_hint ={'center_x': .5,'center_y': 1},height=40)
        self.root.add_widget(flight)
        
        self.root.add_widget(Button(text="AbortFlight",size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: buttonPressAbortFlight(flight.text)))
        
        self.root.add_widget(Button(text="Close window", background_color = [1,0,0,1],size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="Abort Flight", auto_dismiss=True, size_hint=(.9,.8))
        self.popup.add_widget(self.root)
        self.popup.open() 
        
    def start_flight_popup(self):
        def buttonPressBeginFlight(selection):
            global flights
            global locations
            global drones
            global threads
            
            for drone in drones:
                if drone.drone_id == flights[int(selection)-1].getdrone():
                    flight_drone = drone
            threads.append(Thread(target = TakeOffFlyLand,  args = (flight_drone, flights[int(selection)-1], drones, locations), daemon = True))
            threads[len(threads)-1].start()
        
        self.root = BoxLayout(orientation='vertical',spacing=15)

        flightlistview = Label(text= flight_list(),size_hint=(1.01, None))
        flightlistviewscroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/4),scroll_y=1, scroll_type=['bars','content'], bar_width = 10, pos_hint ={'center_x': .5,'center_y': 1})
        flightlistviewscroll.add_widget(flightlistview)
        flightlistviewscroll.effect_cls.spring_constant=0
        self.root.add_widget(flightlistviewscroll)
        
        flight = FloatInput(hint_text="Enter Number corresponding to flight", multiline=False, size_hint=(.9, None), pos_hint ={'center_x': .5,'center_y': 1}, height = 40)
        self.root.add_widget(flight)
        self.root.add_widget(Button(text="BeginFlight",size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: buttonPressBeginFlight(flight.text)))
        
        self.root.add_widget(Button(text="Close window", background_color = [1,0,0,1],size_hint=(.9, .8),pos_hint ={'center_x': .5,'center_y': 1},on_press=lambda a: self.popup.dismiss()))
        self.popup = Popup(title="Start Flight", auto_dismiss=True, size_hint=(.9,.8))
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

if __name__ == "__main__":
    MapViewApp().run()
