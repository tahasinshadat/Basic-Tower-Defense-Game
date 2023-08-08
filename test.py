import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the window
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Circle-Rectangle Collisions in Pygame")

# Set up colors (RGB format)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Circle class
class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

# Rectangle class
class Rectangle:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# Check for circle-rectangle collisions
def check_collision(circle, rect):
    circle_rect = pygame.Rect(circle.x - circle.radius, circle.y - circle.radius, circle.radius * 2, circle.radius * 2)
    return circle_rect.colliderect(rect)

# Create a circle and a rectangle
circle = Circle(200, 300, 50, RED)
rectangle = Rectangle(400, 250, 100, 150, GREEN)

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear the screen
    screen.fill(WHITE)

    # Draw the circle and rectangle
    circle.draw()
    rectangle.draw()

    # Check for collisions
    if check_collision(circle, rectangle):
        print("Colliding!")

    # Update the display
    pygame.display.flip()
