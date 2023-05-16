import modification as m
import pygame as pg
from random import randint, gauss

pg.init()
pg.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

SCREEN_SIZE = (800, 600)

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
        self.gun = m.Cannon()
        self.rival = m.Rival_cannon()
        self.targets = []
        self.rectangle_targets = []
        self.score_t = ScoreTable()
        self.plane = m.Plane([0,0])
        self.n_targets = n_targets
        self.bullets = []
        self.new_mission()
        
        

    def new_mission(self):
        '''
        Adds new targets.
        '''
        for i in range(self.n_targets):
            self.targets.append(m.MovingTargets(rad=randint(max(1, 30 - 2*max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))
            self.targets.append(m.Target(rad=randint(max(1, 30 - 2*max(0, self.score_t.score())),
                30 - max(0, self.score_t.score()))))

        for i in range(5):  # Create 5 rectangle targets
            width = 50  # Specify the width of the rectangle target
            height = 25  # Specify the height of the rectangle target
            x = randint(0, SCREEN_SIZE[0] - width)  # Generate random x-coordinate within screen width
            y = randint(0, SCREEN_SIZE[1] - height)  # Generate random y-coordinate within screen height
            self.rectangle_targets.append(m.RectangleTarget(width, height, x, y))  

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
                    self.gun.move(0,-5)
                if event.key == pg.K_LEFT:
                    self.gun.move(-5,0)
                if event.key == pg.K_RIGHT:
                    self.gun.move(5,0)
                elif event.key == pg.K_DOWN:
                    self.gun.move(0,5)
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
        for target in self.rectangle_targets:
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