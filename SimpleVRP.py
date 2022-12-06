from gurobipy import Model, quicksum, GRB
from numpy import *
from openpyxl import *
from time import *

class CityPair:
    def __init__(self, origin, destination, cost):
        self.From   = origin
        self.To     = destination
        self.Cost   = cost

class City:
    def __init__(self, name):
        self.Name   = name

def VRP_Problem (CityPairs):
    
    model = Model("VRP")                # LP model (this is an object)
    
    x = {}                              # Decision Variables (DVs)
    for ij in range(len(CityPairs)):
        if CityPairs[ij].From != CityPairs[ij].To:
            x[CityPairs[ij].From,CityPairs[ij].To] = model.addVar(obj=CityPairs[ij].Cost, vtype ="B",
                                                name = "x"+CityPairs[ij].From+CityPairs[ij].To)
    
    model.update()                      

    Entering = {}                       # build 'capacity' constraints
    for i in range(len(Cities)):
        Entering[Cities[i].Name] = model.addConstr(quicksum(x[Cities[i].Name,Cities[j].Name] for j in range(len(Cities))),
                                                             '=', 1, name = 'Entering'+Cities[i].Name)                     
    
    Leaving = {}                       # build 'capacity' constraints
    for i in range(len(Cities)):
        Leaving[Cities[i].Name] = model.addConstr(quicksum(x[Cities[j].Name,Cities[i].Name] for j in range(len(Cities))),
                                                             '=', 1, name = 'Leaving'+Cities[i].Name)   

    model.update()
    model.write("VRP_Model.lp")
    model.optimize()
    
    status = model.status
    if status != GRB.Status.OPTIMAL:
        if status == GRB.Status.UNBOUNDED:
            print('The model cannot be solved because it is unbounded')
        elif status == GRB.Status.INFEASIBLE:
            print('The model is infeasible; computing IIS')
            model.computeIIS()
            print('\nThe following constraint(s) cannot be satisfied:')
            for c in model.getConstrs():
                if c.IISConstr:
                    print('%s' % c.constrName)
        elif status != GRB.Status.INF_OR_UNBD:
            print('Optimization was stopped with status %d' % status)
        exit(0)


    print
    # for k in range(len(Arcs)):
    #     Flow = 0
    #     for m in range(len(Commodities)):
    #         Flow += x[m,Arcs[k].From,Arcs[k].To].X
    #     if int(Flow)>0:
    #         print ("Arc(%d,%d) \t" %(Arcs[k].From + 1,Arcs[k].To + 1), int(Flow))
    #         print
    print
    print ("Objective Function =", model.ObjVal/1.0)
    print ("------------------------------------------------------------------------")
    
    
    

if __name__ == '__main__':
    #=================================================================================================
    # Input excel file with arcs data (sheet1) and commodities data (sheet2)
    CityPairs       = []
    Cities          = []
    
    wb = load_workbook("SimpleVRPData.xlsx", read_only=True)
    List_city_pairs = tuple(wb["Sheet1"].iter_rows())

    for i, origin in enumerate(List_city_pairs[1:]):
        for j, destination in enumerate(origin[1:]):
            new_pair = CityPair(List_city_pairs[i+1][0].value,List_city_pairs[0][j+1].value,int(destination.value))
            CityPairs.append(new_pair)

    for i, city in enumerate(List_city_pairs[0][1:]):
        new = City(city.value)
        Cities.append(new)

    for pair in Cities:
        print(vars(pair))

    
    # del new, NewNode
    #=================================================================================================
    start_time = time()
    # RUN MCF PROBLEM
    VRP_Problem(CityPairs)
    
    elapsed_time = time() - start_time

    print ("Run Time = ", elapsed_time)
    print ("END")
