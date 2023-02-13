import pickle

file = open('inp_out.pickle','rb')
data = pickle.load(file)

print(data)

(vars,depots, customers, trucks, nodes, costs) = data

print(depots[1].id)
print(depots[1].x)
