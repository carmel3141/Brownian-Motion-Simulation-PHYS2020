import numpy as np
import matplotlib.pyplot as plt


#time steps
n = 5000
dt= 0.01

t= np.arange(n)*dt

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

msd_total = np.zeros(n)
dx = x - x[0]
dy = y - y[0]

msd= dx**2 + dy**2
msd_total += msd

#msd plot
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(t, msd_total, color='purple', label='Mean Squared Displacement')
ax.set_xlabel('Time Step')
ax.set_ylabel('Mean Squared Displacement')
ax.set_title('MSD of Brownian Motion')
plt.show()

## need to figure out how to make it do it live and so i know where it is at each step

