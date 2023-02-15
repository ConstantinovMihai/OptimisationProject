import numpy as np
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import matplotlib.pyplot as plt


fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

x = np.arange(0,100,0.01)
y = np.arange(0,100,0.01)
x, y = np.meshgrid(x,y)
z = ((1/10*np.sin(x/100) + 1/100*np.sin(x/3) + 1/10*np.sin(x/10) + 1/10*np.sin(x/1000))*100 +
    (1/10*np.cos(y/100) + 1/100*np.cos(y/3) + 1/10*np.cos(y/10) + 1/10*np.cos(y/1000))*100)

surf = ax.plot_surface(x, y, z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

# Customize the z axis.
ax.set_zlim(-100, 100)
ax.zaxis.set_major_locator(LinearLocator(10))
# A StrMethodFormatter is used automatically
ax.zaxis.set_major_formatter('{x:.02f}')

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()