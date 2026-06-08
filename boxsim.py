import pygame
import sys
import math
import random
import numpy as np 

# window 
width, height = 1050, 760
box_x, box_y  = 30, 30
box_w, box_h  = 680, 680
panel_x       = box_x + box_w + 20

# particle params
n_small = 60   # was 40
r_small = 6
m_small = 1.0
r_large_def = 25
r_large_min = 12
r_large_max  = 45

# physics
t_ref     = 300.0
t_min     = 50.0
t_max     = 800.0
eta_def   = 0.15
speed_ref = 4.0
fps       = 60
dt        = 1 / fps

# trail and msd 
trail_len = 300
msd_max   = 600
msd_fit_n = 200  

# colours
bg_col     = (255, 255, 255)
box_col    = (245, 245, 245)
wall_col   = (30,  30,  30)
small_col  = (100, 150, 255)
large_col  = (255, 180, 0)
panel_col  = (235, 235, 245)
text_col   = (40,  40,  40)
sl_bg_col  = (190, 190, 210)
sl_fg_col  = (90,  90,  200)
msd_col    = (200, 60,  60)
msd_bg_col = (215, 215, 228)
fit_col    = (60,  180, 60)  

def random_vel(spd):
    angle = random.uniform(0, 2 * math.pi)
    return math.cos(angle) * spd, math.sin(angle) * spd

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
    dx = p2['x'] - p1['x'];  dy = p2['y'] - p1['y']
    dist = math.hypot(dx, dy)
    min_dist = p1['r'] + p2['r']
    if dist == 0 or dist >= min_dist:
        return
    nx, ny = dx / dist, dy / dist
    dvn = (p1['vx'] - p2['vx']) * nx + (p1['vy'] - p2['vy']) * ny
    if dvn <= 0:
        return
    m1, m2 = p1['m'], p2['m']
    imp = 2 * dvn / (m1 + m2)
    p1['vx'] -= imp * m2 * nx;  p1['vy'] -= imp * m2 * ny
    p2['vx'] += imp * m1 * nx;  p2['vy'] += imp * m1 * ny
    overlap = min_dist - dist
    p1['x'] -= nx * overlap * m2 / (m1 + m2);  p1['y'] -= ny * overlap * m2 / (m1 + m2)
    p2['x'] += nx * overlap * m1 / (m1 + m2);  p2['y'] += ny * overlap * m1 / (m1 + m2)

def init_particles(T, r_large):
    m_large = (r_large / r_small) ** 2 * m_small
    parts = []
    cx = box_x + box_w // 2
    cy = box_y + box_h // 2
    for _ in range(n_small):
        while True:
            x = random.uniform(box_x + r_small + 5, box_x + box_w - r_small - 5)
            y = random.uniform(box_y + r_small + 5, box_y + box_h - r_small - 5)
            if math.hypot(x - cx, y - cy) > r_large + r_small + 10:
                break
        vx, vy = random_vel(speed_ref * math.sqrt(T / t_ref))
        parts.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'r': r_small, 'm': m_small, 'large': False})
    vx, vy = random_vel(speed_ref * math.sqrt(T / t_ref) * math.sqrt(m_small / m_large))
    parts.append({'x': float(cx), 'y': float(cy), 'vx': vx, 'vy': vy, 'r': r_large, 'm': m_large, 'large': True})
    return parts


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

# changed: now also draws the linear fit line if d_sim is available
def draw_msd_plot(screen, font, msd_data, d_sim, px, py, pw, ph):
    pygame.draw.rect(screen, msd_bg_col, (px, py, pw, ph))
    pygame.draw.rect(screen, (150, 150, 170), (px, py, pw, ph), 1)
    screen.blit(font.render('MSD (px^2) vs time', True, text_col), (px, py - 20))
    if len(msd_data) < 2:
        return
    max_msd = max(msd_data) or 1
    n = len(msd_data)
    pts = [(px + int(i / n * pw), py + ph - int(v / max_msd * ph)) for i, v in enumerate(msd_data)]
    pygame.draw.lines(screen, msd_col, False, pts, 2)
    #draw the fit line
    if d_sim is not None:
        y_end = min(4 * d_sim * (n - 1), max_msd)
        pygame.draw.line(screen, fit_col, (px, py + ph), (px + pw, py + ph - int(y_end / max_msd * ph)), 2)

#print summary on quit
def print_summary(large, temp_s, eta_s, msd_data, d_sim, frame_n):
    print(f"\n{'─'*48}")
    print(f"  Box Simulation Summary")
    print(f"{'─'*48}")
    print(f"  T={temp_s['val']:.0f}K   viscosity={eta_s['val']:.2f}   r_large={large['r']}px")
    print(f"  m_large={large['m']:.1f}   frames run={frame_n}")
    if d_sim is not None:
        d_r = d_sim * large['r']
        print(f"  D_sim: {d_sim:.3f} px^2/s  (windowed MSD / 4t, lag=30 frames)")
        print(f"  D*r:   {d_r:.2f}  (should be ~const as r changes - Stokes-Einstein)")
        print(f"  MSD points collected: {len(msd_data)}")
    else:
        print(f"  D: not enough data (need >= 50 frames)")
    print(f"{'─'*48}\n")


def main():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Brownian Motion Simulation')
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont('monospace', 13)
    font_b = pygame.font.SysFont('monospace', 14, bold=True)

    sx     = panel_x + 10
    temp_s = make_slider('Temp (K)',  sx, 90,  220, t_min,       t_max,       t_ref)
    eta_s  = make_slider('Viscosity', sx, 165, 220, 0.0,         1.0,         eta_def, '.2f')
    size_s = make_slider('Size (px)', sx, 240, 220, r_large_min, r_large_max, r_large_def)  

    particles        = init_particles(t_ref, r_large_def)
    large            = particles[-1]
    start_x, start_y = large['x'], large['y']
    trail            = []
    msd_data         = []
    d_sim            = None 
    t_prev           = t_ref
    r_prev           = r_large_def 
    frame_n          = 0
    paused           = False

    running = True
    while running:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print_summary(particles[-1], temp_s, eta_s, msd_data, d_sim, frame_n)   
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    print_summary(particles[-1], temp_s, eta_s, msd_data, d_sim, frame_n) 
                    running = False
                elif event.key == pygame.K_r:
                    r = int(size_s['val'])
                    particles        = init_particles(temp_s['val'], r)
                    large            = particles[-1]
                    start_x, start_y = large['x'], large['y']
                    trail.clear();  msd_data.clear()
                    t_prev = temp_s['val'];  r_prev = r;  frame_n = 0;  d_sim = None
                elif event.key == pygame.K_SPACE:
                    paused = not paused
            handle_slider(temp_s, event)
            handle_slider(eta_s,  event)
            handle_slider(size_s, event)  

        t_now = temp_s['val']
        if not paused and abs(t_now - t_prev) > 0.5:
            factor = math.sqrt(t_now / t_prev)
            for p in particles:
                p['vx'] *= factor;  p['vy'] *= factor
            t_prev = t_now

        #live size change - update large particle r and m, reset msd
        r_now = int(size_s['val'])
        if not paused and r_now != r_prev:
            large      = particles[-1]
            large['r'] = r_now
            large['m'] = (r_now / r_small) ** 2 * m_small
            large['x'] = max(box_x + r_now, min(box_x + box_w - r_now, large['x']))
            large['y'] = max(box_y + r_now, min(box_y + box_h - r_now, large['y']))
            start_x, start_y = large['x'], large['y']
            msd_data.clear();  trail.clear();  d_sim = None
            r_prev = r_now

        if not paused:
            for p in particles:
                p['x'] += p['vx'];  p['y'] += p['vy']
            large  = particles[-1]
            # drag scaled by 0.1 so velocity isn't killed between collisions
            drag_f = max(0.0, 1.0 - 6 * math.pi * eta_s['val'] * large['r'] * dt / large['m'] * 0.1)
            large['vx'] *= drag_f;  large['vy'] *= drag_f
            for p in particles:
                bounce_walls(p)
            for i in range(len(particles)):
                for j in range(i + 1, len(particles)):
                    collide(particles[i], particles[j])
            trail.append((large['x'], large['y']))
            if len(trail) > trail_len:
                trail.pop(0)

            # windowed msd: displacement over fixed lag, not from start
            # avoids bounded-box saturation (particle can't go >box_size from start)
            # for brownian motion: <r^2(lag)> = 4D * lag_time so D = mean(r^2) / (4*lag_time)
            lag = 30
            if len(trail) > lag:
                prev = trail[-(lag + 1)]
                r2 = (large['x'] - prev[0]) ** 2 + (large['y'] - prev[1]) ** 2
                msd_data.append(r2)
                if len(msd_data) > msd_max:
                    msd_data.pop(0)
            frame_n += 1

            if len(msd_data) >= 50:
                lag_time = lag / fps
                d_sim = max(0.0, float(np.mean(msd_data[-200:])) / (4.0 * lag_time))

        # draw 
        screen.fill(bg_col)
        pygame.draw.rect(screen, box_col,  (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, wall_col, (box_x, box_y, box_w, box_h), 2)
        if len(trail) > 1:
            for i in range(len(trail) - 1):
                c = int(50 + 200 * i / len(trail))
                pygame.draw.line(screen, (c, int(c * 0.6), 0),
                                 (int(trail[i][0]),   int(trail[i][1])),
                                 (int(trail[i+1][0]), int(trail[i+1][1])), 2)
        for p in particles:
            col = large_col if p['large'] else small_col
            pygame.draw.circle(screen, col, (int(p['x']), int(p['y'])), p['r'])

        pygame.draw.rect(screen, panel_col, (panel_x, 0, width - panel_x, height))
        draw_slider(screen, temp_s, font)
        draw_slider(screen, eta_s,  font)
        draw_slider(screen, size_s, font) 
        large = particles[-1]
        spd   = math.hypot(large['vx'], large['vy'])
        y = 310
        for label, val in [('large speed', f'{spd:.2f} px/fr'),
                            ('r_large',     f'{large["r"]} px'),
                            ('m_large',     f'{large["m"]:.1f}')]:
            screen.blit(font.render(f'{label}: {val}', True, text_col), (panel_x + 10, y))
            y += 20

        #D display
        y += 10
        if d_sim is not None:
            screen.blit(font_b.render('Diffusion:', True, text_col),                                   (panel_x + 10, y)); y += 20
            screen.blit(font.render(f'D_sim: {d_sim:.2f} px^2/s', True, text_col),                     (panel_x + 10, y)); y += 18
            screen.blit(font.render(f'D*r:   {d_sim * large["r"]:.1f} (const if SE)', True, text_col), (panel_x + 10, y))
        else:
            screen.blit(font.render('D: collecting...', True, (150, 150, 150)), (panel_x + 10, y))

        draw_msd_plot(screen, font, msd_data, d_sim, panel_x + 10, 490, 220, 170)
        for i, txt in enumerate(['[R] reset', '[Space] pause', '[Q] quit']):
            screen.blit(font.render(txt, True, (150, 150, 150)), (panel_x + 10, height - 70 + i * 18))
        if paused:
            screen.blit(font_b.render('PAUSED', True, (200, 100, 0)), (box_x + 290, box_y + 325))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()