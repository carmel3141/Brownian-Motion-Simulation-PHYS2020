import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.stats import linregress

#physical constants
kB = 1.380649e-23
T = 298
eta = 8.9e-4
a = 0.5e-6
D = kB * T / (6 * np.pi * eta * a)
print(f"Diffusion Coefficient: {D:.4e} m^2/s")

#parameters
n_particles = 30
n_steps = 800
dt = 0.05
scale = 1e6  # convert m to um for display
t = np.arange(n_steps) * dt

#trajectory, every step is N(0, sqrt(2*D*dt)) each axis, note that this is 2D, not 3D
sigma = np.sqrt(2 * D * dt)
x_all = np.cumsum(np.random.normal(0, sigma, (n_particles, n_steps)), axis=1) * scale
y_all = np.cumsum(np.random.normal(0, sigma, (n_particles, n_steps)), axis=1) * scale

#msd
dx = x_all - x_all[:, 0:1]
dy = y_all - y_all[:, 0:1]
msd = np.mean(dx**2 + dy**2, axis=0)

#fit msd=4Dt
slope, intercept, r, _, _ = linregress(t, msd)
D_fit = slope / 4 / (scale**2)  # convert back to m^2/s
print(f"Fitted Diffusion Coefficient: {D_fit:.4e} m^2/s")

#anim and fig
xi = x_all[0]
yi = y_all[0]
fig = plt.figure(figsize=(13, 6))
gs = fig.add_gridspec(1, 2, wspace=0.3)
ax_walk = fig.add_subplot(gs[0])
ax_msd = fig.add_subplot(gs[1])

#walk panel - background particles
for i in range(1, n_particles):
    ax_walk.plot(x_all[i], y_all[i], alpha=0.35)
ax_walk.scatter(x_all[1:, 0], y_all[1:, 0], color='green', alpha=0.5)
ax_walk.scatter(x_all[1:, -1], y_all[1:, -1], color='red', alpha=0.5)

# ax.plot() returns a list, the trailing comma unpacks it to get the Line2D directly
# blit=True requires Line2D objects, not lists, so this is necessary
# i know its a bit weird to explain this line but there was a bug that was cooking me so i thought i should clarify it
bg_line, = ax_walk.plot([], [], color='black', lw=0.8)
live_line, = ax_walk.plot([], [], color='red', lw=2)
live_dot, = ax_walk.plot([], [], 'o', color='green', markersize=8)

ax_walk.axhline(0, color='gray', lw=0.5, ls='--')
ax_walk.axvline(0, color='gray', lw=0.5, ls='--')
ax_walk.set_xlabel('X (um)')
ax_walk.set_ylabel('Y (um)')
ax_walk.set_title(f'2D Brownian motion | {n_particles} particles\nT={T}K, a={a*1e6:.1f}um, D={D:.2e} m^2/s')

#axis lims
pad = max(np.ptp(xi), np.ptp(yi)) * 0.15
ax_walk.set_xlim(xi.min() - pad, xi.max() + pad)
ax_walk.set_ylim(yi.min() - pad, yi.max() + pad)

#msd panel
ax_msd.plot(t, msd, label='Simulated MSD')
ax_msd.plot(t, 4 * D * (scale**2) * t, label=f'Theoretical: MSD=4Dt, D={D:.2e} m^2/s', ls='--')
ax_msd.plot(t, slope * t + intercept, label=f'Fit: D={D_fit:.2e} m^2/s, R^2={r**2:.3f}', ls=':')
ax_msd.set_xlabel('Time (s)')
ax_msd.set_ylabel('MSD (um^2)')
ax_msd.legend()
#hey i think u have to full screen for this lowk the fig doesn't always show up and sometimes is blank, i think tight layout is cooking it a bit, so fullscreen it plz

#anim
trail = 80
def init():
    bg_line.set_data([], [])
    live_line.set_data([], [])
    live_dot.set_data([], [])
    return bg_line, live_line, live_dot

def update(frame):
    f = frame + 1
    t0 = max(0, f - trail)
    bg_line.set_data(xi[:f], yi[:f])
    live_line.set_data(xi[t0:f], yi[t0:f])
    live_dot.set_data([xi[f-1]], [yi[f-1]])
    return bg_line, live_line, live_dot

ani = FuncAnimation(
    fig,
    update,
    frames=n_steps,
    init_func=init,
    interval=20,
    blit=True,
    repeat=False
)

plt.suptitle('Brownian Motion Simulation')
plt.tight_layout()
plt.show()