import pygame
import random
from Particle import Particle
from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 800,600
win = pygame.display.set_mode((WIDTH,HEIGHT))
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("particle Simulation")

font = pygame.font.SysFont(None, 24)


G = pygame.Vector2(0,0)
FPS = 60


particle_list=[]


def spawnRandom(n, vel_min, vel_max, r_min, r_max):
    for i in range(n):
        pos = (random.randint(1,WIDTH-1), random.randint(1,HEIGHT-1))
        radius = random.randint(r_min,r_max)
        color =(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        vel = pygame.Vector2(random.randint(vel_min, vel_max),random.randint(vel_min, vel_max))
        acc = pygame.Vector2(0,0)
        p = Particle(pos,radius,color,vel,acc)
        particle_list.append(p)


spawnRandom(50, -100, 100, 10, 30) 


def edge(particle, w, h, env_type):
    """
        Check that the particles do not escape from the environment
    """
    if env_type==1:
        if particle.pos.x + particle.radius > w:
            particle.pos.x = w - particle.radius
            particle.vel.x *= -1
            particle.vel *= particle.elasticity
        elif particle.pos.x - particle.radius < 0:
            particle.pos.x = particle.radius
            particle.vel.x *= -1
            particle.vel *= particle.elasticity

        if particle.pos.y + particle.radius > h:
            particle.pos.y = h - particle.radius
            particle.vel.y *= -1
            particle.vel *= particle.elasticity
        elif particle.pos.y - particle.radius < 0:
            particle.pos.y = particle.radius
            particle.vel.y *= -1
            particle.vel *= particle.elasticity
    elif env_type==2:
        if particle.pos.x > w+1:
            particle.pos.x = 0
        elif particle.pos.x < -1:
            particle.pos.x = w

        if particle.pos.y > h+1:
            particle.pos.y = 0
        elif particle.pos.y < -1:
            particle.pos.y = h
    elif env_type==3:
        if (particle.pos.x - particle.radius > w) or (particle.pos.x + particle.radius < 0) or (particle.pos.y - particle.radius > h) or (particle.pos.y + particle.radius < 0):
            particle_list.remove(particle)


def inside(p,other):
        """
            detect if another particle is inside it.
        """
        dist_squared = (p.pos - other.pos).magnitude_squared()
        if 0 < dist_squared < (p.radius + other.radius)**2:
            return True
        else:
            return False
    
def collision(type, p1, other):
    """
        Detects if two particles collide,
        if they do, it gets the new speeds for each one.

        The formula used is that of Collision elastic in two dimensions.
    """
    if inside(p1, other):
        if type==7: # simply bounce off each other
            # avoid division by zero
            dist_squared = max((p1.pos - other.pos).magnitude_squared(), 1)
            
            old_v1 = p1.vel
            old_v2 = other.vel
            common = 2/(p1.mass + other.mass)

            p1.vel = old_v1 - other.mass*common * ((old_v1-old_v2).dot(p1.pos-other.pos)/dist_squared) * (p1.pos-other.pos)
            other.vel = old_v2 - p1.mass*common * ((old_v2-old_v1).dot(other.pos-p1.pos)/dist_squared) * (other.pos-p1.pos)

            p1.vel  *= p1.elasticity
            other.vel *= other.elasticity

            # Move one of the two particles to avoid overlapping
            collide_dir = p1.pos - other.pos
            intercention = max(-collide_dir.magnitude()+p1.radius+other.radius, 1)
            r = random.randint(1, 2)
            if r == 1:
                p1.pos += collide_dir.normalize()*intercention
            else:
                other.pos += -collide_dir.normalize()*intercention

        elif type==8: # merges together
            new_mass = p1.mass + other.mass
            new_radius = (new_mass ** 0.5)  # Since radius squared gives mass

            
            # Center of mass calculation
            new_pos = (p1.pos * p1.mass + other.pos * other.mass) / new_mass
            new_vel = (p1.vel * p1.mass + other.vel * other.mass) / new_mass

            replace_particle = Particle(new_pos, new_radius, (p1.color if p1.radius>other.radius else other.color), new_vel, p1.acc + other.acc)
            particle_list.append(replace_particle)
            particle_list.remove(p1)
            particle_list.remove(other)
        




def main():
    running=True
    clock = pygame.time.Clock()


    #objects=[]
    mouse_down = False
    selected_obj = None

    env_type=1
    single_obj_pull = False
    pull_const = 2
    collision_type = 7
    spawn_radius = 20
    show_controls = True
    trails = True

    while running:

        delta = clock.tick(FPS)/1000

        mouse_pos = pygame.mouse.get_pos()


        for event in pygame.event.get():
            if event.type == QUIT:
                running=False
            elif event.type ==pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                if single_obj_pull:
                    for p in particle_list:
                        if p.mouse_over(mouse_pos):
                            selected_obj = p
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False
                selected_obj = None
            elif event.type==KEYDOWN:
                if event.key==K_1:
                    env_type = 1
                elif event.key==K_2:
                    env_type = 2
                elif event.key==K_3:
                    env_type = 3
                
                elif event.key==K_DOWN:
                    G.y+=1
                elif event.key==K_UP:
                    G.y-=1
                elif event.key==K_RIGHT:
                    G.x+=1
                elif event.key==K_LEFT:
                    G.x-=1
                elif event.key==K_a:
                    single_obj_pull = not single_obj_pull
                elif event.key==K_p:
                    pull_const *= -1
                elif event.key==K_7:
                    collision_type =7
                elif event.key==K_8:
                    collision_type =8
                elif event.key==K_9:
                    collision_type =9
                elif event.key==K_s:
                    particle_list.append(Particle(mouse_pos, spawn_radius, 'white', pygame.Vector2(0,0), pygame.Vector2(0,0)))
                elif event.key==K_i:
                    spawn_radius+=1
                elif event.key==K_k:
                    if spawn_radius>1:
                        spawn_radius-=1
                elif event.key==K_t:
                    trails = not trails
                elif event.key==K_DELETE:
                    if selected_obj:
                        particle_list.remove(selected_obj)
                elif event.key==K_c:
                    show_controls = not show_controls

        if trails:
            trail_surface.fill((225,225,225,220),special_flags=pygame.BLEND_RGBA_MULT)
        else:
            trail_surface.fill((0,0,0))

        for i, p in enumerate(particle_list):
            if mouse_down:
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                if not single_obj_pull:
                    dir = mouse_pos - p.pos
                    dist = dir.length()
                    

                    if dist!=0:
                        direction = dir.normalize()
                        pull_force = pull_const*p.mass/dist**2 #0.001*selected_obj.radius*dist
                        p.accelerate(pull_force*dir)
                        #selected_obj.vel *= 0.95 # damping effect

                else:
                    if selected_obj: #and p!= selected_obj:
                        dir = mouse_pos - selected_obj.pos
                        dist = dir.length()
                        

                        if dist!=0:
                            direction = dir.normalize()
                            pull_force = pull_const*selected_obj.mass*0.5/dist**2 #0.001*selected_obj.radius*dist
                            selected_obj.accelerate(pull_force*dir)
                            #selected_obj.vel *= 0.95 # damping effect


            p.accelerate(G)
            for p2 in particle_list[i+1:]:
                collision(collision_type,p,p2)
            edge(p, WIDTH, HEIGHT, env_type)
            p.update(delta)
            p.draw(trail_surface)

        pygame.display.update()
        win.fill("black")

        win.blit(trail_surface, (0,0))

        win.blit(font.render(f"controls: {'SHOWN' if show_controls else 'HIDDEN'} (c)", True, 'blue'), (20,20))

        if show_controls:
            
            win.blit(font.render(f"env type:{'box' if env_type==1 else 'loop' if env_type==2 else 'endless'} (1, 2 or 3)", True, 'blue'), (20,40))
            win.blit(font.render(f'G:{G} (direction arrows)', True, 'blue'), (20,60))
            win.blit(font.render(f"anchor push/pull {'ON' if mouse_down else 'OFF'} {selected_obj} (hold left mouse)", True, 'blue'), (20,80))
            win.blit(font.render(f"{'PUSHING' if pull_const<0 else 'PULLING'} (p) {'SINGLE' if single_obj_pull else 'ALL'} OBJECTS (a), (del) selected obj", True, 'blue'), (20,100))
            win.blit(font.render(f"collision type: {'BOUNCE' if collision_type==7 else 'MERGE' if collision_type==8 else 'NONE'} (7,8, or 9)", True, 'blue'), (20,120))
            win.blit(font.render(f"spawn (s) new object radius: {spawn_radius} (i/k to inc/dec)", True, 'blue'), (20,140))
            win.blit(font.render(f"trails: {'ON' if trails else 'OFF'} (t)", True, 'blue'), (20,160))



    pygame.quit()

if __name__ =="__main__":
    main()