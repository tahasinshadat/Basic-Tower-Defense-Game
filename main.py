import pygame, sys
from pygame.locals import QUIT
from enemyPath import waypoints
import math
from pygame.math import Vector2

pygame.init()
screen_width = 1000
screen_height = 532
FPS = 60
spawn_time = 150
spawn_frequency = 30
enemy_count = 0
money = 500
tower1_cost = 100
tower2_cost = 250
clock = pygame.time.Clock()
SCREEN = pygame.display.set_mode((screen_width, screen_height))
font = pygame.font.SysFont(None, 36) 
pygame.display.set_caption('Tower Defense')
background_map = pygame.image.load('graphics/MonkeyMeadow.webp').convert()
enemy_group = pygame.sprite.Group()
tower_group = pygame.sprite.Group()
tower2_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemies_killed = 0
tower1_image = pygame.image.load('graphics/turret.png').convert_alpha()
tower2_image = pygame.image.load('graphics/pixil-frame-0.png').convert_alpha()



def calculate_distance(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def draw_range_circle(screen, center_x, center_y, radius, transparency):
    color = (0, 0, 255, int(255 * transparency))  # Use the specified transparency

    circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(circle_surface, color, (radius, radius), radius)

    screen.blit(circle_surface, (center_x - radius, center_y - radius))

def draw_rectangle(screen, color, rect):
    pygame.draw.rect(screen, color, rect)

class Enemy(pygame.sprite.Sprite):

    def __init__(self, screen, waypoints, size, image_path):
        pygame.sprite.Sprite.__init__(self)
        self.offset = 0
        self.waypoints = [(waypoint[0] + self.offset, waypoint[1] + self.offset) for waypoint in waypoints]
        self.pos = self.waypoints[0]
        self.target_waypoints = 1
        self.size = size
        self.screen = screen
        self.color = 'blue'
        self.speed = 2
        

        # Load the enemy image and scale it to the desired size
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)

        # draw enemy
        self.rect = self.image.get_rect(center=self.pos)

        # Draw Health bar of enemy
        self.health = 100

        # Check for death
        self.dead = False

    def draw(self):
        self.screen.blit(self.image, self.rect)
        self.displayHealth()

    def update(self):
        self.move()
        # self.decreaseHealth(1)
        self.draw()
        if self.dead:
            self.delete()

    def move(self):
        # check if all the waypoints have been reached yet
        if self.target_waypoints < len(self.waypoints):

            self.target = Vector2(self.waypoints[self.target_waypoints])  # the difference between two points
            self.movement = self.target - self.pos  # represents the distance between the current position of the enemy and the target waypoint

            if self.movement.length() != 0:
                # .normalize() is a vector2 method that tells us how many pixels to move WDF
                # self.pos += self.movement.normalize() * self.speed # update the enemies current position to a point closer to the target waypoint

                # self.rect.center = self.pos # sets the center of the enemy to the current position

                # Check if the magnitude of self.movement is less than the speed, it means the enemy has reached the current waypoint
                if self.movement.length() <= self.speed:
                    self.pos = self.target
                    self.target_waypoints += 1  # go on to the next waypoint
                else:
                    # update the enemies current position to a point closer to the target waypoint
                    self.pos += self.movement.normalize() * self.speed
                    # sets the center of the enemy to the current position
                    self.rect.center = self.pos
        
        elif self.target_waypoints == len(self.waypoints):
            self.delete()

        # if not, then we reached the end of the path
        else:
            self.speed = 0

    def displayHealth(self):
        # Calculate width of the health bar based on the current amt of health
        health_bar_width = self.rect.width * (self.health / 100)
        health_bar_height = 5
        health_bar_position = (self.rect.x,
                               self.rect.y - health_bar_height - 5)
        health_color = (255, 0, 0)
        health_bar = pygame.Rect(health_bar_position,
                                 (health_bar_width, health_bar_height))
        draw_rectangle(self.screen, health_color, health_bar)

    def decreaseHealth(self, amount):
        self.health -= amount
        if self.health < 0:  # stops health bar at 0
            self.health = 0
            self.dead = True

    def delete(self):
        global enemies_killed, money
        enemies_killed += 1
        money += 5
        self.kill()  # built in function inside pygame's sprite class that deletes all an objects data

class Tower(pygame.sprite.Sprite):

    def __init__(self, screen, pos, size, image):
        pygame.sprite.Sprite.__init__(self)

        self.pos = pos
        self.size = size
        self.screen = screen
        self.color = 'blue'
        self.attack_speed = 1
        self.is_dropped = False
        self.clicked_on = 0
        self.bought = False
        self.bullet_group = pygame.sprite.Group()
        
        # Load the enemy image and scale it to the desired size
        self.original_image = image
        self.original_image = pygame.transform.scale(self.original_image, self.size)

        self.image = self.original_image

        # draw Tower
        self.rect = self.image.get_rect(center=self.pos)

        # attack attributes
        self.range = 110
        self.attack_timer = 0
        self.attack_cooldown = 60 / self.attack_speed

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def update(self):
        if self.is_dropped:
            # Check if it's time to attack
            if self.attack_timer >= self.attack_cooldown:
                enemy_to_attack = self.find_enemy()
                if enemy_to_attack:
                    self.rotate(enemy_to_attack.rect.center)
                    self.shoot_bullet(enemy_to_attack.rect.center)
            pass
        if self.clicked_on % 2 == 1:
            self.showRange()

        self.bullet_group.update()
        self.draw()
        self.rect.center = self.pos
        self.attack_timer += 1

    def shoot_bullet(self, enemy_pos):
        turret_position = (self.pos[0], self.pos[1])
        if self.attack_timer > self.attack_speed:
            if calculate_distance(turret_position, enemy_pos) < self.range:
                bullet = Bullet(self.screen, self.pos, enemy_pos, 'graphics/enemy.png')
                bullet_group.add(bullet)
                self.attack_timer = 0

    # Finds the enemy with the most progress in the road withint it's range (aka, the first enemy)
    def find_enemy(self):
        turret_position = Vector2(self.pos)
        max_progress_enemy = None
        max_progress = -1

        for enemy in enemy_group:
            enemy_position = Vector2(enemy.rect.center)
            distance = calculate_distance(turret_position, enemy_position)

            if distance <= self.range:
                progress = enemy.target_waypoints / len(enemy.waypoints)
                if progress > max_progress:
                    max_progress = progress
                    max_progress_enemy = enemy

        return max_progress_enemy
    
    def rotate(self, target_pos):
        # Calculate the angle between the tower's position and the target position
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        angle_rad = math.atan2(-dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Rotate the tower's image to the calculated angle
        self.image = pygame.transform.rotate(self.original_image, angle_deg)
        self.rect = self.image.get_rect(center=self.rect.center)

    def showRange(self):
        draw_range_circle(self.screen, self.pos[0], self.pos[1], self.range, 0.4)

class Bullet(pygame.sprite.Sprite):

    def __init__(self, screen, start_pos, target_pos, image_path):
        pygame.sprite.Sprite.__init__(self)

        self.pos = start_pos
        self.size = (10, 10)
        self.screen = screen
        self.color = 'blue'
        self.speed = 5
        self.target_pos = target_pos
        
        # Load the enemy image and scale it to the desired size
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def update(self):
        self.move()
        self.draw()

    def move(self):
        self.target = Vector2(self.target_pos)
        self.movement = self.target - self.pos
        self.pos += self.movement.normalize() * self.speed
        self.rect.center = self.pos
        if self.movement.length() <= self.speed:
            self.kill()
            del self

def display_message(screen, message, duration):
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

    pygame.time.wait(duration)

# create and adds a new enemy to the enemy_group
def create_enemy(speed, health):
    enemy = Enemy(SCREEN, waypoints, (50, 50), 'graphics/ballon.png')
    enemy_group.add(enemy)
    enemy.speed = speed
    enemy.health = health

# create and add a new tower to the tower_group
def create_tower():
    tower = Tower(SCREEN, [900, 100], (50, 50), tower1_image)
    tower_group.add(tower)  # Add the tower to the tower_group

def create_tower_2():
    tower2 = Tower(SCREEN, [900, 300], (60, 60), tower2_image)
    tower2.attack_speed = 2
    tower2.range = 125
    tower2.attack_cooldown = 60 / tower2.attack_speed  # Update attack cooldown based on attack speed
    tower2_group.add(tower2)

tower_count = 0
selected_tower = None
run = True
current_round = 0
round1_passed = False
tower_damage = 5

ROUNDS = [
    # Spawn Frequency, Enemy Count, Enemy Speed, Enemy Health

    [30, 15, 1, 25], # Round 1

    [25, 20, 1, 40], # Round 2

    [35, 25, 1.1, 60], # Round 3

    [20, 30, 1.2, 35], # Round 4

    [50, 35, 1.2, 80], # Round 5

    [20, 40, 1.2, 60], # Round 6

    [15, 50, 1.5, 50], # Round 7

    [25, 25, 1, 90], # Round 8

    [20, 30, 1.1, 100],  # Round 9

    [15, 35, 1.3, 120] # Round 10

]

while run:

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:  # check if left click is clicked      
                mouse_x, mouse_y = pygame.mouse.get_pos()  # get mouse positions
                click_rect = pygame.Rect(mouse_x, mouse_y, 1,1)  # create mouse rect/area
                
                for enemy in enemy_group:
                    if enemy.rect.colliderect(click_rect):  # check if there is a collision between rects
                        if selected_tower:
                            selected_tower.shoot_bullet(enemy.rect.center)

                for tower in tower_group:
                    if tower.rect.colliderect(click_rect):
                        if money >= tower1_cost:
                            tower.bought = True
                        if tower.bought:
                            tower.clicked_on += 1
                        if not tower.is_dropped:
                            if money >= tower1_cost:
                                tower.bought = True
                                money -= 100
                                selected_tower = tower
                                break

                for tower2 in tower2_group:
                    if tower2.rect.colliderect(click_rect):
                        if money >= tower2_cost:
                            tower2.bought = True
                        if tower2.bought:
                            tower2.clicked_on += 1
                        if not tower2.is_dropped:
                            if money >= tower2_cost:
                                tower2.bought = True
                                money -= 250
                                selected_tower = tower2
                                break
          
            
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse release
                if selected_tower:
                    selected_tower.is_dropped = True
                    selected_tower = None

        if selected_tower and not selected_tower.is_dropped:
            create_tower()
            create_tower_2()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            selected_tower.pos[0] = mouse_x
            selected_tower.pos[1] = mouse_y

    if spawn_time > ROUNDS[current_round][0] and enemy_count != ROUNDS[current_round][1]:
        create_enemy(ROUNDS[current_round][2], ROUNDS[current_round][3])
        spawn_time = 0
        enemy_count += 1
    else:
        spawn_time += 1

    if (enemies_killed == ROUNDS[current_round][1]): # Have killed all the enemies
        current_round += 1
        spawn_time = 0
        enemy_count = 0 
        enemies_killed = 0
        display_message(SCREEN, f'Round {current_round + 1}' , 2000)

    if tower_count < 1:
        create_tower()
        create_tower_2()
    
    if not round1_passed:
        display_message(SCREEN, f'Round {current_round + 1}' , 2000)
        round1_passed = True

    for bullet in bullet_group:
        collisions = pygame.sprite.spritecollide(bullet, enemy_group, False)
        if collisions:
            # If there's a collision, decrease the health of the first collided enemy
            enemy = collisions[0]
            enemy.decreaseHealth(tower_damage)

    SCREEN.fill((0, 0, 0))
    SCREEN.blit(background_map, (0, 0))  # everything after this line

    enemy_group.update()
    tower_group.update()
    enemy_group.draw(SCREEN)
    tower_group.draw(SCREEN)
    bullet_group.update()
    bullet_group.draw(SCREEN)
    tower2_group.update()
    tower2_group.draw(SCREEN)

    money_text = font.render(f"Money: {money}", True, (255, 255, 255))  # Render the money text
    SCREEN.blit(money_text, (10, 10)) 
    label_text = font.render("Towers:", True, (255, 255, 255))
    SCREEN.blit(label_text, (865, 10)) 

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
