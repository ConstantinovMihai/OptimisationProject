""" This file generates input for the model, based on the definition of the classes from parameters.py"""

import numpy as np
from parameters import *


def generatesInputDepos(nb_depots : int):
    """ creates the Depot classes and generates data for their attributes

    Args:
        nb_depots (int): number of depos

    Returns a list containing the newly created classes
    """
    depos = []
    for i in range(nb_depots):
        # cost of setting the depo
        Oi = max(np.random.normal(loc=100, scale=10), 0)
        Wi = np.random.uniform(low=5, high=40)
        x = np.random.uniform(low=0, high=100)
        y = np.random.uniform(low=0, high=100)
        z = np.random.uniform(low=0, high=10)
        new_depo = Depot(Oi, Wi, x, y, z)
        depos.append(new_depo)

    return depos


def generatesInputCustomers(nb_customers : int):
    """ creates the Customer classes and generates data for their attributes

    Args:
        nb_customers (int): number of depos
    
    Returns a list containing the newly created classes
    """
    customers = []
    for i in range(nb_customers):
        # cost of setting the depo
        dem = max(np.random.normal(loc=100, scale=10), 0)
        x = np.random.uniform(low=0, high=100)
        y = np.random.uniform(low=0, high=100)
        z = np.random.uniform(low=0, high=10)
        new_customer = Customer(dem, x, y, z)
        customers.append(new_customer)

    return customers


def generatesInputTrucks(nb_trucks : int):
    """ creates the Truck classes and generates data for their attributes

    Args:
        nb_trucks (int): number of depos
    
    Returns a list containing the newly created classes
    """
    customers = []
    for i in range(nb_trucks):
        # cost of setting the depo
        F = max(np.random.normal(loc=30, scale=10), 0)
        Q = max(np.random.normal(loc=30, scale=10), 10)
        m = max(np.random.normal(loc=30, scale=10), 10)
        F_wind = max(np.random.normal(loc=30, scale=10), 10)
        F_int = max(np.random.normal(loc=30, scale=10), 10)
        E = max(np.random.normal(loc=30, scale=10), 10)
        new_customer = Truck(F, Q, m, F_wind, F_int, E)

        customers.append(new_customer)

    return customers


def generateInput(nb_depots : int, nb_customers : int, nb_trucks : int):
    """ creates the classes and generates data for their attributes

    Args:
        nb_depots (int): total number of available depots
        nb_customers (int): total number of customers
        nb_trucks (int): total number of available trucks
    """
    
    depos = generatesInputDepos(nb_depots)
    customers = generatesInputCustomers(nb_customers)
    trucks = generatesInputTrucks(nb_trucks)

    return depos, customers, trucks


if __name__ == "__main__":
    stuff = generateInput(10, 5, 10)
    print("done")
