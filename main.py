import os
from threading import Thread
import kivy
os.environ['DISPLAY'] = ":0.0"
os.environ['KIVY_WINDOW'] = 'egl_rpi'
import pygame
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider
from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton
from pidev.kivy.selfupdatinglabel import SelfUpdatingLabel
from kivy.animation import Animation
from kivy.uix.widget import Widget
from pidev.Joystick import Joystick
from datetime import datetime
import itertools
from time import sleep
from ODrive_Ease_Lib import *

time = datetime

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'
PICTURE_SCREEN_NAME = 'picture'
JOYSTICK_SCREEN_NAME = 'joystick'

od = find_odrive()

class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    Direction = 0
    count = 0
    motor_label = "Off"
    counter3 = 0
    count2 = .55
    ax = ODrive_Axis(od.axis0, 20)
    topspeed = 40
    def startup(self):
        assert od.config.enable_brake_resistor is True, "Check for faulty brake resistor."
        dump_errors(od)

        # Selecting an axis to talk to, axis0 and axis1 correspond to M0 and M1 on the ODrive

        # Basic motor tuning, for more precise tuning follow this guide: https://docs.odriverobotics.com/control.html#tuning
        self.ax.set_gains()

        if not self.ax.is_calibrated():
            print("calibrating...")
            # ax.calibrate()
            self.ax.calibrate_with_current_lim(20)
        self.ax.set_vel_limit(self.topspeed)
        Thread(target=self.updatelabel).start()
    def pressed(self):
        """
        Function called on button touch event for button with id: testButton
        :return: None
        """
        sleep(1)
        quit()

    def pressed2(self):
        self.ax.set_relative_pos(50)

    def position0(self):
        self.ax.set_pos(0)

    def slider_something(self, speed):
        if speed == 0:
            self.ax.idle()
        else:
            self.ax.set_vel(speed)
        dump_errors(od)
    def motor_change_direction(self):
        if self.Direction == 0:
            self.ax.set_vel(self.topspeed)
            self.Direction = 1
        else:
            self.ax.set_vel(-1*self.topspeed)
            self.Direction = 0
    joystick1 = Joystick(0, False)

    def updatelabel (self):
        while True:
            if self.joystick1.get_both_axes()[1] !=0:
                self.ax.set_vel(self.topspeed*self.joystick1.get_both_axes()[1])
                sleep(.1)
            else:
                self.ax.set_vel(0)
                while self.ax.is_busy():
                    sleep(.1)
    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """

        SCREEN_MANAGER.current = 'passCode'



class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()

Builder.load_file('main.kv')

SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'

    ProjectNameGUI().run()

