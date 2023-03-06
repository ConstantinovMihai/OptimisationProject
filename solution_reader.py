import pickle
from SimpleVRP import plotSolution

with open('solutions/solutions_truck_cost18_14_49.pickle', 'rb') as f:
    loaded_obj = pickle.load(f, encoding= 'unicode_escape')

    plotSolution(loaded_obj, "truck_cost")


print(loaded_obj)