import pygame
import sys
import math
import random

# window
W, H = 760, 760

#boundaries

bx, by, bw, bh = 40, 40, 680, 680

FPS = 60

#particles

n_small = 30
r_small = 5

n_large = 10
r_large = 20
speed = 5
m_small = 1
m_large = (r_large / r_small) ** 2 * m_small  # mass proportional to area

#colors
bg=(255, 255, 255)
col_small = (70 ,120, 210)
col_large = (220, 170, 30)
col_wall = (40, 40, 40)
col_tect = (100, 100, 100)

def random_vel(s):
    a = random.uniform(0,2*math.pi)
    return [math.cos(a)*s, math.sin(a)*s]

