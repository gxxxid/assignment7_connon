# python_programming_class
Python for programmers class

__Project completes the following tasks:__

    1. Implement various types of projectiles.
    
    2. Develop several target types with different movement patterns.
    
    3. Transform the cannon into a moving tank.
    
    4. Create "bombs" that will be dropped by targets onto the cannon.
    
    5. Implement multiple cannons that can shoot at each other.


__Changes made to the program__

     def move(self, inc_x, inc_y): 
        -added the ability to move the target left and right, the previous abilities of the gun were only up and down. 
        -made sure that the variables changing the left/right and up/down had valuable variable names (inc_x, inc_y)
        
     class bomb(Gameobject)
        makes the bomb, if cannon got hit by the bomb, get points off
        
     class Plane(Gameobject
        makes a plane that will move along the diagonal
    class Tank(GameObject):
        Draws the tank on the screen to be able to make a moc=ving tank
        
    def new_mission(self):
        adds new targets, calls the Rectangle class
        
    class RectangleTarget:
        draws the rectangles on the screen to be later called 
        
    class MovingTargets(Target):
        makes moving targets and a new location
        
__Group Members:__
Natalia Jauregui 
Haosi Lin
