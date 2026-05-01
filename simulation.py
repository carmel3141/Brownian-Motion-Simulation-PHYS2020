import numpy as np
import matplotlib.pyplot as plt


#time steps
n = 5000

# motion in x and y direction
x = np.cumsum(np.random.randn(n))
y = np.cumsum(np.random.randn(n))

# interpolate for smoothness 
k = 10
x2 = np.interp(np.arange(0, n, k), np.arange(n), x)
y2 = np.interp(np.arange(0, n, k), np.arange(n), y)

fig, ax = plt.subplots(1, 1, figsize=(8, 8))

#path and points
ax.plot(x2, y2, color='blue', linewidth=1, label='Brownian Motion')
ax.scatter(x2[0], y2[0], color='green', s=100, label='Start Point')
ax.scatter(x2[-1], y2[-1], color='red', s=100, label='End Point')

#cartesian
ax.axhline(0, color='gray', linewidth=0.5, linestyle='--')
ax.axvline(0, color='gray', linewidth=0.5, linestyle='--')
ax.set_xlabel('X Position')
ax.set_ylabel('Y Position')
ax.set_title('2D Brownian Motion Simulation')
ax.axis('equal')
ax.legend()
plt.show()

### Direct Displacement (Will do two types)

##def direct_MSD(position)
  ##  position 
  ##  displacements = position - position[0]
  ##  sq_disp = np.sum(displacements**2, axis=1)
 ##   return sq_disp



##will do one based on dx,dy,dt (based off of 2013 brownian motion lab document)





#i need to make it continuous instead of lattice



## need to figure out how to make it do it live and so i know where it is at each step

