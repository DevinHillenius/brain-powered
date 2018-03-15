#! /usr/bin/env python3
# Communication with drone
# By Derk Barten and Devin Hillenius
# UvA Brain Powered 2017-2018

import ardrone
from time import sleep


class Drone(object):
    def __init__(self):
        self.d = ardrone.ARDrone()

    def takeoff(self):
        """Start flying the drone."""
        self.d.takeoff()

    def land(self):
        """Land the drone."""
        self.d.land()

    def move(self, direction, t):
        """
        Move the drone forward or backward or rotate the drone for 't' seconds.
        The 'direction' argument can be:
            - 'forward': move forward
            - 'backward': move backward
            - 'rotate': rotate to the right
        """
        if direction == 'forward':
            self.d.move_forward()
        elif direction == 'backward':
            self.d.move_backward()
        else:
            self.d.turn_right()
        sleep(t)
        self.d.hover()

    def print_battery():
        """Print the battery percentage of the drone to stdout."""
        print("Drone battery percentage: {}".format(drone.navdata['demo'][
            'battery']))
