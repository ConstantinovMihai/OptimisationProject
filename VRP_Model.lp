\ Model VRP
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize multi-objectives
  OBJ0: Priority=1 Weight=1 AbsTol=1e-06 RelTol=0
   27.43711445805983 x_01 + 27.43711445805983 x_10 + 93.10374901564694 y_0
   + 67.76439341641453 a_01
Subject To
 customer_visited1: x_01 + x_11 = 1
 flow_cons1: - x_01 + a_01 = 0
 return_to_depot0: x_01 - a_01 = 0
 arc_orientation00: 2 x_00 <= 1
 arc_orientation01: x_01 + x_10 <= 1
 arc_orientation10: x_01 + x_10 <= 1
 arc_orientation11: 2 x_11 <= 1
 flow_balance1: t_01 - t_10 = 16.65942178476886
 cycle_prevention: x_00 + x_01 + x_10 + x_11 = 1
 demand_facility1: f_01 <= 1
 veh_cap00: - 116.6278228834015 x_00 + t_00 <= 0
 veh_cap01: - 116.6278228834015 x_01 + t_01 <= 0
 veh_cap10: - 116.6278228834015 x_10 + t_10 <= 0
 veh_cap11: - 116.6278228834015 x_11 + t_11 <= 0
 depot_activation0: - 552.7889680388456 y_0 + t_01 <= 0
 no_outp_termi1: x_10 + x_11 + z_1 = 1
 viewing_constr01: - f_01 - z_1 + a_01 >= -1
 arcs1000: 2 x_00 <= 1
 arcs1001: x_01 + x_10 - f_00 + f_01 <= 1
 arcs1010: x_01 + x_10 + f_00 - f_01 <= 1
 arcs1011: 2 x_11 <= 1
 arcs2000: 2 x_00 <= 1
 arcs2001: x_01 + x_10 + f_00 - f_01 <= 1
 arcs2010: x_01 + x_10 - f_00 + f_01 <= 1
 arcs2011: 2 x_11 <= 1
 depot_con01: - x_01 + f_01 >= 0
 min_depots0: 552.7889680388456 y_0 >= 16.65942178476886
 depot_route_cap0: x_01 <= 4.739769245212573
 client_dem: x_01 >= 0.1428426028446411
Bounds
Binaries
 x_00 x_01 x_10 x_11 y_0 f_00 f_01 z_1 a_01 t_00 t_01 t_10 t_11
End
