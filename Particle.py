import pygame
import random

class Particle():
    def __init__(self,pos,radius,color,vel,acc):
        self.pos = pygame.Vector2(pos)
        self.color=color
        self.radius = radius
        self.mass= radius**2

        self.vel = vel # pygame.vector2
        self.acc = acc # pygame.vector2
        self.elasticity = 0.6


    def mouse_over(self, mouse_pos):
        return self.pos.distance_to(mouse_pos) <= self.radius

    def accelerate(self,acc):
        self.acc += acc

    def update(self,delta):
        self.vel+=self.acc
        self.acc=pygame.Vector2(0,0)

        self.pos+=self.vel*delta

    def draw(self,screen):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)

