import pygame
import sys
import math
import random
 
# window and box
width, height = 800, 800
box_x, box_y  = 50, 50
box_w, box_h  = 700, 700
 
# particle params
n_small = 20
r_small = 6
r_large = 25
m_small = 1.0
m_large = (r_large / r_small) ** 2   # mass proportional to area
 
speed = 4   # all small particles same speed for now
fps   = 60
 
# colours
bg_col    = (255, 255, 255)
box_col   = (245, 245, 245)
wall_col  = (30,  30,  30)
small_col = (100, 150, 255)
large_col = (255, 180, 0)
 
 
def random_vel(spd):
    angle = random.uniform(0, 2 * math.pi)
    return math.cos(angle) * spd, math.sin(angle) * spd
 
 
def init_particles():
    parts = []
    cx = box_x + box_w // 2
    cy = box_y + box_h // 2
 
    # small fluid molecules - place randomly, avoid the centre where large one starts
    for _ in range(n_small):
        while True:
            x = random.uniform(box_x + r_small + 5, box_x + box_w - r_small - 5)
            y = random.uniform(box_y + r_small + 5, box_y + box_h - r_small - 5)
            if math.hypot(x - cx, y - cy) > r_large + r_small + 10:
                break
        vx, vy = random_vel(speed)
        parts.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'r': r_small, 'm': m_small, 'large': False})
 
    # large brownian particle in centre, starts slower because heavier (v proportional to 1/sqrt(m))
    vx, vy = random_vel(speed * math.sqrt(m_small / m_large))
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
 
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Brownian Motion - Basic Box')
    clock = pygame.time.Clock()
    font  = pygame.font.SysFont('monospace', 14)
 
    particles = init_particles()
 
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
                    particles = init_particles()
 
        # move
        for p in particles:
            p['x'] += p['vx'];  p['y'] += p['vy']
 
        # wall bounces
        for p in particles:
            bounce_walls(p)
 
        # check all pairs for collisions
        for i in range(len(particles)):
            for j in range(i + 1, len(particles)):
                collide(particles[i], particles[j])
 
        # draw
        screen.fill(bg_col)
        pygame.draw.rect(screen, box_col, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, wall_col, (box_x, box_y, box_w, box_h), 2)
        for p in particles:
            col = large_col if p['large'] else small_col
            pygame.draw.circle(screen, col, (int(p['x']), int(p['y'])), p['r'])
        screen.blit(font.render('[R] reset   [Q] quit', True, (150, 150, 150)), (box_x, box_y + box_h + 15))
        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == '__main__':
    main()
 
