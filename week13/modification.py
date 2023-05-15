import pygame as pg
import numpy as np
from random import randint

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

SCREEN_SIZE = (800, 600)

def rand_color():
    return (randint(0, 255), randint(0, 255), randint(0, 255))

class GameObject:

    def move(self):
        pass
    
    def draw(self, screen):
        pass  

class Shell(GameObject):
    '''
    The ball class. Creates a ball, controls it's movement and implement it's rendering.
    '''
    def __init__(self, coord, vel, rad=20, color=None):
        '''
        Constructor method. Initializes ball's parameters and initial values.
        '''
        self.coord = coord
        self.vel = vel
        if color == None:
            color = rand_color()
        self.color = color
        self.rad = rad
        self.is_alive = True

    def check_corners(self, refl_ort=0.8, refl_par=0.9):
        '''
        Reflects ball's velocity when ball bumps into the screen corners. Implemetns inelastic rebounce.
        '''
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1-i] = int(self.vel[1-i] * refl_par)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1-i] = int(self.vel[1-i] * refl_par)

    def move(self, time=1, grav=0):
        '''
        Moves the ball according to it's velocity and time step.
        Changes the ball's velocity due to gravitational force.
        '''
        self.vel[1] += grav
        for i in range(2):
            self.coord[i] += time * self.vel[i]
        self.check_corners()
        if self.vel[0]**2 + self.vel[1]**2 < 2**2 and self.coord[1] > SCREEN_SIZE[1] - 2*self.rad:
            self.is_alive = False

    def draw(self, screen):
        '''
        Draws the ball on appropriate surface.
        '''
        pg.draw.circle(screen, self.color, self.coord, self.rad)

class Cannon(GameObject):
    '''
    Cannon class. Manages it's renderring, movement and striking.
    '''
    def __init__(self, coord=[30, SCREEN_SIZE[1]//2], angle=0, max_pow=50, min_pow=10, color=RED):
        '''
        Constructor method. Sets coordinate, direction, minimum and maximum power and color of the gun.
        '''
        self.coord = coord
        self.angle = angle
        self.max_pow = max_pow
        self.min_pow = min_pow
        self.color = color
        self.active = False
        self.pow = min_pow
    
    def activate(self):
        '''
        Activates gun's charge.
        '''
        self.active = True

    def gain(self, inc=2):
        '''
        Increases current gun charge power.
        '''
        if self.active and self.pow < self.max_pow:
            self.pow += inc

    def strike(self):
        '''
        Creates ball, according to gun's direction and current charge power.
        '''
        vel = self.pow
        angle = self.angle
        ball = Shell(list(self.coord), [int(vel * np.cos(angle)), int(vel * np.sin(angle))])
        self.pow = self.min_pow
        self.active = False
        return ball
        
    def set_angle(self, target_pos):
        '''
        Sets gun's direction to target position.
        '''
        self.angle = np.arctan2(target_pos[1] - self.coord[1], target_pos[0] - self.coord[0])

    def move(self, inc):
        '''
        Changes vertical position of the gun.
        '''
        if (self.coord[1] > 30 or inc > 0) and (self.coord[1] < SCREEN_SIZE[1] - 30 or inc < 0):
            self.coord[1] += inc

    def draw(self, screen):
        '''
        Draws the gun on the screen.
        '''
        gun_shape = []
        vec_1 = np.array([int(5*np.cos(self.angle - np.pi/2)), int(5*np.sin(self.angle - np.pi/2))])
        vec_2 = np.array([int(self.pow*np.cos(self.angle)), int(self.pow*np.sin(self.angle))])
        gun_pos = np.array(self.coord)
        gun_shape.append((gun_pos + vec_1).tolist())
        gun_shape.append((gun_pos + vec_1 + vec_2).tolist())
        gun_shape.append((gun_pos + vec_2 - vec_1).tolist())
        gun_shape.append((gun_pos - vec_1).tolist())
        pg.draw.polygon(screen, self.color, gun_shape)

    def check_collision(self, bomb):
        '''
        Checks whether the bomb bumps into cannon.
        '''
        dist = sum([(self.coord[i] - bomb.coord[i])**2 for i in range(2)])**0.5
        #min_dist = self.rad + bomb.rad
        return dist <= bomb.rad
    

class Bullet(GameObject):
    '''
    rival cannon's bullet. Manages it's renderring, movement.
    '''
    def __init__(self, coord, vel = 20, rad = 15):
        '''
        constructor method, load bullet image and its radius, velocity.
        '''
        self.coord = coord
        self.vel = vel
        self.rad = rad
        self.bullet = pg.image.load('ball.png')
        self.bullet = pg.transform.scale(self.bullet,(15,15))
        self.count = 300

    def move(self):
        '''
        move method for bullet, move horizontally towards user cannon.
        '''
        self.coord[0] -= self.vel
            
    def draw(self, screen):
        '''
        draw the bullet
        '''
        screen.blit(self.bullet, self.coord)


class Rival_cannon(GameObject):
    '''
    Rival_cannon class. Manages it's renderring, movement and striking. This is the rival cannon.
    that attacks the user
    '''
    def __init__(self, coord=[770, SCREEN_SIZE[1]//2], angle=30, max_pow=50, min_pow=10, color=WHITE):
        '''
        Constructor method. Sets coordinate, direction, minimum and maximum power and color of the gun.
        '''
        self.coord = coord
        self.angle = angle
        self.max_pow = max_pow
        self.min_pow = min_pow
        self.color = color
        self.active = False
        self.pow = min_pow

    def move(self, cannon):
        '''
        move towards user cannon
        '''
        if(cannon.coord[1] != self.coord[1]):
            if(cannon.coord[1] > self.coord[1]):
                self.coord[1] += 3
            else:
                self.coord[1] -= 3

    def draw(self, screen):
        '''
        draw a rival cannon on the oposite side of our user cannon
        '''
        gun_shape = []
        vec_1 = np.array([int(5*np.cos(self.angle - np.pi/2)), int(5*np.sin(self.angle - np.pi/2))])
        vec_2 = np.array([int(self.pow*np.cos(self.angle)), int(self.pow*np.sin(self.angle))])
        gun_pos = np.array(self.coord)
        gun_shape.append((gun_pos + vec_1).tolist())
        gun_shape.append((gun_pos + vec_1 + vec_2).tolist())
        gun_shape.append((gun_pos + vec_2 - vec_1).tolist())
        gun_shape.append((gun_pos - vec_1).tolist())
        pg.draw.polygon(screen, self.color, gun_shape)

    def strike(self):
        '''
        strike method, let rival cannon shoot a bullet 
        return object bullet
        '''
        bullet = Bullet(list(self.coord))
        return bullet

class Bombs(GameObject):
    '''
    Bomb class. Creates a bomb from rival or target manages it's rendering and collision with a cannon event.
    '''

    def __init__(self, coord, vel, rad=15, color=WHITE):
        '''
        Constructor method. Initializes ball's parameters and initial values.
        '''
        self.coord = coord
        self.vel = vel
        self.color = color
        self.rad = rad
        self.is_alive = True
        self.bomb = pg.image.load('bomb.png')
        self.bomb = pg.transform.scale(self.bomb,(15,15))
    
    def check_corners(self, refl_ort=0.8, refl_par=0.9):
        '''
        Reflects bombs' velocity when bomb bumps into the screen corners. Implemetns inelastic rebounce.
        '''
        for i in range(2):
            if self.coord[i] < self.rad:
                self.coord[i] = self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
                self.vel[1-i] = int(self.vel[1-i] * refl_par)
            elif self.coord[i] > SCREEN_SIZE[i] - self.rad:
                self.coord[i] = SCREEN_SIZE[i] - self.rad
                self.vel[i] = -int(self.vel[i] * refl_ort)
             

    def move(self, time=1, grav=0):
        '''
        Moves the ball according to it's velocity and time step.
        Changes the ball's velocity due to gravitational force.
        '''
        self.vel[1] += grav
        for i in range(2):
            self.coord[i] += time * self.vel[i]
        self.check_corners()
        if self.vel[0]**2 + self.vel[1]**2 < 2**2 and self.coord[1] > SCREEN_SIZE[1] - 2*self.rad:
            self.is_alive = False
        #screen.blit(self.bomb, self.coord)

    def draw(self, screen):
        '''
        Draws the bomb on appropriate surface.
        '''
        #pg.draw.circle(screen, self.color, self.coord, self.rad)
        screen.blit(self.bomb, self.coord)

class Target(GameObject):
    '''
    Target class. Creates target, manages it's rendering and collision with a ball event.
    '''
    def __init__(self, coord=None, color=None, rad=30):
        '''
        Constructor method. Sets coordinate, color and radius of the target.
        '''
        if coord == None:
            coord = [randint(rad, SCREEN_SIZE[0] - rad), randint(rad, SCREEN_SIZE[1] - rad)]
        self.coord = coord
        self.rad = rad

        if color == None:
            color = rand_color()
        self.color = color

    def check_collision(self, ball):
        '''
        Checks whether the ball bumps into target.
        '''
        dist = sum([(self.coord[i] - ball.coord[i])**2 for i in range(2)])**0.5
        min_dist = self.rad + ball.rad
        return dist <= min_dist

    def draw(self, screen):
        '''
        Draws the target on the screen
        '''
        pg.draw.circle(screen, self.color, self.coord, self.rad)

    def move(self):
        """
        This type of target can't move at all.
        :return: None
        """
        pass
        

    def strike(self):
        '''
        Creates ball, according to gun's direction and current charge power.
        '''
        vel = randint(1,5)
        angle = randint(0,360)
        bomb = Bombs(list(self.coord), [int(vel * np.cos(angle)), int(vel * np.sin(angle))])
        return bomb

class Plane(GameObject):
    '''
    Create target that move very fast from diagonal
    '''
    def __init__(self, coord, rad = 30):
        '''
        Constructor method. Sets coordinate of the target.
        '''
        coord_set = [ [ 0, 0], [ 800, 0], [ 0, 600], [ 800, 600] ]
        self.position = randint(0,3) 
        coord = coord_set[self.position]
        self.coord = coord
        self.plane = pg.image.load('plane.png')
        self.plane = pg.transform.scale(self.plane,(30,30))
        self.rad = rad
    def move(self):
        '''
        Move the target plane from diagonal
        '''
        if(self.position == 0):
            if(self.coord[0] <= 800 and self.coord[1] <= 600):
                self.coord[0] += 10
                self.coord[1] = self.coord[0] * 0.75
        elif(self.position == 1):
            if(self.coord[0] >=0 and self.coord[1] <= 600):
                self.coord[0] -= 10
                self.coord[1] = -self.coord[0] * 0.75 + 600
        elif(self.position == 2):
            if(self.coord[0] <= 800 and self.coord[1] >= 0 ):
                self.coord[0] += 10
                self.coord[1] = -self.coord[0] * 0.75 + 600
        else:
            if(self.coord[0] >= 0  and self.coord[1] >= 0):
                self.coord[0] -= 10
                self.coord[1] =  self.coord[0] * 0.75
    def draw(self, screen):
        '''
        Draw a target plane from one corner of the screen
        '''
        screen.blit(self.plane, self.coord)   

class MovingTargets(Target):
    def __init__(self, coord=None, color=None, rad=30):
        super().__init__(coord, color, rad)
        self.vx = randint(-2, +2)
        self.vy = randint(-2, +2)
    
    def move(self):
        self.coord[0] += self.vx
        self.coord[1] += self.vy