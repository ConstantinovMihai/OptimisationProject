import pickle
from SimpleVRP import plotSolution

with open('solutions2/solutions_depot_capacity11_24_34.pickle', 'rb') as f:
    loaded_obj = pickle.load(f, encoding= 'unicode_escape')

    plotSolution(loaded_obj, "depot_capacity")


print(loaded_obj)