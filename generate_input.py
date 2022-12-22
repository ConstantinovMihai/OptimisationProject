""" This file generates input for the model, based on the definition of the classes from parameters.py"""

import numpy as np
from parameters import *

np.random.seed(422)

def generatesInputDepos(nb_depots : int, id_list : np.array):
    """ creates the Depot classes and generates data for their attributes

    Args:
        nb_depots (int): number of depos
        id_list (np.array): the list with ids for the customers
    Returns a list containing the newly created classes
    """
    depos = []
    for i in range(nb_depots):
        # cost of setting the depo
        Oi = max(np.random.normal(loc=100, scale=10), 0)
        Wi = np.random.uniform(low=200, high=3000)
        x = np.random.uniform(low=0, high=100)
        y = np.random.uniform(low=0, high=100)
        z = np.random.uniform(low=0, high=10)
        new_depo = Depot(Oi, Wi, x, y, z, id=id_list[i])
        depos.append(new_depo)

    return depos



def generatesInputCustomers(nb_customers : int, id_list : np.array):
    """ creates the Customer classes and generates data for their attributes

    Args:
        nb_customers (int): number of depos
        id_list (np.array): the list wiht ids for the customers
    
    Returns a list containing the newly created classes
    """
    customers = []
    for i in range(nb_customers):
        # cost of setting the depo
        dem = max(np.random.normal(loc=30, scale=10), 0)
        x = np.random.uniform(low=0, high=100)
        y = np.random.uniform(low=0, high=100)
        z = np.random.uniform(low=0, high=10)
        new_customer = Customer(dem, x, y, z, id = id_list[i])
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
        Q = max(np.random.normal(loc=100, scale=10), 10)
        m = max(np.random.normal(loc=30, scale=10), 10)
        F_wind = max(np.random.normal(loc=30, scale=10), 10)
        F_int = max(np.random.normal(loc=30, scale=10), 10)
        E = max(np.random.normal(loc=30, scale=10), 10)
        new_customer = Truck(F, Q, m, F_wind, F_int, E, id = i)

        customers.append(new_customer)

    return customers


def generateCostsBetweenNodes(depos, customers):
    """ Generates a matrix of costs from node i to node j
        The model is based on the amount of fuel needed to go from Node i to Node j, plus some gaussian noise (road tolls etc)

    Args:
        depos (list of Depos): list containing Depos objects
        customers (list of Customers): list containing Customer objects
    """

    def computeDistance(node1, node2):
        return np.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

    costs = np.zeros((len(depos) + len(customers), len(depos) + len(customers)))
    nodes = [*depos, *customers]


    for idx_i, node_i in enumerate(nodes):
        for idx_j, node_j in enumerate(nodes):
            costs[idx_i, idx_j] = computeDistance(node_i, node_j) # add here some gaussian noise or smth

    return costs



def generateInput(nb_depots : int, nb_customers : int, nb_trucks : int):
    """ creates the classes and generates data for their attributes

    Args:
        nb_depots (int): total number of available depots
        nb_customers (int): total number of customers
        nb_trucks (int): total number of available trucks
    """

    id_list = np.arange(nb_customers + nb_depots)
   
    depos = generatesInputDepos(nb_depots, id_list[:nb_depots])
    customers = generatesInputCustomers(nb_customers, id_list[nb_depots : nb_depots + nb_customers])
    trucks = generatesInputTrucks(nb_trucks)

    return depos, customers, trucks


if __name__ == "__main__":
    stuff = generateInput(2, 5, 10)
    costs = generateCostsBetweenNodes(depos = stuff[0], customers = stuff[1])
    print(costs)
    print("done")
