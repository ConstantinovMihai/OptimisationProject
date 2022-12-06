"""This file contains definitions of the classes used in the model"""

import numpy as np

class Depot:
    def __init__(self, Oi, Wi, x, y, z):
        """ Constructor of the Depot class

        Args:
            Oi (float): cost of setting up the depot
            Wi (float): capacity of the depot
            x (float): x coordinate of the depot
            y (float): y coordinate of the depot
            z (float): z coordinate of the depot 
        """

        self.cost = Oi
        self.cap = Wi
        self.x = x
        self.y = y
        self.z = z


class Customer:
    def __init__(self, D, x, y, z):
        """ Constructor of the Customer class

        Args:
            D (float): demand of the customer
            x (float): x coordinate of the customer
            y (float): y coordinate of the customer
            z (float): z coordinate of the customer 
        """

        self.demand = D
        self.x = x
        self.y = y
        self.z = z


class Truck:
    def __init__(self, F, Q, m, F_wind, F_internal, E):
        """ Constructor of the Truck class

        Args:
            F (float): Cost of using the truck
            Q (float): max capacity of the truck
            m (float): mass of the truck
            F_wind (float) : drag force acting on the truck
            F_internal (float) : force acting on the truck
            E (float) : fuel consumption of the trucl
        """

        self.F = F
        self.Q = Q
        self.m = m
        self.F_wind = F_wind
        self.F_internal = F_internal
        self.E = E


