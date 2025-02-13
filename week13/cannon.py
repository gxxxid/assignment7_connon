import numpy as np
import pygame as pg
from random import randint, gauss

pg.init()
pg.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
###
SADDLE = (139,69,19)

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
        self.coord = coord
        self.vel = vel
        self.rad = rad
        self.bullet = pg.image.load('ball.png')
        self.bullet = pg.transform.scale(self.bullet,(15,15))
        self.count = 300

    def move(self):
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
        bullet = Bullet(list(self.coord))
        return bullet


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

    
        



class MovingTargets(Target):
    def __init__(self, coord=None, color=None, rad=30):
        super().__init__(coord, color, rad)
        self.vx = randint(-2, +2)
        self.vy = randint(-2, +2)
    
    def move(self):
        self.coord[0] += self.vx
        self.coord[1] += self.vy


class ScoreTable:
    '''
    Score table class.
    '''
    def __init__(self, t_destr=0, b_used=0,h_score = 0):
        self.t_destr = t_destr
        self.b_used = b_used
        self.font = pg.font.SysFont("dejavusansmono", 25)
        self.h_score = h_score

    def score(self):
        '''
        Score calculation method.
        '''
        return self.t_destr - self.b_used - self.h_score

    def draw(self, screen):
        score_surf = []
        score_surf.append(self.font.render("Destroyed: {}".format(self.t_destr), True, WHITE))
        score_surf.append(self.font.render("Balls used: {}".format(self.b_used), True, WHITE))
        score_surf.append(self.font.render("Got hit: {}".format(self.h_score), True, WHITE))
        score_surf.append(self.font.render("Total: {}".format(self.score()), True, RED))
        
        for i in range(4):
            screen.blit(score_surf[i], [10, 10 + 30*i])


class Manager:
    '''
    Class that manages events' handling, ball's motion and collision, target creation, etc.
    '''
    def __init__(self, n_targets=1):
        self.balls = []
        self.bombs = []
        self.gun = Cannon()
        self.rival = Rival_cannon()
        self.targets = []
        self.score_t = ScoreTable()
        self.plane = Plane([0,0])
        self.n_targets = n_targets
        self.bullets = []
        self.new_mission()
        

    def new_mission(self):
        '''
        Adds new targets.
        '''
        for i in range(self.n_targets):
            self.targets.append(MovingTargets(rad=randint(max(1, 30 - 2*max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))
            self.targets.append(Target(rad=randint(max(1, 30 - 2*max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))


    def process(self, events, screen):
        '''
        Runs all necessary method for each iteration. Adds new targets, if previous are destroyed.
        '''
        done = self.handle_events(events)

        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            self.gun.set_angle(mouse_pos)
        
        self.move()
        self.collide()
        self.draw(screen)

        if len(self.targets) == 0 and len(self.balls) == 0:
            self.new_mission()

        return done

    def handle_events(self, events):
        '''
        Handles events from keyboard, mouse, etc.
        '''
        done = False
        for event in events:
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.gun.move(-5)
                elif event.key == pg.K_DOWN:
                    self.gun.move(5)
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.gun.activate()
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    self.balls.append(self.gun.strike())
                    for target in self.targets:
                        self.bombs.append(target.strike())
                    self.bullets.append(self.rival.strike())
                    self.score_t.b_used += 1

        return done

    def draw(self, screen):
        '''
        Runs balls', gun's, targets' and score table's drawing method.
        '''
        for ball in self.balls:
            ball.draw(screen)
        for target in self.targets:
            target.draw(screen)
        self.gun.draw(screen)
        self.rival.draw(screen)
        self.plane.draw(screen)
        self.score_t.draw(screen)

    def move(self):
        '''
        Runs balls' and gun's movement method, removes dead balls.
        '''
        self.plane.move()
        dead_balls = []
        for i, ball in enumerate(self.balls):
            ball.move(grav=2)
            if not ball.is_alive:
                dead_balls.append(i)
        for i in reversed(dead_balls):
            self.balls.pop(i)
        for i, target in enumerate(self.targets):
            target.move()
        for bomb in self.bombs:
            bomb.draw(screen)
            bomb.move()
        for bullet in self.bullets:
            bullet.draw(screen)
            bullet.move()
        self.rival.move(self.gun)
        
        self.gun.gain()

    def collide(self):
        '''
        Checks whether balls bump into targets, sets balls' alive trigger.
        '''
        collisions = []
        targets_c = []
        
        for i, ball in enumerate(self.balls):
            for j, target in enumerate(self.targets):
                if target.check_collision(ball):
                    collisions.append([i, j])
                    targets_c.append(j)
        targets_c.sort()
        for j in reversed(targets_c):
            self.score_t.t_destr += 1
            self.targets.pop(j)

        for i,bomb in enumerate(self.bombs):
            if(self.gun.check_collision(bomb)):
                self.score_t.h_score += 1

        for i, bullet in enumerate(self.bullets):
            if(self.gun.check_collision(bullet)):
                self.score_t.h_score += 1

        if(self.gun.check_collision(self.plane)):
            self.score_t.h_score += 1


screen = pg.display.set_mode(SCREEN_SIZE)
pg.display.set_caption("The gun of Khiryanov")

done = False
clock = pg.time.Clock()

mgr = Manager(n_targets=3)

while not done:
    clock.tick(15)
    screen.fill(BLACK)

    done = mgr.process(pg.event.get(), screen)

    pg.display.update()


pg.quit()