from gurobipy import Model, quicksum, GRB
from numpy import *
from time import *
from generate_input import generateInput, generateCostsBetweenNodes
import pickle


def VRP_Problem (depots, customers, trucks, nodes, costs):
    
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
            a[node_i.id,node_j.id] = model.addVar(vtype = "B", name = f"a{node_i.id}_{node_j.id}")

    t = {} # CV indicating the amount of cargo transported between nodes i and j
    for node_i in nodes:
        for node_j in nodes:
            t[node_i.id,node_j.id] = model.addVar(vtype = "C", name = f"t{node_i.id}_{node_j.id}")
    
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


    # HCECKKC of this is RIGHTSTSTTSTS
    min_depots = {} # 28 lower limit to the number of deposits that must be constructed according to the sum of the demands and the capacity of the facility
    # for node_i in depots:
    min_depots[0] = model.addConstr(quicksum(y[node_i.id]*node_i.cap for node_i in depots),">=",quicksum(node_j.demand for node_j in customers),name=f'min_depots{node_i.id}')

    depot_route_cap = {} # 29 number of routes that can leave a deposit is restricted according with the facility capacity and vehicle capacity
    for node_i in depots:    
        depot_route_cap[node_i.id] = model.addConstr(quicksum(x[node_i.id,node_j.id] for node_j in customers),'<=',node_i.cap/trucks[0].Q, name=f"depot_route_cap{node_i.id}")

    cient_dem = {} # 30 number of routes is sufficient to attend all clients demand
    cient_dem[0] = model.addConstr(quicksum(quicksum(x[node_i.id,node_j.id] for node_i in depots) for node_j in customers),'>=',quicksum(node_j.demand/trucks[0].Q for node_j in customers),name=f'client_dem')
    
    model.update()

    model.setObjectiveN(quicksum(node_i.cost*y[node_i.id] for node_i in depots)+
                        quicksum(quicksum(trucks[0].F*a[node_i.id,node_j.id] for node_i in depots) for node_j in customers)+
                        quicksum(quicksum(costs[node_i.id,node_j.id]*x[node_i.id,node_j.id] for node_i in nodes) for node_j in nodes)+
                        quicksum(quicksum(costs[node_i.id,node_j.id]*a[node_i.id,node_j.id] for node_i in depots) for node_j in customers), 0, 1)

    # model.setOjbectiveN(quicksum(costs[node_i.id,node_j.id]*x[node_i.id,node_j.id] for l in L for k in stations), 1, 0)

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
            model.write('VRP_model.ilp')
            print('\nThe following constraint(s) cannot be satisfied:')
            for c in model.getConstrs():
                if c.IISConstr:
                    print('%s' % c.constrName)
        elif status != GRB.Status.INF_OR_UNBD:
            print('Optimization was stopped with status %d' % status)
        exit(0)

    vars = {}
    for v in model.getVars():
        vars[v.varName] = v.x
        if v.x > 0:
            print('%s %g' % (v.varName, v.x))

    model.write("VRP_model.sol")

    data = (vars, depots, customers, trucks, nodes, costs)

    with open('inp_out.pickle', 'wb') as file:
        pickle.dump(data, file)
          
    print
   
    print
    print ("Objective Function =", round(model.ObjVal/1.0, 3))
    print ("------------------------------------------------------------------------")
    
    
    

if __name__ == '__main__':
    #=================================================================================================
    # Input excel file with arcs data (sheet1) and commodities data (sheet2)

    # I, J
    depots, customers, trucks = generateInput(3,15,6)

    # V
    nodes = [*depots, *customers]

    costs = generateCostsBetweenNodes(depots, customers)    

    for object in nodes:
        print(vars(object))
    for object in trucks:
        print(vars(object))

    #=================================================================================================
    start_time = time()
    
    VRP_Problem(depots, customers, trucks, nodes, costs)
    
    elapsed_time = time() - start_time

    print ("Run Time = ", round(elapsed_time, 4), '[s]')
    print ("END")
