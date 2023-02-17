""" This file generates input for the model, based on the definition of the classes from parameters.py"""

import numpy as np
from parameters import *
from scipy.integrate import quad

np.random.seed(422)

hourly_wage = 20 #euro/hour
avg_speed = 50 #km/h
truck_mass = 2000 # kg
grav_const = 9.81
F_wind = 
F_int = 
b = 


def generateTerrain(x,y):
    z = ((1/10*np.sin(x/100) + 1/100*np.sin(x/3) + 1/10*np.sin(x/10) + 1/10*np.sin(x/1000))*100 +
        (1/10*np.cos(y/100) + 1/100*np.cos(y/3) + 1/10*np.cos(y/10) + 1/10*np.cos(y/1000))*100)
    return z

def congestion_integral(point1, point2):

    def F(X):
        x, y = X
        cong_factor = ((1/10*np.sin(x/100) + 1/100*np.sin(x/3) + 1/10*np.sin(x/10) + 1/10*np.sin(x/1000))*100 +
        (1/10*np.cos(y/100) + 1/100*np.cos(y/3) + 1/10*np.cos(y/10) + 1/10*np.cos(y/1000))*100)
        return cong_factor
    
    def r(t):        
        return np.array([(point2.x-point1.x)*t, (point2.y-point1.y)*t])
           
    def integrand(t):
        return F(r(t))

    I, e = quad(integrand, 0.0, 1.0)
    # print(f'The integral is {I:1.4f}.')
    return I

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
        Wi = np.random.uniform(low=200, high=500)
        x = np.random.uniform(low=0, high=100)
        y = np.random.uniform(low=0, high=100)
        z = generateTerrain(x,y)
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
        z = generateTerrain(x,y)
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
        F = 80 # euro/day
        Q = 100 # units
        m = truck_mass # kg
        F_wind = max(np.random.normal(loc=30, scale=10), 10)
        F_int = max(np.random.normal(loc=30, scale=10), 10)
        E = max(np.random.normal(loc=30, scale=10), 10)
        new_customer = Truck(F, Q, m, F_wind, F_int, E, id = i)

        customers.append(new_customer)

    return customers


def generateDistanceBetweenNodes(depos, customers):
    """ Generates a matrix of distance from node i to node j

    Args:
        depos (list of Depos): list containing Depos objects
        customers (list of Customers): list containing Customer objects
    """

    def computeDistance(node1, node2):
        return np.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

    dist = np.zeros((len(depos) + len(customers), len(depos) + len(customers)))
    nodes = [*depos, *customers]


    for idx_i, node_i in enumerate(nodes):
        for idx_j, node_j in enumerate(nodes):
            dist[idx_i, idx_j] = computeDistance(node_i, node_j) # add here some gaussian noise or smth

    return dist

def generateCostsBetweenNodes(depos, customers):
    """ Generates a matrix of costs from node i to node j
        The model is based on the distance and an hourly wage. The congestion factor is also included as this will influence the duration of a trip

    Args:
        depos (list of Depos): list containing Depos objects
        customers (list of Customers): list containing Customer objects
    """
    
    hourly_wage = 20 #euro/hour
    avg_speed = 50 #km/h

    def computeDistance(node1, node2):
        return np.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

    costs = np.zeros((len(depos) + len(customers), len(depos) + len(customers)))
    nodes = [*depos, *customers]


    for idx_i, node_i in enumerate(nodes):
        for idx_j, node_j in enumerate(nodes):
            costs[idx_i, idx_j] = computeDistance(node_i, node_j)/avg_speed*hourly_wage*(1+congestion_integral(node_i,node_j)/100) # add here some gaussian noise or smth
            
    return costs

def generateAlphaGamma(depos, customers):
    """ Generates a matrix of the coefficients alpha and gamma from node i to node j

    Args:
        depos (list of Depos): list containing Depos objects
        customers (list of Customers): list containing Customer objects
    """
    
    

    def computeDistance(node1, node2):
        return np.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

    alpha = np.zeros((len(depos) + len(customers), len(depos) + len(customers)))
    gamma = np.zeros((len(depos) + len(customers), len(depos) + len(customers)))
    nodes = [*depos, *customers]

    

    for idx_i, node_i in enumerate(nodes):
        for idx_j, node_j in enumerate(nodes):
            d_ij = computeDistance(node_i,node_j)
            Beta = np.tan((node_j.z-node_i.z)/d_ij)
            alpha[idx_i, idx_j] = truck_mass*grav_const*(b*np.cos(Beta)+np.sin(Beta)*avg_speed**2/(2*grav_const*d_ij)) + F_wind + F_int
            gamma[idx_i, idx_j] = grav_const*(b*np.cos(Beta)+np.sin(Beta)*avg_speed**2/(2*grav_const*d_ij))
    return costs



def generateInput(nb_depots : int, nb_customers : int):
    """ creates the classes and generates data for their attributes

    Args:
        nb_depots (int): total number of available depots
        nb_customers (int): total number of customers
        nb_trucks (int): total number of available trucks
    """

    id_list = np.arange(nb_customers + nb_depots)
   
    depos = generatesInputDepos(nb_depots, id_list[:nb_depots])
    customers = generatesInputCustomers(nb_customers, id_list[nb_depots : nb_depots + nb_customers])
    trucks = generatesInputTrucks(1)

    return depos, customers, trucks


if __name__ == "__main__":
    stuff = generateInput(2, 5)
    costs = generateCostsBetweenNodes(depos = stuff[0], customers = stuff[1])
    print(costs)
    print("done")
