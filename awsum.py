#! /usr/bin/env python
 
import pygame
 
bgcolor = 0, 0, 0
blueval = 0
bluedir = 1
x = y = 0
running = 1
screen = pygame.display.set_mode((640, 640))
height = 640
width = 640
top = 0
bottom = height - 1
left = 0
right = width - 1
while running:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = 0
    elif event.type == pygame.MOUSEMOTION:
        x, y = event.pos

    screen.fill(bgcolor)
    #pygame.draw.line(screen, (0, 0, blueval), (x, y+50), (x, y-50))
    #pygame.draw.line(screen, (0, 0, blueval), (x-50, y), (x+50, y))
    pygame.draw.line(screen, (blueval, 0, blueval), (x, y), (left, bottom))
    pygame.draw.line(screen, (0, blueval, blueval), (x, y), (right, bottom))
    blueval += bluedir
    if blueval == 255 or blueval == 0: bluedir *= -1     
    pygame.display.flip()