from gurobipy import Model, quicksum, GRB
from numpy import *
from time import *
from generate_input import generateInput, generateCostsBetweenNodes, generateAlphaGamma
import pickle
import matplotlib.pyplot as plt
from datetime import datetime

def Run_Model(solutions, epsilon, first_run):

    model = Model("VRP")                # LP model (this is an object)
    x = {} # BV indicating the use of the path between nodes i,j
    for node_i in nodes:
        for node_j in nodes:
            x[node_i.id,node_j.id] = model.addVar(vtype ="B", name = f"x{node_i.id}_{node_j.id}")
    
    y = {} # BV indicating the use of facility i
    for depo in depots:
        y[depo.id] = model.addVar(vtype = "B", name = f"y_{depo.id}")

    f = {} # BV indicating if customer at node j is served by route that starts at depo at node i
    for node_i in depots:
        for node_j in nodes:
            f[node_i.id,node_j.id] = model.addVar(vtype = "B", name =  f"f{node_i.id}_{node_j.id}")
    
    z = {} # BV if customer at node j is last one served in route
    for node_j in customers:
        z[node_j.id] = model.addVar(vtype = "B", name = f"z_{node_j.id}")

    a = {} # BV that indicates if a vehicle uses path j to return from the end of its route (at node j) to a depot (at node i)
    for node_i in depots:
        for node_j in customers:
            a[node_i.id,node_j.id] = model.addVar(vtype = "B", name = f"a{node_j.id}_{node_i.id}")

    t = {} # CV indicating the amount of cargo transported between nodes i and j
    for node_i in nodes:
        for node_j in nodes:
            t[node_i.id,node_j.id] = model.addVar(vtype = "C", name = f"t{node_i.id}_{node_j.id}")

    money_obj = model.addVar(vtype = "C", name = f"money_objective value")
    emis_obj = model.addVar(vtype = "C", name = f"emis_objective value")
    
    model.update()                      

    customer_visited = {} # 14 the number of arcs arriving to a customer node must be 1, that is, every customer node is visited by a route.
    for node_j in customers:
        customer_visited[node_j.id] = model.addConstr(quicksum(x[node_i.id,node_j.id] for node_i in nodes),
                                                    '=', 1, name = f'customer_visited{node_j.id}')

    flow_conservation = {} # 15 the sum of the arcs of output of a demand is equal to the sum of the input arcs:
    for node_j in customers:
        flow_conservation[node_j.id] = model.addConstr(quicksum(x[node_j.id,node_k.id] for node_k in customers)
                                                    +  quicksum(a[node_i.id,node_j.id] for node_i in depots),
                                                    '=', quicksum(x[node_i.id,node_j.id] for node_i in nodes),
                                                    name = f"flow_cons{node_j.id}") 

    return_to_depot = {} # 16 for a facility i, the number of output arcs x must be equal to the number of arcs of arrival a                                                                              
    for node_i in depots:
        return_to_depot[node_i.id] = model.addConstr(quicksum(x[node_i.id,node_j.id] for node_j in customers),
                                                '=', quicksum(a[node_i.id,node_j.id] for node_j in customers),
                                                name = f'return_to_depot{node_i.id}')
    arc_orientation = {} # 17 avoid duplication of the arcs, the orientation of an arc is defined, i.e., if the direction is from i to j                                    
    for node_i in nodes:
        for node_j in nodes:
            arc_orientation[node_i.id,node_j.id] = model.addConstr(x[node_i.id,node_j.id]+x[node_j.id,node_i.id],"<=",1, name=f"arc_orientation{node_i.id}{node_j.id}")

    flow_balance = {} # 18 flow balance for node j  in terms of incoming and outgoing flows and demand at node j
    for node_j in customers:
        flow_balance[node_j.id] = model.addConstr(quicksum(t[node_i.id,node_j.id] for node_i in nodes if node_i.id != node_j.id),'=',
                                                quicksum(t[node_j.id,node_k.id] for node_k in nodes if node_k.id != node_j.id)+node_j.demand,name=f"flow_balance{node_j.id}")

    cycle_prevention = {} # 19 number of active arcs needed to connect all customer nodes assured that the routes are radials and do not have cycles
    cycle_prevention[0] = model.addConstr(quicksum(quicksum(x[node_i.id,node_j.id] for node_i in nodes) for node_j in nodes), '=', len(customers), name="cycle_prevention")

    demand_facility = {} # 20 demand for a route is connected to a facility
    for node_j in customers:
        demand_facility[node_j.id] = model.addConstr(quicksum(f[node_i.id,node_j.id] for node_i in depots),'<=',1, name=f"demand_facility{node_j.id}")

    vehicle_capacity = {} # 21 limits flow routes according to the capacity of the vehicles
    for node_i in nodes:
        for node_j in nodes:
            vehicle_capacity[node_i.id,node_j.id] = model.addConstr(t[node_i.id,node_j.id],'<=', trucks[0].Q*x[node_i.id,node_j.id], name=f"veh_cap{node_i.id}{node_j.id}")

    depot_activation = {} # 22 limits flows leaving a deposit according to the ability and decision to build the facility
    for node_i in depots:
        depot_activation[node_i.id] = model.addConstr(quicksum(t[node_i.id,node_j.id] for node_j in customers),"<=",node_i.cap*y[node_i.id], name=f"depot_activation{node_i.id}")

    no_outp_termi = {} # 23 identifies the terminal nodes of the routes when no output arc is demanded for that node. 
    for node_j in customers:
        no_outp_termi[node_j.id] = model.addConstr(quicksum(x[node_j.id,node_k.id] for node_k in nodes),"=", 1-z[node_j.id], name=f"no_outp_termi{node_j.id}")

    viewing_constr = {} # 24 if j is a terminal node, then the viewing constraint requires that there is a return arc
    for node_i in depots:
        for node_j in customers:
            viewing_constr[node_i.id,node_j.id] = model.addConstr(1+ a[node_i.id,node_j.id],">=", f[node_i.id,node_j.id]+z[node_j.id], name=f"viewing_constr{node_i.id}{node_j.id}")

    arcs1 = {} # 25 ensure that the active arcs are connected to the same facility to form the route
    for node_i in depots:
        for node_j in nodes:
            for node_u in nodes:
                arcs1[node_i.id, node_j.id, node_u.id] = model.addConstr(-(1-x[node_j.id,node_u.id]-x[node_u.id,node_j.id]),"<=",f[node_i.id,node_j.id]-f[node_i.id,node_u.id], name = f"arcs1{node_i.id}{node_j.id}{node_u.id}")

    arcs2 = {} # 26 ensure that the active arcs are connected to the same facility to form the route
    for node_i in depots:
        for node_j in nodes:
            for node_u in nodes:
                arcs2[node_i.id, node_j.id, node_u.id] = model.addConstr(f[node_i.id,node_j.id]-f[node_i.id,node_u.id],"<=",(1-x[node_j.id,node_u.id]-x[node_u.id,node_j.id]),name=f"arcs2{node_i.id}{node_j.id}{node_u.id}")

    depot_con = {} # 27 If the arc between facility i and demand j is active, then it is ensured that the node j is connected to the facility i
    for node_i in depots:
        for node_j in customers:
            depot_con[node_i.id,node_j.id] = model.addConstr(f[node_i.id,node_j.id],'>=',x[node_i.id,node_j.id],name=f"depot_con{node_i.id}{node_j.id}")


    min_depots = {} # 28 total depot capacity should exceed total customer demand
    # for node_i in depots:
    min_depots[0] = model.addConstr(quicksum(y[node_i.id]*node_i.cap for node_i in depots),">=",quicksum(node_j.demand for node_j in customers),name=f'min_depots{node_i.id}')

    depot_route_cap = {} # 29 number of routes that can leave a deposit is restricted according with the facility capacity and vehicle capacity
    for node_i in depots:    
        depot_route_cap[node_i.id] = model.addConstr(quicksum(x[node_i.id,node_j.id] for node_j in customers),'<=',node_i.cap/trucks[0].Q, name=f"depot_route_cap{node_i.id}")

    cient_dem = {} # 30 number of routes is sufficient to attend all clients demand
    cient_dem[0] = model.addConstr(quicksum(quicksum(x[node_i.id,node_j.id] for node_i in depots) for node_j in customers),'>=',quicksum(node_j.demand/trucks[0].Q for node_j in customers),name=f'client_dem')
    
    if not first_run:
        epsilon_obj = model.addConstr(quicksum(node_i.cost*y[node_i.id] for node_i in depots)+
                            quicksum(quicksum(trucks[0].F*a[node_i.id,node_j.id] for node_i in depots) for node_j in customers)+
                            quicksum(quicksum(costs[node_i.id,node_j.id]*x[node_i.id,node_j.id] for node_i in nodes) for node_j in nodes)+
                            quicksum(quicksum(costs[node_i.id,node_j.id]*a[node_i.id,node_j.id] for node_i in depots) for node_j in customers),'<=',epsilon,name=f'epsilon_constraint')

    money_obj_val_con = model.addConstr(quicksum(node_i.cost*y[node_i.id] for node_i in depots)+
                        quicksum(quicksum(trucks[0].F*a[node_i.id,node_j.id] for node_i in depots) for node_j in customers)+
                        quicksum(quicksum(costs[node_i.id,node_j.id]*x[node_i.id,node_j.id] for node_i in nodes) for node_j in nodes)+
                        quicksum(quicksum(costs[node_i.id,node_j.id]*a[node_i.id,node_j.id] for node_i in depots) for node_j in customers),'=',money_obj,name=f'money objectvie value')
    
    emis_obj_val_con = model.addConstr(quicksum(quicksum(alpha[node_i.id,node_j.id]*distance[node_i.id,node_j.id]*x[node_i.id,node_j.id] for node_i in nodes) for node_j in nodes) +
                            quicksum(quicksum(alpha[node_i.id,node_j.id]*distance[node_i.id,node_j.id]*a[node_i.id,node_j.id] for node_i in depots) for node_j in customers) +
                            quicksum(quicksum(gamma[node_i.id,node_j.id]*distance[node_i.id,node_j.id]*t[node_i.id,node_j.id] for node_i in nodes) for node_j in nodes),'=',emis_obj,name=f'emission objectvie value')

    model.update()

    if first_run:
        model.setObjective(quicksum(node_i.cost*y[node_i.id] for node_i in depots)+
                            quicksum(quicksum(trucks[0].F*a[node_i.id,node_j.id] for node_i in depots) for node_j in customers)+
                            quicksum(quicksum(costs[node_i.id,node_j.id]*x[node_i.id,node_j.id] for node_i in nodes) for node_j in nodes)+
                            quicksum(quicksum(costs[node_i.id,node_j.id]*a[node_i.id,node_j.id] for node_i in depots) for node_j in customers))
    else:
        model.setObjective(quicksum(quicksum(alpha[node_i.id,node_j.id]*distance[node_i.id,node_j.id]*x[node_i.id,node_j.id] for node_i in nodes) for node_j in nodes) +
                            quicksum(quicksum(alpha[node_i.id,node_j.id]*distance[node_i.id,node_j.id]*a[node_i.id,node_j.id] for node_i in depots) for node_j in customers) +
                            quicksum(quicksum(gamma[node_i.id,node_j.id]*distance[node_i.id,node_j.id]*t[node_i.id,node_j.id] for node_i in nodes) for node_j in nodes))

    model.update()
    model.setParam('MIPGap', 0.01)
    model.optimize()

    status = model.status
    if status != GRB.Status.OPTIMAL:
        if status == GRB.Status.UNBOUNDED:
            print('The model cannot be solved because it is unbounded')
        elif status == GRB.Status.INFEASIBLE:
            print('The model is infeasible; computing IIS')
            model.computeIIS()
            model.write('VRP_model.ilp')
            print('\nThe following constraint(s) cannot be satisfied:')
            for c in model.getConstrs():
                if c.IISConstr:
                    print('%s' % c.constrName)
        elif status != GRB.Status.INF_OR_UNBD:
            print('Optimization was stopped with status %d' % status)
        exit(0)

    # vars = {}
    # for v in model.getVars():
    #     vars[v.varName] = v.x
    #     if v.x > 0:
    #         print('%s %g' % (v.varName, v.x))

    # model.write("VRP_model.sol")

    # data = (vars, depots, customers, trucks, nodes, costs)

    # with open('inp_out.pickle', 'wb') as file:
    #     pickle.dump(data, file)
        
    # print(model.getVars()[-1].varName)
    # print ("Objective Function =", round(model.ObjVal/1.0, 3))
    # print ("------------------------------------------------------------------------")
    solutions[dP][epsilon] = {model.getVars()[-1].varName:model.getVars()[-1].x, model.getVars()[-2].varName:model.getVars()[-2].x}
    # solutions.append((epsilon,model.ObjVal,model.getVars()[-1].x))

    return solutions


def VRP_Problem (depots, customers, trucks, nodes, costs, alpha, gamma, distance):
    """_summary_

    Args:
        depots (_type_): _description_
        customers (_type_): _description_
        trucks (_type_): _description_
        nodes (_type_): _description_
        costs (_type_): _description_
        alpha (_type_): _description_
        gamma (_type_): _description_
        distance (_type_): _description_

    Returns:
        _type_: _description_
    """

    Run_Model(solutions, epsilon=0, first_run = True)

    # print(solutions)

    min_possible_money_cost = int(solutions[dP][0]['money_objective value'])

    for epsilon in linspace(min_possible_money_cost+1,min_possible_money_cost*10,10):
        # print(f"Model with epsilon {epsilon}")
        Run_Model(solutions, epsilon, first_run = False)       


def plotSolution(solutions, name_param):
    plt.clf()
    for dP in reversed(solutions):
        obj1 = []
        obj2 = []
        for sol in solutions[dP].items():
            obj1.append(sol[1]['emis_objective value'])
            obj2.append(sol[1]['money_objective value'])
        plt.scatter(obj2, obj1)
        plt.plot(obj2, obj1, label=f"{dP} X {name_param}")
    plt.legend()
    plt.grid()
    plt.xlabel(r'Money objective $\Psi_1$ value (\$)')
    plt.ylabel(r'Emission objective $\Psi_2$ value ($kg$ $C02$)')
    plt.savefig(f"solutions/{name_param}")

    
def saveResults(solutions, name_param, start_time):
   
    # elapsed_time = time() - start_time

    time = datetime.now().strftime("%H_%M_%S")
    with open(f'solutions/solutions_{name_param}{time}.pickle', 'wb') as f:
        pickle.dump(solutions, f)
    
    saveResults(solutions, name_param)

    print ("END")

        

if __name__ == '__main__':
    #=================================================================================================
    # Input excel file with arcs data (sheet1) and commodities data (sheet2)

    # I, J
    depots, customers, trucks = generateInput(3,9)

    # V
    nodes = [*depots, *customers]

    costs = generateCostsBetweenNodes(depots, customers)    
    alpha, gamma, distance = generateAlphaGamma(depots, customers)

    """ for object in nodes:
        print(vars(object))
    for object in trucks:
        print(vars(object))
    """
    #=================================================================================================

    start_time = time()

    solutions = {}
    # iterate among the amount of change to be applied
    for dP in [0.95, 1, 1.05]:
        # change the values of the depots
        solutions[dP] = {}
        
        for depot in depots:
            depot.cost = dP * depot.cost

        # run the model
        VRP_Problem(depots, customers, trucks, nodes, costs, alpha, gamma, distance)

        # undo the changes in the values of the depots
        for depot in depots:
            depot.cost = depot.cost / dP
    
    saveResults(solutions, "depots_cost", start_time)
      #=================================================================================================
    start_time = time()

    solutions = {}
    # iterate among the amount of change to be applied
    for dP in [0.95, 1, 1.05]:
        # change the values of the depots
        solutions[dP] = {}
        
        for depot in depots:
            depot.cap = dP * depot.cap

        # run the model
        VRP_Problem(depots, customers, trucks, nodes, costs, alpha, gamma, distance)

        # undo the changes in the values of the depots
        for depot in depots:
            depot.cap = depot.cap / dP
    
    saveResults(solutions, "depots_capacity", start_time)

      #=================================================================================================
    start_time = time()

    solutions = {}
    # iterate among the amount of change to be applied
    for dP in [0.95, 1, 1.05]:
        # change the values of the depots
        solutions[dP] = {}
        
        for truck in trucks:
           truck.Q = dP *  truck.Q

        # run the model
        VRP_Problem(depots, customers, trucks, nodes, costs, alpha, gamma, distance)

        # undo the changes in the values of the depots
          
        for truck in trucks:
           truck.Q = truck.Q / dP
    
    saveResults(solutions, "truck_capacity", start_time)
      #=================================================================================================
    
    start_time = time()

    solutions = {}
        # iterate among the amount of change to be applied
    for dP in [0.95, 1, 1.05]:
        # change the values of the depots
        solutions[dP] = {}
        
        for truck in trucks:
           truck.F = dP *  truck.F

        # run the model
        VRP_Problem(depots, customers, trucks, nodes, costs, alpha, gamma, distance)

        # undo the changes in the values of the depots
          
        for truck in trucks:
           truck.F = truck.F / dP
    
    saveResults(solutions, "truck_cost", start_time)
      #=================================================================================================
    start_time = time()

    solutions = {}
    # iterate among the amount of change to be applied
    for dP in [0.95, 1, 1.05]:
        # change the values of the depots
        solutions[dP] = {}
        
        for customer in customers:
            customer.demand = dP * customer.demand

        # run the model
        VRP_Problem(depots, customers, trucks, nodes, costs, alpha, gamma, distance)

        # undo the changes in the values of the depots
        for customer in customers:
            customer.demand = customer.demand / dP
    
    saveResults(solutions, "customer_demand", start_time)
      #=================================================================================================
    start_time = time()

    solutions = {}
    # iterate among the amount of change to be applied
    for dP in [0.95, 1, 1.05]:
        # change the values of the depots
        solutions[dP] = {}
        
        for x in range(len(distance)):
            for y in range(len(distance[x])):
                distance[x][y] = dP * distance[x][y]

        # run the model
        VRP_Problem(depots, customers, trucks, nodes, costs, alpha, gamma, distance)

        # undo the changes in the values of the depots
        for x in range(len(distance)):
            for y in range(len(distance[x])):
                distance[x][y] =  distance[x][y]/dP
    
    saveResults(solutions, "distance", start_time)
      #=================================================================================================
    start_time = time()

    solutions = {}
    # iterate among the amount of change to be applied
    for dP in [0.95, 1, 1.05]:
        # change the values of the depots
        solutions[dP] = {}
        
        for x in range(len(alpha)):
            for y in range(len(alpha[x])):
                alpha[x][y] = dP * alpha[x][y]

        for x in range(len(gamma)):
            for y in range(len(gamma[x])):
                gamma[x][y] = dP * gamma[x][y]

        # run the model
        VRP_Problem(depots, customers, trucks, nodes, costs, alpha, gamma, distance)

        # undo the changes in the values of the depots
        for x in range(len(alpha)):
            for y in range(len(alpha[x])):
                alpha[x][y] =  alpha[x][y]/dP

        for x in range(len(gamma)):
            for y in range(len(gamma[x])):
                gamma[x][y] = gamma[x][y]/dP

    saveResults(solutions, "alpha_beta", start_time)
      #=================================================================================================

    start_time = time()

    solutions = {}
    # iterate among the amount of change to be applied
    for dP in [0.95, 1, 1.05]:
        # change the values of the depots
        solutions[dP] = {}
        
        for x in range(len(costs)):
            for y in range(len(costs[x])):
                costs[x][y] = dP * costs[x][y]

       

        # run the model
        VRP_Problem(depots, customers, trucks, nodes, costs, alpha, gamma, distance)

        # undo the changes in the values of the depots
        for x in range(len(costs)):
            for y in range(len(costs[x])):
                costs[x][y] = costs[x][y]/dP

     

    saveResults(solutions, "route_costs", start_time)
      #=================================================================================================

