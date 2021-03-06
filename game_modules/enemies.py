import pygame
from math import sin, cos, degrees, atan, pi
import os

'''
Parent class for basic enemy features

spawn = (x, y) coordinates of top left of sprite of spawn point
'''
class Enemy(pygame.sprite.Sprite):
    def __init__(self, spawn:tuple, imageFileName, size:tuple):
        super().__init__()
        #loads image as pygame Surface object
        self.image = pygame.image.load(os.path.join("game_assets", imageFileName))
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()

        #saves spawn for game restart purposes
        self.spawn = spawn

        #variable for flipping sprite to face direction
        self.direction = 'right'

        #sets pygame rect positions to spawn
        self.rect.x = spawn[0]
        self.rect.y = spawn[1]

        #x and y position as floats for physics purposes(rect.y and rect.y cant be floats)
        self.x = spawn[0]
        self.y = spawn[1] 

'''
Spikes class that kill the player if touched

spawn = (x, y) coordinates of top left of sprite of spawn point
'''
class Spikes(Enemy):
    def __init__(self, spawn):
        super().__init__(spawn, "spikes.png", (50,50))
        self.type = 'spikes'

    '''
    Spikes do not need to be reinitialized
    '''
    def reinitialize(self):
        pass

    '''
    Spikes do not need to be updated each frame
    '''
    def update(self, **kwargs):
        pass


'''
Walking enemy that changes direction when it hits the edges of map

spawn = (x, y) coordinates of top left of sprite of spawn point
'''
class WalkingEnemy(Enemy):
    def __init__(self, spawn:tuple):
        super().__init__(spawn, "wolf.png", (70, 50))
        
        #default walks to the right on spawn
        self.velocityX = 3

        #type definition for map saving purposes(Object of type type is not JSON serializable)
        self.type = "walking"

    '''
    Method to reset state of enemy for when game restarts
    '''
    def reinitialize(self):
        self.rect.x = self.spawn[0]
        self.rect.y = self.spawn[1]
        self.x = self.spawn[0]
        self.y = self.spawn[1] 
        self.velocityX = 3

    '''
    Methods to walk left and right by changing velocity
    '''
    def walkLeft(self):
        if self.direction == 'right':
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = 'left'
        self.velocityX = -3

    def walkRight(self):
        if self.direction == 'left':
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = 'right'
        self.velocityX = 3
        
    '''
    Method to fall at a constant rate of 5 pixels per frame

    floorHeight: height of floor in pixels from bottom of screen
    platformsTouching: list of platforms that are colliding with the player
    '''
    def fall(self, floorHeight, platformsTouching):
        #test if player is above floor level to determine if grounded
        if self.rect.y + self.rect.height < 720 - floorHeight and platformsTouching == []:
            #falls by 5 pixels per inch when not during jump animation
            self.rect.y += 5
    
    '''
    Updates position of enemy by falling and sideways movement depending on velocity

    floorHeight: height of floor in pixels from bottom of screen
    screenSize: (width, height) of game screen
    platformsTouching: list of platforms that are colliding with the player
    '''
    def update(self, **kwargs):

        #walks left when reaches right boundary
        if self.rect.x + self.rect.width > kwargs['screenSize'][0]:
            self.walkLeft()

        #walks right when reaches left boundary
        elif self.rect.x < 0:
            self.walkRight()
        
        #updates horizontal position due to velocity
        self.rect.x += self.velocityX
        self.fall(kwargs['floorHeight'], kwargs['platformsTouching'])

'''
Class for flying enemy object
flies directly towards player

coordinates: (x, y) of top left corner of sprite
'''
class FlyingEnemy(Enemy):
    def __init__(self, spawn:tuple):
        super().__init__(spawn, "bird.png", (70, 50))

        #instaniates velocities
        self.velocityX = 0.0
        self.velocityY = 0.0

        #type definition for map saving purposes(Object of type type is not JSON serializable)
        self.type = "flying"

        #variable for flipping sprite to face direction
        self.direction = 'left'

    '''
    Method to reset state of enemy for when game restarts
    '''
    def reinitialize(self):
        self.rect.x = self.spawn[0]
        self.rect.y = self.spawn[1]
        self.x = self.spawn[0]
        self.y = self.spawn[1]
        self.velocityX = 0.0
        self.velocityY = 0.0

    '''
    Find the angle between the enemy and the player

    player: player object
    '''
    def find_angle(self, player):
        #calculating x and y displacement
        deltaX = player.rect.x - self.rect.x
        deltaY = player.rect.y - self.rect.y
        
        #special case to prevent division by 0
        if deltaX == 0:
            deltaX = 1 

        angle = atan(deltaY/deltaX)

        #cases where the angle is in the 2nd or 3rd quadrant
        if deltaX < 0:
            angle += pi

        return angle
    
    '''
    Updates flying enemy every frame
    moves towards player at a velocity of 1 pixel per frame

    coordinates = (x, y)
    '''
    def update(self, **kwargs):
        angle = self.find_angle(kwargs['player']) 
        
        #components of 1 pixel/frame velocity
        self.velocityX = cos(angle)
        self.velocityY = sin(angle)
        #add components to x and y position
        self.x += self.velocityX
        self.y += self.velocityY

        if self.velocityX < 0:
            if self.direction == 'right':
                self.image = pygame.transform.flip(self.image, True, False)
                self.direction = 'left'

        else:
            if self.direction == 'left':
                self.image = pygame.transform.flip(self.image, True, False)
                self.direction = 'right'

        #truncate x and y position to pygame sprite position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
