import numpy as np
import matplotlib.pyplot as plt

n=1000
moves = np.array([[0,1],[0,-1],[1,0],[-1,0]])

random_walk = np.random.choice(4, size=n)
steps = moves[random_walk]


position = np.cumsum(steps,axis=0)
x, y = position[:, 0], position[:, 1]


plt.plot(position[:,0], position[:,1])
plt.scatter(0, 0, color='red', label='Start')
plt.scatter(x[-1],y[-1],color='black', label='End')
plt.show()

## need to figure out how to make it do it live and so i know where it is at each step

