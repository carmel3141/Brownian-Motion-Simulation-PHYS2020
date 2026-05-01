import numpy as np
import matplotlib.pyplot as plt


def random_walk_2d(n):
    moves = np.array([[0,1],[0,-1],[1,0],[-1,0]])

    steps = np.random.choice(4, size=n)
    position = np.cumsum(moves[steps], axis=0)

    return position


n = 10000
dt = 0.01

position = random_walk_2d(n)

x, y = position[:, 0], position[:, 1]
t = np.arange(n) * dt


# --- plot trajectory ---
plt.plot(x, y)
plt.scatter(0, 0, color='red', label='Start')
plt.scatter(x[-1], y[-1], color='black', label='End')

plt.title(f"2D Random Walk ({n} steps)")
plt.legend()
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

