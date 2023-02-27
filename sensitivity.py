"""
This file contains the sensitivity analysis experiments we performed
"""

from SimpleVRP import *  

import numpy as np

a = np.array([[0,1,2], [4,5,6]])

print(np.sum(a, axis=(0,1)))
print(np.sum(a, axis=1))

# if __name__ == '__main__':
#     #=================================================================================================
#     # Input excel file with arcs data (sheet1) and commodities data (sheet2)

#     # I, J
#     depots, customers, trucks = generateInput(1,10,10)

#     # V
#     nodes = [*depots, *customers]

#     costs = generateCostsBetweenNodes(depots, customers)    
#     alpha, gamma, distance = generateAlphaGamma(depots, customers)

#     """ for object in nodes:
#         print(vars(object))
#     for object in trucks:
#         print(vars(object))
#     """
#     #=================================================================================================
#     start_time = time()
    
#     VRP_Problem(depots, customers, trucks, nodes, costs, alpha, gamma, distance)
    
#     elapsed_time = time() - start_time

#     print ("Run Time = ", round(elapsed_time, 4), '[s]')
#     print ("END")
