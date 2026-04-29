import numpy as np
import matplotlib.pyplot as plt


for i in range(5):
    n=1000
    moves = np.array([[0,1],[0,-1],[1,0],[-1,0]])

    random_walk = np.random.choice(4, size=n)
    steps = moves[random_walk]


    position = np.cumsum(steps,axis=0)
    x, y = position[:, 0], position[:, 1]

    plt.plot(position[:,0], position[:,1])
    plt.scatter(0, 0, color='red', label='Start')
    plt.scatter(x[-1],y[-1],color='black', label='End')
    plt.title(f"2D Random Walk ({n} Steps)")
    plt.legend()
    plt.show()


### Direct Displacement (Will do two types)

##def direct_MSD(position)
  ##  position 
  ##  displacements = position - position[0]
  ##  sq_disp = np.sum(displacements**2, axis=1)
 ##   return sq_disp



##will do one based on dx,dy,dt (based off of 2013 brownian motion lab document)









## need to figure out how to make it do it live and so i know where it is at each step

