import pygame
import sys
import math
import random
 
# window and box
width, height = 1050, 760
box_x, box_y  = 30, 30
box_w, box_h  = 680, 680
panel_x       = box_x + box_w + 20
 
# particle params
n_small = 40
r_small = 6
r_large = 25
m_small = 1.0
m_large = (r_large / r_small) ** 2   # mass proportional to area

# physics reference values
t_ref     = 300.0
t_min     = 50.0
t_max     = 800.0
eta_def   = 0.15
speed_ref = 4.0   # px/frame for small particles at t_ref
fps       = 60
dt        = 1 / fps


# trail and msd
trail_len = 300
msd_max   = 500   # how many msd samples to keep

 
fps   = 60
 
# colours
bg_col    = (255, 255, 255)
box_col   = (245, 245, 245)
wall_col  = (30,  30,  30)
small_col = (100, 150, 255)
large_col = (255, 180, 0)

#panel colours
panel_col  = (235, 235, 245)
text_col   = (40,  40,  40)
sl_bg_col  = (190, 190, 210)
sl_fg_col  = (90,  90,  200)
msd_col    = (200, 60,  60)
msd_bg_col = (215, 215, 228)
 
def v_small(T):
    # rms speed scales as sqrt(T) from maxwell-boltzmann
    return speed_ref * math.sqrt(T / t_ref)
 
def v_large_init(T):
    # heavier particle moves slower: v proportional to 1/sqrt(m)
    return v_small(T) * math.sqrt(m_small / m_large)

 
def random_vel(spd):
    angle = random.uniform(0, 2 * math.pi)
    return math.cos(angle) * spd, math.sin(angle) * spd
 
 
def init_particles(T):
    parts = []
    cx = box_x + box_w // 2
    cy = box_y + box_h // 2
    for _ in range(n_small):
        while True:
            x = random.uniform(box_x + r_small + 5, box_x + box_w - r_small - 5)
            y = random.uniform(box_y + r_small + 5, box_y + box_h - r_small - 5)
            if math.hypot(x - cx, y - cy) > r_large + r_small + 10:
                break
        vx, vy = random_vel(v_small(T))
        parts.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'r': r_small, 'm': m_small, 'large': False})
    vx, vy = random_vel(v_large_init(T))
    parts.append({'x': float(cx), 'y': float(cy), 'vx': vx, 'vy': vy, 'r': r_large, 'm': m_large, 'large': True})
    return parts

 
 
def bounce_walls(p):
    if p['x'] - p['r'] < box_x:
        p['x'] = box_x + p['r'];           p['vx'] = abs(p['vx'])
    elif p['x'] + p['r'] > box_x + box_w:
        p['x'] = box_x + box_w - p['r'];   p['vx'] = -abs(p['vx'])
    if p['y'] - p['r'] < box_y:
        p['y'] = box_y + p['r'];           p['vy'] = abs(p['vy'])
    elif p['y'] + p['r'] > box_y + box_h:
        p['y'] = box_y + box_h - p['r'];   p['vy'] = -abs(p['vy'])
 
 
def collide(p1, p2):
    # elastic collision - conserves momentum and kinetic energy
    dx = p2['x'] - p1['x'];  dy = p2['y'] - p1['y']
    dist = math.hypot(dx, dy)
    min_dist = p1['r'] + p2['r']
    if dist == 0 or dist >= min_dist:
        return
 
    # collision normal
    nx, ny = dx / dist, dy / dist
 
    # relative velocity along normal
    dvn = (p1['vx'] - p2['vx']) * nx + (p1['vy'] - p2['vy']) * ny
    if dvn <= 0:   # already moving apart, skip
        return
 
    m1, m2 = p1['m'], p2['m']
    imp = 2 * dvn / (m1 + m2)
 
    p1['vx'] -= imp * m2 * nx;  p1['vy'] -= imp * m2 * ny
    p2['vx'] += imp * m1 * nx;  p2['vy'] += imp * m1 * ny
 
    # push apart so they don't stick together
    overlap = min_dist - dist
    p1['x'] -= nx * overlap * m2 / (m1 + m2);  p1['y'] -= ny * overlap * m2 / (m1 + m2)
    p2['x'] += nx * overlap * m1 / (m1 + m2);  p2['y'] += ny * overlap * m1 / (m1 + m2)

def make_slider(label, x, y, w, vmin, vmax, vdef, fmt='.0f'):
    return {'label': label, 'x': x, 'y': y, 'w': w, 'min': vmin, 'max': vmax, 'val': vdef, 'fmt': fmt, 'drag': False}
 
def slider_hx(s):
    return int(s['x'] + (s['val'] - s['min']) / (s['max'] - s['min']) * s['w'])
 
def draw_slider(screen, s, font):
    pygame.draw.rect(screen, sl_bg_col, (s['x'], s['y'], s['w'], 6), border_radius=3)
    hx = slider_hx(s)
    pygame.draw.rect(screen, sl_fg_col, (s['x'], s['y'], hx - s['x'], 6), border_radius=3)
    pygame.draw.circle(screen, sl_fg_col, (hx, s['y'] + 3), 9)
    screen.blit(font.render(f"{s['label']}: {s['val']:{s['fmt']}}", True, text_col), (s['x'], s['y'] - 20))
 
def handle_slider(s, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if math.hypot(event.pos[0] - slider_hx(s), event.pos[1] - (s['y'] + 3)) < 12:
            s['drag'] = True
    elif event.type == pygame.MOUSEBUTTONUP:
        s['drag'] = False
    elif event.type == pygame.MOUSEMOTION and s['drag']:
        frac = (event.pos[0] - s['x']) / s['w']
        s['val'] = s['min'] + max(0.0, min(1.0, frac)) * (s['max'] - s['min'])
 
#msd mini plot in panel
def draw_msd_plot(screen, font, msd_data, px, py, pw, ph):
    pygame.draw.rect(screen, msd_bg_col, (px, py, pw, ph))
    pygame.draw.rect(screen, (150, 150, 170), (px, py, pw, ph), 1)
    screen.blit(font.render('MSD (px^2) vs time', True, text_col), (px, py - 20))
    if len(msd_data) < 2:
        return
    max_msd = max(msd_data) or 1
    n = len(msd_data)
    pts = [(px + int(i / n * pw), py + ph - int(v / max_msd * ph)) for i, v in enumerate(msd_data)]
    pygame.draw.lines(screen, msd_col, False, pts, 2)

 
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Brownian Motion - Basic Box')
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont('monospace', 14)
    font_b = pygame.font.SysFont('monospace', 14, bold=True)   # needed for PAUSED text
    #sliders
    sx     = panel_x + 10
    temp_s = make_slider('Temp (K)',  sx, 90,  220, t_min, t_max, t_ref)
    eta_s  = make_slider('Viscosity', sx, 165, 220, 0.0,   1.0,   eta_def, '.2f')

 
    particles = init_particles(t_ref)
    #tracking variables for trail and msd
    large            = particles[-1]
    start_x, start_y = large['x'], large['y']
    trail            = []
    msd_data         = []
    t_prev           = t_ref
    frame_n          = 0
    paused           = False

 
    running = True
    while running:
        clock.tick(fps)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    particles        = init_particles(temp_s['val'])
                    large            = particles[-1]
                    start_x, start_y = large['x'], large['y']
                    trail.clear();  msd_data.clear()
                    t_prev = temp_s['val'];  frame_n = 0
                elif event.key == pygame.K_SPACE: 
                    paused = not paused
            handle_slider(temp_s, event)  
            handle_slider(eta_s,  event)   

    #rescale all velocities when temperature slider moves (v proportional to sqrt(T))
        t_now = temp_s['val']
        if not paused and abs(t_now - t_prev) > 0.5:
            factor = math.sqrt(t_now / t_prev)
            for p in particles:
                p['vx'] *= factor;  p['vy'] *= factor
            t_prev = t_now
 
        if not paused:
            for p in particles:
                p['x'] += p['vx'];  p['y'] += p['vy']
 
            #stokes drag on large particle only: dv = -6*pi*eta*r*v*dt / m
            large  = particles[-1]
            drag_f = max(0.0, 1.0 - 6 * math.pi * eta_s['val'] * large['r'] * dt / large['m'])
            large['vx'] *= drag_f;  large['vy'] *= drag_f
 
            for p in particles:
                bounce_walls(p)
            for i in range(len(particles)):
                for j in range(i + 1, len(particles)):
                    collide(particles[i], particles[j])
            #trail and msd tracking
            trail.append((large['x'], large['y']))
            if len(trail) > trail_len:
                trail.pop(0)
            r2 = (large['x'] - start_x) ** 2 + (large['y'] - start_y) ** 2
            msd_data.append(r2)
            if len(msd_data) > msd_max:
                msd_data.pop(0)
            frame_n += 1

        # draw - fill first so trail and panel aren't wiped out
        screen.fill(bg_col)
        pygame.draw.rect(screen, box_col, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, wall_col, (box_x, box_y, box_w, box_h), 2)
        for p in particles:
            col = large_col if p['large'] else small_col
            pygame.draw.circle(screen, col, (int(p['x']), int(p['y'])), p['r'])

#trail
        if len(trail) > 1:
            for i in range(len(trail) - 1):
                c = int(50 + 200 * i / len(trail))
                pygame.draw.line(screen, (c, int(c * 0.6), 0),
                                 (int(trail[i][0]),   int(trail[i][1])),
                                 (int(trail[i+1][0]), int(trail[i+1][1])), 2)


#panel
        pygame.draw.rect(screen, panel_col, (panel_x, 0, width - panel_x, height))
        draw_slider(screen, temp_s, font)
        draw_slider(screen, eta_s,  font)
        large = particles[-1]
        spd   = math.hypot(large['vx'], large['vy'])
        y = 220
        for label, val in [('large speed', f'{spd:.2f} px/fr'),
                            ('msd now',    f'{msd_data[-1]:.0f} px^2' if msd_data else 'n/a'),
                            ('frame',      str(frame_n))]:
            screen.blit(font.render(f'{label}: {val}', True, text_col), (panel_x + 10, y))
            y += 22
        draw_msd_plot(screen, font, msd_data, panel_x + 10, 460, 220, 180)
        for i, txt in enumerate(['[R] reset', '[Space] pause', '[Q] quit']):
            screen.blit(font.render(txt, True, (150, 150, 150)), (panel_x + 10, height - 70 + i * 18))
        if paused:
            screen.blit(font_b.render('PAUSED', True, (200, 100, 0)), (box_x + 290, box_y + 325))

        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == '__main__':
    main()