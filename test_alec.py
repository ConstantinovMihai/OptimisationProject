import numpy as np
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import matplotlib.pyplot as plt
from scipy.integrate import quad

point1 = [20,20]
point2 = [60,60]

x = np.arange(0,100,0.1)
y = np.arange(0,100,0.1)
x, y = np.meshgrid(x,y)

x_line = np.linspace(point2[0],point1[0], 100)
y_line = np.linspace(point2[1],point1[1], 100)

def F(x,y):
    # similiar to terrain, generate a congestion field over the map
    cong_factor = ((1/10*np.sin(x/100) + 1/100*np.sin(x/3) + 1/10*np.sin(x/10) + 1/10*np.sin(x/1000))*100 +
    (1/10*np.cos(y/100) + 1/100*np.cos(y/3) + 1/10*np.cos(y/10) + 1/10*np.cos(y/1000))*100)
    return cong_factor

z = ((1/10*np.sin(x/100) + 1/100*np.sin(x/3) + 1/10*np.sin(x/10) + 1/10*np.sin(x/1000))*100 +
        (1/10*np.cos(y/100) + 1/100*np.cos(y/3) + 1/10*np.cos(y/10) + 1/10*np.cos(y/1000))*100)
    
def r(t): 
    # parametrize the vector from one node to the other       
    return (point2[0]-point1[0])*t, (point2[1]-point1[1])*t
        
def integrand(t):
    x,y = r(t)
    return F(x,y)

# integrate the line through the scalar field
I, e = quad(integrand, 0.0, 1.0)

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

surf = ax.plot_surface(x, y, z, cmap='spring', alpha = 0.7)

ax.plot(point1, point2, color='grey', linewidth=1, linestyle='dashed')

ax.plot(x_line, y_line, F(x_line,y_line),  linewidth=1, color='black')

# Customize the z axis.
ax.set_zlim(-100, 100)
ax.zaxis.set_major_locator(LinearLocator(10))
# A StrMethodFormatter is used automatically
ax.zaxis.set_major_formatter('{x:.02f}')

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()