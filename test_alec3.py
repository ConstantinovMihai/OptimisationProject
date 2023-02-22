from mpl_toolkits.mplot3d import Axes3D
from matplotlib import pyplot as plt
import numpy as np

def f(x1, x2):
    return 0.5 * x1 + 0.6 * x2 + 0.2 * x1 * x1 + 0.1 * x1 * x2 + 0.3 * x2 * x2 + 4

def F(x,y):
    # similiar to terrain, generate a congestion field over the map
    cong_factor = ((1/10*np.sin(x/100) + 1/100*np.sin(x/3) + 1/10*np.sin(x/10) + 1/10*np.sin(x/1000))*100 +
    (1/10*np.cos(y/100) + 1/100*np.cos(y/3) + 1/10*np.cos(y/10) + 1/10*np.cos(y/1000))*100)
    return cong_factor

x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
xx, yy = np.meshgrid(x,y)
z = f(xx, yy)

# set up the figure
fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
ax.set_xlim(-3, 3)
ax.set_ylim(3, -3)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")

# plot the figure
ax.plot_surface(xx, yy, z, cmap="spring", alpha = 0.7)

# add the x=y line to the ground plane
ax.plot([-3, 3], [-3, 3], color='grey', linewidth=1, linestyle='dashed')

# add the x=-y line to the ground plane
ax.plot([3, -3], [-3, 3], color='grey', linewidth=1, linestyle='dashed')

ax.plot(x, x, F(x, x), color='dodgerblue')
ax.plot(x, -x, F(x, -x), color='dodgerblue')

plt.show()