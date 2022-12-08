from gurobipy import Model, quicksum, GRB
from numpy import *
from openpyxl import *
from time import *
from generate_input import generateInput

def VRP_Problem (depots, customers, trucks, nodes):
    
    model = Model("VRP")                # LP model (this is an object)
    
    x = {} # BV indicating the use of the path between nodes i,j
    for node_i in nodes:
        for node_j in nodes:
            x[node_i.id,node_j.id] = model.addVar(vtype ="B", name = f"x_{node_i.id}{node_j.id}")
    
    y = {} # BV indicating the use of facility i
    for depo in depots:
        y[depo.id] = model.addVar(vtype = "B", name = f"y_{depo.id}")

    f = {} # BV indicating if customer at node j is served by route that starts at depo at node i
    for node_i in depots:
        for node_j in customers:
            f[node_i.id,node_j.id] = model.addVar(vtype = "B", name =  f"x_{node_i.id}{node_j.id}")
    
    z = {} # BV if customer at node j is last one served in route
    for node_j in customers:
        z[node_j.id] = model.addVar(vtype = "B", name = f"z_{node_j.id}")

    a = {} # BV that indicates if a vehicle uses path j to return from the end of its route (at node j) to a depot (at node i)
    for node_i in depots:
        for node_j in customers:
            a[node_i.id,node_j.id] = model.addVar(vtype = "B", name = f"a_{node_i.id}{node_j.id}")

    t = {} # CV indicating the amount of cargo transported between nodes i and j
    for node_i in depots:
        for node_j in customers:
            t[node_i.id,node_j.id] = model.addVar(vtype = "B", name = f"t_{node_i.id}{node_j.id}")
    
    model.update()                      

    customer_visited = {} # the number of arcs arriving to a customer node must be 1, that is, every customer node is visited by a route.
    for node_j in customers:
        customer_visited[node_j.id] = model.addConstr(quicksum(x[node_i.id,node_j.id] for node_i in nodes),
                                                     '=', 1, name = f'customer_visited{node_j.id}')

    flow_conservation = {} #the sum of the arcs of output of a demand is equal to the sum of the input arcs:
    for node_j in customers:
        flow_conservation[node_j.id] = model.addConstr(quicksum(x[node_j.id,node_k.id] for node_k in customers)
                                                    +  quicksum(a[node_i.id,node_j.id] for node_i in depots),
                                                    '=', quicksum(x[node_i.id,node_j.id] for node_i in nodes),
                                                    name = f"flow_cons{node_j.id}") 

    return_to_depot = {} # for a facility i, the number of output arcs x must be equal to the number of arcs of arrival a                                                                              
    for node_i in depots:
        return_to_depot[node_i.id] = model.addConstr(quicksum(x[node_i.id,node_j.id] for node_j in customers),
                                                '=', quicksum(a[node_i.id,node_j.id] for node_j in customers),
                                                name = f'return_to_depot{node_i.id}')
        

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
   
    print
    print ("Objective Function =", model.ObjVal/1.0)
    print ("------------------------------------------------------------------------")
    
    
    

if __name__ == '__main__':
    #=================================================================================================
    # Input excel file with arcs data (sheet1) and commodities data (sheet2)

    # I, J
    depots, customers, trucks = generateInput(3,3,1)

    # V
    nodes = [*depots, *customers]    

    for object in nodes:
        print(vars(object))

    #=================================================================================================
    start_time = time()
    
    VRP_Problem(depots, customers, trucks, nodes)
    
    elapsed_time = time() - start_time

    print ("Run Time = ", elapsed_time)
    print ("END")
