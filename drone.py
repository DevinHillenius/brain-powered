#! /usr/bin/env python3
# Communication with drone
# By Derk Barten and Devin Hillenius
# UvA Brain Powered 2017-2018

from pyardrone import ARDrone
from time import sleep


class Drone(object):
    def __init__(self):
        self.d = ARDrone()
        self.d.navdata_ready.wait()

    def takeoff(self):
        """Start flying the drone."""
        self.d.takeoff()

    def land(self):
        """Land the drone."""
        self.d.land()

    def move(self, direction, t=1, speed=1):
        """
        Move the drone forward or backward or rotate the drone for 't' seconds.
        The 'direction' argument can be:
            - 'forward': move forward
            - 'backward': move backward
            - 'rotate_right': rotate 90 degrees to the right
            - 'rotate_left': rotate 90 degrees to the left
        """
        if direction == 'forward':
            self.d.move(forward=speed)
        elif direction == 'backward':
            self.d.move(backward=speed)
        elif direction == 'rotate_right':
            self.d.move(cw=speed)
        elif direction == 'rotate_left':
            self.d.move(ccw=speed)
        else:
            raise ValueError(
                'Given direction {} not supported!'.format(direction))
        sleep(t)
        self.d.hover()

    # def print_battery():
    #     """Print the battery percentage of the drone to stdout."""
    #     print("Drone battery percentage: {}".format(drone.navdata['demo'][
    #         'battery']))
