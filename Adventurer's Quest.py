import sys
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

W_Width, W_Height = 500, 500

# Character's position and speed
char_x = -200  # Initial X position
char_y = -210  # Feet positioned at y = -210 (ground level)
char_velocity_x = 0  # Horizontal speed (velocity)
char_velocity_y = 0  # Vertical speed (velocity)
acceleration = 1  # Acceleration when moving left or right
max_speed = 7  # Maximum horizontal speed
gravity = -1  # Gravity affecting the vertical velocity
jump_strength = 15  # Jump strength (initial upward velocity)
on_ground = True  # Check if the character is on the ground
stage = 1
boss_health = 5000
player_health = 1000  # Player's initial health
player_score = 0  # Player's initial score
projectiles = []  # List to store projectiles
spawn_interval = 1 * 1000
snakes = []
game_paused = False  

cn = 32
cn1 = 42




def update_window_size():
    global W_Height, W_Width
    W_Width, W_Height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)

def reshape(w, h):
    global W_Width, W_Height
    W_Width, W_Height = w, h  
    update_window_size()  
    glViewport(0, 0, W_Width, W_Height)  

def convert_coordinate(x, y):
    global W_Width, W_Height
    W_Height = glutGet(GLUT_WINDOW_HEIGHT)
    W_Width = glutGet(GLUT_WINDOW_WIDTH)
    a = x - (W_Width / 2)
    b = (W_Height / 2) - y
    return a, b




def draw_line(x1, y1, x2, y2):
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    glBegin(GL_POINTS)
    for i in points:
        glVertex2i(*i)
    glEnd()



def draw_hollow_triangle():
    top_center = (-10, 230)  
    left = (-10, 210)  
    right = (10, 220)  
    glColor3f(1, 1, 0)  
    def plot_line(x1, y1, x2, y2):
        steps = 30  
        for i in range(steps + 1):
            t = i / float(steps)  
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            glBegin(GL_POINTS)
            glVertex2f(x, y)
            glEnd()

    plot_line(top_center[0], top_center[1], left[0], left[1])  
    plot_line(left[0], left[1], right[0], right[1])  
    plot_line(right[0], right[1], top_center[0], top_center[1]) 



# Attack variables
attacks = []
sparks = []
direction_vectors = [
    (1, 0), (-1, 0), (0, 1), (0, -1),  # Cardinal directions
    (1, 1), (-1, 1), (1, -1), (-1, -1)  # Diagonal directions
]
attack_active = False  # Tracks if an attack is active
facing_left = False  # Tracks character direction
hand_offset = 0


# Coin coordinates
coins = [
    (-210, -165),
    (-120, -125),
    (-40, -85),
    (-110, -45),
    (-135, -45),
    (-220, -5),
    (-120, 35),
    (-105, 35),
    (-90, 35),
    (-75, 35),
    (-60, 35),
    (-45, 35),
    (50, 75),
    (75, 75),
    (-140, 115),
    (-120, 115),
    (-95, 115),
    (-80, 115),
    (-50, 115),
    (-35, 115),
    (50, 155),
    (65, 155),
    (80, 155),
    (95, 155),
    (110, 155),
    (135, 155),
    (-220, 155),
    (-200, 155),
    (-60, 195),
    (-45, 195),
    (-30, 195),
    (-15, 195),
]


coins1 = [
    (-210, 155),
    (-195, 155),
    (-225, 155),
    (220, 155),
    (205, 155),
    (235, 155),
    (-130, 115),
    (-115, 115),
    (-145, 115),
    (140, 115),
    (125, 115),
    (155, 115),
    (-50, 75),
    (-35, 75),
    (-65, 75),
    (60, 75),
    (45, 75),
    (75, 75),
    (-210, -5),
    (-195, -5),
    (-225, -5),
    (220, -5),
    (205, -5),
    (235, -5),
    (-130, -45),
    (-115, -45),
    (-145, -45),
    (140, -45),
    (125, -45),
    (155, -45),
    (-130, -125),
    (-115, -125),
    (-145, -125),
    (140, -125),
    (125, -125),
    (155, -125),
    (-210, -165),
    (-195, -165),
    (-225, -165),
    (220, -165),
    (205, -165),
    (235, -165),
]

if stage == 2:
    coins = coins1
 
# Spark-related functions
def launch_sparks(x, y, count=10):
    global direction_vectors
    for _ in range(count):
        dx, dy = random.choice(direction_vectors)  # Randomly select a direction vector
        speed = random.uniform(1, 3)  # Random speed for each spark
        sparks.append({
            "x": x,
            "y": y,
            "dx": dx * speed,
            "dy": dy * speed,
            "life": 10  # Frames before disappearing
        })

def update_sparks():
    global sparks
    for spark in sparks:
        if spark["life"] > 0:
            spark["x"] += spark["dx"]
            spark["y"] += spark["dy"]
            spark["life"] -= 1
    sparks = [spark for spark in sparks if spark["life"] > 0]

def draw_sparks():
    glPointSize(2)  # Small point size for sparks
    glBegin(GL_POINTS)
    for spark in sparks:
        life_fraction = spark["life"] / 10.0  # Assuming max life is 10
        r = 1.0  # Start with full red
        g = life_fraction  # Green decreases with life
        b = 0.0  # No blue for yellow-to-red transition

        glColor3f(r, g, b)  # Set spark color based on remaining life
        glVertex2i(int(spark["x"]), int(spark["y"]))  # Draw the spark
    glEnd()
    glPointSize(1)  # Reset point size

# Function to draw a circle for attacks
def draw_circle(x_center, y_center, radius, color):
    x = radius
    y = 0
    p = 1 - radius

    glColor3f(*color)
    glBegin(GL_POINTS)

    while x >= y:
        for xc, yc in [
            (x_center + x, y_center + y),
            (x_center - x, y_center + y),
            (x_center + x, y_center - y),
            (x_center - x, y_center - y),
            (x_center + y, y_center + x),
            (x_center - y, y_center + x),
            (x_center + y, y_center - x),
            (x_center - y, y_center - x)
        ]:
            glVertex2f(xc, yc)

        y += 1
        if p <= 0:
            p = p + 2 * y + 1
        else:
            x -= 1
            p = p + 2 * (y - x) + 1

    glEnd()

# Function to draw a 10x10 block
def drawBlock(x, y):
    for i in range(x, x + 10):
        for j in range(y, y + 10):
            glBegin(GL_POINTS)
            glVertex2i(i, j)
            glEnd()

def draw_character(x, y):
    glColor3f(1, 0.88, 0.74)  # Skin color for head (light peach)
    for i in range(8):
        for j in range(8):
            glBegin(GL_POINTS)
            glVertex2i(x + j, y + i)
            glEnd()

    glColor3f(0.5, 0, 1)  # Purple color for body
    for i in range(10):
        for j in range(6):
            glBegin(GL_POINTS)
            glVertex2i(x + 1 + j, y - 1 - i)
            glEnd()


def draw_coins():
    """Draw all coins."""
    for coin_x, coin_y in coins:
        draw_circle(coin_x, coin_y, 5, (1.0, 1.0, 0.0))  # Yellow color for coins


hp = [ (-20, 120) ]
hp1 = [ (0, 0) ]
def draw_health():
    global hp, hp1
    if stage == 1:
        for heal in hp:
            draw_circle(heal[0], heal[1], 10, (1.0, 0.08, 0.58))
    elif stage == 2:
        for heal in hp1:
            draw_circle(heal[0], heal[1], 10, (1.0, 0.08, 0.58))

def check_collision1(player_x, player_y, object_x, object_y, object_radius=5):
    """Check if the player collides with an object using bounding box and radius for coins."""
    # Player bounding box (calculated based on draw_character)
    player_xmin = player_x
    player_xmax = player_x + 8  # Width is 8
    player_ymin = player_y - 10  # Body extends 10 units below the head
    player_ymax = player_y + 8  # Head height is 8

    # Object bounding box for coin
    object_xmin = object_x - object_radius
    object_xmax = object_x + object_radius
    object_ymin = object_y - object_radius
    object_ymax = object_y + object_radius

    # Check for overlap
    if (
        player_xmax > object_xmin and
        player_xmin < object_xmax and
        player_ymax > object_ymin and
        player_ymin < object_ymax
    ):
        return True
    return False

import math

def check_collision_circle(circle1_x, circle1_y, circle1_radius, circle2_x, circle2_y, circle2_radius):
    # Calculate the distance between the centers of the circles
    distance = math.sqrt((circle1_x - circle2_x) ** 2 + (circle1_y - circle2_y) ** 2)
    
    # Check if the distance is less than or equal to the sum of the radii
    if distance <= (circle1_radius + circle2_radius):
        return True
    return False



def stage1():
    glColor3f(0.404, 0.255, 0.027)  # Ground color
    for i in range(-250, 251, 10):
        drawBlock(i, -250)
        drawBlock(i, -240)
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-250, 251, 10):
        drawBlock(i, -230)


    #1
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-230, -191, 10):
        drawBlock(i, -190)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-230, -191, 10):
        drawBlock(i, -180)
    #2
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -111, 10):
        drawBlock(i, -150)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-150, -111, 10):
        drawBlock(i, -140)
    #3
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-70, -31, 10):
        drawBlock(i, -110)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-70, -31, 10):
        drawBlock(i, -100)
    #4
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -111, 10):
        drawBlock(i, -70)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-150, -111, 10):
        drawBlock(i, -60)  
    #5
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-230, -191, 10):
        drawBlock(i, -30)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-230, -191, 10):
        drawBlock(i, -20) 
     
    #6
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -11, 10):
        drawBlock(i, 10)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-150, -11, 10):
        drawBlock(i, 20)

    #7
    glColor3f(0.404, 0.255, 0.027)
    for i in range(30, 71, 10):
        drawBlock(i, 50)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(30, 71, 10):
        drawBlock(i, 60)

    #8
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -11, 10):
        drawBlock(i, 90)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-150, -11, 10):
        drawBlock(i, 100)

    #9
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-230, -191, 10):
        drawBlock(i, 130)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-230, -191, 10):
        drawBlock(i, 140)
   
    #10
    glColor3f(0.404, 0.255, 0.027)
    for i in range(30, 141, 10):
        drawBlock(i, 130)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(30, 141, 10):
        drawBlock(i, 140)
  
    #11
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-70, -11, 10):
        drawBlock(i, 170)
        
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-70, -11, 10):
        drawBlock(i, 180)

    draw_health()


def stage2():
    global frame_counter, frame_counter1, snakes, game_paused
    glColor3f(0.404, 0.255, 0.027)  # Ground color
    for i in range(-250, 251, 10):
        drawBlock(i, -250)
        drawBlock(i, -240)
    glColor3f(0.255, 0.596, 0.039)
    for i in range(-250, 251, 10):
        drawBlock(i, -230)

    #1
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-230, -191, 10):
        drawBlock(i, -180)
        drawBlock(i, -190)
    #2
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -111, 10):
        drawBlock(i, -150)
        drawBlock(i, -140)
    
    #3
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-70, -31, 10):
        drawBlock(i, -110)
        drawBlock(i, -100)
    
    #4
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -111, 10):
        drawBlock(i, -70)
        drawBlock(i, -60)
      
    #5
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-230, -191, 10):
        drawBlock(i, -30)
        drawBlock(i, -20) 
     
    #6
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-230, -191, 10):
        drawBlock(-i, -180)
        drawBlock(-i, -190)
    #7
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -111, 10):
        drawBlock(-i, -150)
        drawBlock(-i, -140)
    
    #8
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-70, -31, 10):
        drawBlock(-i, -110)
        drawBlock(-i, -100)
    
    #9
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -111, 10):
        drawBlock(-i, -70)
        drawBlock(-i, -60)
      
    #10
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-230, -191, 10):
        drawBlock(-i, -30)
        drawBlock(-i, -20)

    
    #11
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -111, 10):
        drawBlock(i, 10)
        drawBlock(i, 20)
    
    #12
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-70, -31, 10):
        drawBlock(i, 50)
        drawBlock(i, 60)
    
    #13
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -111, 10):
        drawBlock(i, 90)
        drawBlock(i, 100)

    #14
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -111, 10):
        drawBlock(-i, 10)
        drawBlock(-i, 20)
    
    #15
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-70, -31, 10):
        drawBlock(-i, 50)
        drawBlock(-i, 60)
    
    #16
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-150, -111, 10):
        drawBlock(-i, 90)
        drawBlock(-i, 100)

    #17
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-230, -191, 10):
        drawBlock(i, 130)
        drawBlock(i, 140)

    #18
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-70, -31, 10):
        drawBlock(i, 130)
        drawBlock(i, 140)

    #19
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-230, -191, 10):
        drawBlock(-i, 130)
        drawBlock(-i, 140)
    

    #20
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-70, -31, 10):
        drawBlock(-i, 130)
        drawBlock(-i, 140)
    
    for snake in snakes[:]:
        snake["s"]()
        snake["p"]()
    
        # Call the lambda, which will call draw_snake with the stored arguments
        
    
  

     
    draw_health()
    
    update_poison()
    frame_counter += 1
    update_poison1()
    frame_counter1 += 1
    draw_poison()
    
    check_collision_with_poison(char_x, char_y)
    check_collision_with_poison1(char_x, char_y)




def spawn_projectile():
    global game_paused
    if game_paused == True:
        return
    proj_x = 120  # Left boundary of the boss
    proj_y = random.randint(-50, 50)
    projectiles.append([proj_x, proj_y])

def move_projectiles():
    global game_paused
    if game_paused == True:
        return
    for proj in projectiles[:]:
        proj[0] -= 3
        if proj[0] < -250:
            projectiles.remove(proj)

def draw_projectiles():
    
    # Red color for projectiles
    for proj in projectiles:
        draw_circle(proj[0], proj[1], 5, (1.0, 0.0, 0.0))
    




def stage4():
    # Main body
    draw_circle(150, 0, 50, (1.0, 1.0, 0.0))

    # Small circles around the boss
    draw_circle(150, 50, 10, (1.0, 0.0, 0.0))
    draw_circle(150, -50, 10, (1.0, 0.0, 0.0))
    draw_circle(210, 0, 10, (1.0, 0.0, 0.0))

    # Projectile launcher
    draw_line(150, 0, 120, 0)

    # Decorative circles
    draw_circle(120, 30, 5, (1.0, 0.0, 0.0))
    draw_circle(120, -30, 5, (1.0, 0.0, 0.0))
    
    glColor3f(0.404, 0.255, 0.027)
    for i in range(-230, -31, 10):
        drawBlock(i, -95)
    for i in range(-180, -81, 10):
        drawBlock(i, 5)
    for i in range(-230, -191, 10):
        drawBlock(i, -45)
    for i in range(-70, -31, 10):
        drawBlock(i, -45)


def stage5():
    global char_x, char_y, boss_health, player_health
    glClearColor(0.0, 0.0, 0.0, 1)
    char_x = 0
    char_y = 0
    if boss_health <= 0:
        print("Congratulations! You finished the game!")
    if player_health <= 0:
        print("Game Over! Better luck next time!")
    


def draw_thorn(x, y):
    """Draw a thorn smaller than the player at the given coordinates."""
    glColor3f(1, 0, 0)  # Thorn color (red)
    for i in range(12):
        for j in range(4):
            glBegin(GL_POINTS)
            glVertex2i(x + j, y + i)
            glEnd()


def draw_diamond(x, y, size, color):
    """Draw a diamond shape centered at (x, y) with the given size and color."""
    r, g, b = color  # Extract color components
    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    for dx in range(-size, size + 1):
        dy = size - abs(dx)
        glVertex2i(x + dx, y + dy)
        glVertex2i(x + dx, y - dy)
    glEnd()

fish_list = [
    {"x": -150, "y": -100, "jump_height": 40, "jump_speed": 1, "vertical_velocity": 1, "is_jumping": True, "health": 100},
    {"x": -50, "y": -100, "jump_height": 30, "jump_speed": 2, "vertical_velocity": 2, "is_jumping": True, "health": 80},
    {"x": 50, "y": -100, "jump_height": 50, "jump_speed": 3, "vertical_velocity": 3, "is_jumping": True, "health": 120},
    {"x": 150, "y": -100, "jump_height": 40, "jump_speed": 1, "vertical_velocity": 1, "is_jumping": True, "health": 100},
    {"x": 220, "y": -100, "jump_height": 30, "jump_speed": 2, "vertical_velocity": 2, "is_jumping": True, "health": 80},
]

def draw_fish(fish):
    """Draw a diamond-shaped fish-like creature at the fish's coordinates."""
    if fish["health"] > 0:
        x, y = fish["x"], fish["y"]

        # Body (diamond shape)
        draw_diamond(x, y, 10, (0.0, 0.5, 1.0))  # Main body (blue)
        draw_diamond(x, y + 12, 8, (0.0, 0.5, 1.0))  # Extending the body

        # Eye
        draw_diamond(x + 1, y + 13, 2, (1.0, 1.0, 1.0))  # White of the eye
        draw_diamond(x + 1, y + 13, 1, (0.0, 0.0, 0.0))  # Pupil

        # Fins
        glColor3f(0.0, 0.7, 0.7)  # Light blue for fins
        glBegin(GL_POINTS)
        for i in range(-8, 0):  # Top fin
            glVertex2i(x - 8 + i // 2, y + 12 + i)
        for i in range(-8, 0):  # Bottom fin
            glVertex2i(x + 8 - i // 2, y + 12 + i)
        glEnd()

        # Tail
        glColor3f(0.0, 0.4, 0.8)  # Darker blue for tail
        glBegin(GL_POINTS)
        for i in range(-6, 6):
            glVertex2i(x + i, y - 10)  # Vertical tail
            glVertex2i(x + i, y - 10 + abs(i // 2))  # Horizontal taper
        glEnd()

def update_fish_health(fish_list, attacks):
    """Update the health of all fish based on collisions with attacks."""
    fish_hit_radius = 10  # Radius within which the fish can be hit

    for fish in fish_list:
        if fish["health"] > 0:  # Only process fish that are alive
            for attack in attacks:
                # Check for collision
                if (abs(attack["x"] - fish["x"]) <= fish_hit_radius and
                    abs(attack["y"] - fish["y"]) <= fish_hit_radius):
                    fish["health"] -= 10  # Reduce health by 10 on each hit
                    print(f"Sea Monster Health: {fish['health']}")
                    attacks.remove(attack)  # Remove attack after collision
                    if fish["health"] <= 0:
                        print(f"Sea Monster killed")
                        fish["health"] = 0  # Ensure health doesn't go below zero
                    break

def update_fish(fish):
    global game_paused
    if game_paused == True:
        return
    if fish["health"] > 0:  # Only update if the fish is alive
        if fish["is_jumping"]:
            fish["y"] += fish["vertical_velocity"]
            fish["vertical_velocity"] -= 1  # Apply gravity effect

            # Reverse direction if reaching jump height or ground
            if fish["y"] == -230:
                fish["vertical_velocity"] += 20
                
            if fish["vertical_velocity"] < 0 and fish["y"] <= -230:
                fish["vertical_velocity"] = fish["jump_speed"]
                fish["y"] = -230
                            

def check_collision_with_fish(player_x, player_y, fish_list):
    """Check if the player collides with any fish."""
    global player_health

    for fish in fish_list:
        if fish["health"] > 0:  # Only check collisions with alive fish
            fish_width, fish_height = 20, 20
            fish_xmin = fish["x"] - fish_width // 2
            fish_xmax = fish["x"] + fish_width // 2
            fish_ymin = fish["y"] - fish_height // 2
            fish_ymax = fish["y"] + fish_height // 2

            if (
                player_x + 8 > fish_xmin and  # player_xmax
                player_x < fish_xmax and      # player_xmin
                player_y + 8 > fish_ymin and  # player_ymax
                player_y - 10 < fish_ymax     # player_ymin
            ):
                player_health = 0  # Set health to 0 upon collision
                print("Player hit by fish! Health: 0")
                return True
    return False


def update_and_draw_fish(fish_list, player_x, player_y):
    """Update and draw all fish, and check for collisions."""
    
    
    for fish in fish_list:
        update_fish(fish)  # Update each fish's position
        draw_fish(fish)    # Draw each fish
    update_fish_health(fish_list, attacks)  # Check for attack collisions
    check_collision_with_fish(player_x, player_y, fish_list)

def draw_snake(x, y, length):
    """Draw a simple horizontal snake on a platform."""
    """Draw a snake with a head and body segments."""
    # Draw the head as a small circle
    draw_circle(x, y + 10, 5, (1.0, 0.0, 0.0))  # Red head above the body

    # Draw the vertical segment
    glColor3f(1.0, 0.0, 0.0)  # Green color for the body
    glBegin(GL_POINTS)
    for i in range(10):  # Vertical segment length
        glVertex2i(x, y + i)
    glEnd()

    # Draw the horizontal segment (body)
    glBegin(GL_POINTS)
    for i in range(15):  # Horizontal body length
        glVertex2i(x + i, y)
    glEnd()
    return x, y+10


def draw_snake1(x, y, length):
    """Draw a simple horizontal snake reflected about the y-axis."""
    """Draw a snake with a head and body segments."""

    # Draw the head as a small circle (reflected about the y-axis)
    draw_circle(-x, y + 10, 5, (1.0, 0.0, 0.0))  # Red head above the body

    # Draw the vertical segment (reflected about the y-axis)
    glColor3f(1.0, 0.0, 0.0)  # Green color for the body
    glBegin(GL_POINTS)
    for i in range(10):  # Vertical segment length
        glVertex2i(-x, y + i)
    glEnd()

    # Draw the horizontal segment (body, reflected about the y-axis)
    glBegin(GL_POINTS)
    for i in range(15):  # Horizontal body length
        glVertex2i(-x - i, y)
    glEnd()
    return -x, y+10



poisons = []  # List to track poison shots
poison_speed = 2  # Speed of the poison shots
poison_color = (0.5, 0, 1)  # Purple color for poison
poison_launch_interval = 60  # Frames between each poison launch
frame_counter = 0  # Frame counter for controlling poison launches

poisons1 = []  # List to track poison shots
poison_speed1 = 2  # Speed of the poison shots
poison_color1 = (0.5, 0, 1)  # Purple color for poison
poison_launch_interval1 = 60  # Frames between each poison launch
frame_counter1 = 0  # Frame counter for controlling poison launches

def launch_poison(snake_x, snake_y):
    
    """Launch poison from the snake's head."""
    """
    Launch poison shot from a given position (x, y).
    """
    global frame_counter, poison_launch_interval
    if frame_counter % poison_launch_interval == 0:
        poisons.append({
            "x": snake_x,
            "y": snake_y,
            "dy": poison_speed  # Moving downwards
        })

def launch_poison1(snake_x, snake_y):
    
    """Launch poison from the snake's head."""
    """
    Launch poison shot from a given position (x, y).
    """
    global frame_counter1, poison_launch_interval1
    if frame_counter1 % poison_launch_interval1 == 0:
        poisons1.append({
            "x": snake_x,
            "y": snake_y,
            "dy": poison_speed1  # Moving downwards
        })

def check_collision_with_poison(player_x, player_y):

        global player_health
        for poison in poisons:  # Assuming `poison_shots` stores all active poison positions
            if check_collision1(player_x, player_y, poison["x"], poison["y"], 2):  # Adjust radius as needed
                player_health -= 100  # Reduce health when hit
                print(f"Player hit by poison! Health: {player_health}")
                poisons.remove(poison)  # Remove poison after collision

def check_collision_with_poison1(player_x, player_y):

        global player_health
        for poison in poisons1:  # Assuming `poison_shots` stores all active poison positions
            if check_collision1(player_x, player_y, poison["x"], poison["y"], 2):  # Adjust radius as needed
                player_health -= 100  # Reduce health when hit
                print(f"Player hit by poison! Health: {player_health}")
                poisons1.remove(poison)  # Remove poison after collision


def update_poison():
    
    
    global poisons, game_paused
    if game_paused == True:
        return
    for poison in poisons:
        poison["x"] -= poison["dy"]  # Move poison leftwards
    poisons = [poison for poison in poisons if poison["y"] > -250]  # Remove off-screen poison

def update_poison1():
    
    """
    Update the position of all poison shots and remove those that go off-screen.
    """
    global poisons1, game_paused
    if game_paused == True:
        return
    for poison in poisons1:
        poison["x"] += poison["dy"]  # Move poison rightwards
    poisons1 = [poison for poison in poisons1 if poison["y"] < 250]  # Remove off-screen poison

def draw_poison():
    
    """Draw the poison shots."""
    """
    Draw all poison shots.
    """
    for poison in poisons:
        draw_circle(poison["x"], poison["y"], 2, poison_color)  # Draw poison as small purple circles
    for poison in poisons1:
        draw_circle(poison["x"], poison["y"], 2, poison_color)  # Draw poison as small purple circles






def check_collision(player_x, player_y, thorn_x, thorn_y):
    """Check if the player collides with the thorn using AABB (Axis-Aligned Bounding Box)."""
    # Player bounding box (calculated based on draw_character)
    player_xmin = player_x
    player_xmax = player_x + 8  # Width is 8
    player_ymin = player_y - 10  # Body extends 10 units below the head
    player_ymax = player_y + 8  # Head height is 8

    # Thorn bounding box
    thorn_xmin = thorn_x
    thorn_xmax = thorn_x + 4  # Width is 4
    thorn_ymin = thorn_y
    thorn_ymax = thorn_y + 12  # Height is 12

    # Check for overlap
    if (
        player_xmax > thorn_xmin and
        player_xmin < thorn_xmax and
        player_ymax > thorn_ymin and
        player_ymin < thorn_ymax
    ):
        return True
    return False


def update_health():
    """Print the player's health in the console."""
    print(f"Player Health: {player_health}")

def update_score():
    """Print the player's score in the console."""
    print(f"Player Score: {player_score}")

# Example thorn coordinates (add more as needed)
thorns = [
    (-140, -130), # Thorn 1
    (-60, -90),  # Thorn 2
    (-130, -50),
    (-210, -10),
    (-140, 30),
    (-30, 30),
    (30, 70),
    (-110, 110),
    (-70, 110),
    (30, 150)
]


snakes.append({
            "s": lambda: draw_snake(-50, 150, 15),
            "p": lambda: launch_poison(-50, 165)
        })
snakes.append({
            "s": lambda: draw_snake(-130, 30, 15),
            "p": lambda: launch_poison(-130, 45)
        })
snakes.append({
            "s": lambda: draw_snake(-50, -90, 15),
            "p": lambda: launch_poison(-50, -85)
        })
snakes.append({
            "s": lambda: draw_snake1(-60, 150, 15),
            "p": lambda: launch_poison1(60, 165)
        })
snakes.append({
            "s": lambda: draw_snake1(-140, 30, 15),
            "p": lambda: launch_poison1(140, 45)
        })
snakes.append({
            "s": lambda: draw_snake1(-60, -90, 15),
            "p": lambda: launch_poison1(60, -85)
        })



# Update function (kept from the first code)
def update():
    global char_x, char_y, char_velocity_x, char_velocity_y, on_ground, player_health, player_score, coins, stage, hp, hp1, max_speed, boss_health, projectiles, snakes, fish_health, cn, cn1, game_paused
    if game_paused == True:
        return
    # Update character position based on velocity
    char_x += char_velocity_x
    char_y += char_velocity_y
    if not on_ground:
        char_velocity_y += gravity
    if stage == 1:
        if -230 <= char_x <= -190 and -170 <= char_y <= -160 and on_ground == False:
            char_y = -160
            char_velocity_y = 0
            on_ground = True
        elif -150 <= char_x <= -110 and -130 <= char_y <= -120 and on_ground == False:
            char_y = -120
            char_velocity_y = 0
            on_ground = True
        elif -70 <= char_x <= -30 and -90 <= char_y <= -80 and on_ground == False:
            char_y = -80
            char_velocity_y = 0
            on_ground = True
        elif -150 <= char_x <= -110 and -50 <= char_y <= -40 and on_ground == False:
            char_y = -40
            char_velocity_y = 0
            on_ground = True
        elif -230 <= char_x <= -190 and -10 <= char_y <= 0 and on_ground == False:
            char_y = 0
            char_velocity_y = 0
            on_ground = True
        elif -150 <= char_x <= -10 and 30 <= char_y <= 40 and on_ground == False:
            char_y = 40
            char_velocity_y = 0
            on_ground = True
        elif 30 <= char_x <= 70 and 70 <= char_y <= 80 and on_ground == False:
            char_y = 80
            char_velocity_y = 0
            on_ground = True
        elif -150 <= char_x <= -10 and 110 <= char_y <= 120 and on_ground == False:
            char_y = 120
            char_velocity_y = 0
            on_ground = True
        elif -230 <= char_x <= -190 and 150 <= char_y <= 160 and on_ground == False:
            char_y = 160
            char_velocity_y = 0
            on_ground = True
        elif 30 <= char_x <= 140 and 150 <= char_y <= 160 and on_ground == False:
            char_y = 160
            char_velocity_y = 0
            on_ground = True
        elif -70 <= char_x <= -10 and 190 <= char_y <= 200 and on_ground == False:
            char_y = 200
            char_velocity_y = 0
            on_ground = True
        elif char_y > -210:
            char_velocity_y += gravity
            on_ground = False
        else:
            char_y = -210
            char_velocity_y = 0
            on_ground = True

    if stage == 2:
        if -230 <= char_x <= -190 and -170 <= char_y <= -160 and on_ground == False:
            char_y = -160
            char_velocity_y = 0
            on_ground = True
        elif -150 <= char_x <= -110 and -130 <= char_y <= -120 and on_ground == False:
            char_y = -120
            char_velocity_y = 0
            on_ground = True
        elif -70 <= char_x <= -30 and -90 <= char_y <= -80 and on_ground == False:
            char_y = -80
            char_velocity_y = 0
            on_ground = True
        elif -150 <= char_x <= -110 and -50 <= char_y <= -40 and on_ground == False:
            char_y = -40
            char_velocity_y = 0
            on_ground = True
        elif -230 <= char_x <= -190 and -10 <= char_y <= 0 and on_ground == False:
            char_y = 0
            char_velocity_y = 0
            on_ground = True


        elif 230 >= char_x >= 190 and -170 <= char_y <= -160 and on_ground == False:
            char_y = -160
            char_velocity_y = 0
            on_ground = True
        elif 150 >= char_x >= 110 and -130 <= char_y <= -120 and on_ground == False:
            char_y = -120
            char_velocity_y = 0
            on_ground = True
        elif 70 >= char_x >= 30 and -90 <= char_y <= -80 and on_ground == False:
            char_y = -80
            char_velocity_y = 0
            on_ground = True
        elif 150 >= char_x >= 110 and -50 <= char_y <= -40 and on_ground == False:
            char_y = -40
            char_velocity_y = 0
            on_ground = True
        elif 230 >= char_x >= 190 and -10 <= char_y <= 0 and on_ground == False:
            char_y = 0
            char_velocity_y = 0
            on_ground = True


        elif -150 <= char_x <= -110 and 30 <= char_y <= 40 and on_ground == False:
            char_y = 40
            char_velocity_y = 0
            on_ground = True
        elif -70 <= char_x <= -30 and 70 <= char_y <= 80 and on_ground == False:
            char_y = 80
            char_velocity_y = 0
            on_ground = True
        elif -150 <= char_x <= -110 and 110 <= char_y <= 120 and on_ground == False:
            char_y = 120
            char_velocity_y = 0
            on_ground = True
        elif -230 <= char_x <= -190 and 150 <= char_y <= 160 and on_ground == False:
            char_y = 160
            char_velocity_y = 0
            on_ground = True


        elif 150 >= char_x >= 110 and 30 <= char_y <= 40 and on_ground == False:
            char_y = 40
            char_velocity_y = 0
            on_ground = True
        elif 70 >= char_x >= 30 and 70 <= char_y <= 80 and on_ground == False:
            char_y = 80
            char_velocity_y = 0
            on_ground = True
        elif 150 >= char_x >= 110 and 110 <= char_y <= 120 and on_ground == False:
            char_y = 120
            char_velocity_y = 0
            on_ground = True
        elif 230 >= char_x >= 190 and 150 <= char_y <= 160 and on_ground == False:
            char_y = 160
            char_velocity_y = 0
            on_ground = True
        

        elif -70 <= char_x <= -30 and 150 <= char_y <= 160 and on_ground == False:
            char_y = 160
            char_velocity_y = 0
            on_ground = True
        elif 70 >= char_x >= 30 and 150 <= char_y <= 160 and on_ground == False:
            char_y = 160
            char_velocity_y = 0
            on_ground = True

        elif char_y > -210:
            char_velocity_y += gravity
            on_ground = False
        else:
            char_y = -210
            char_velocity_y = 0
            on_ground = True
    

    if stage == 3:
        if char_y > -210:
            char_velocity_y += gravity
            on_ground = False
        else:
            char_y = -210
            char_velocity_y = 0
            on_ground = True


    if stage == 4:     
        max_speed = 5
        if -230 <= char_x <= -190 and -35 <= char_y <= -25 and on_ground == False:
            char_y = -25
            char_velocity_y = 0
            on_ground = True
        elif -70 <= char_x <= -30 and -35 <= char_y <= -25 and on_ground == False:
            char_y = -25
            char_velocity_y = 0
            on_ground = True  
        elif -180 <= char_x <= -80 and 20 <= char_y <= 30 and on_ground == False:
            char_y = 25
            char_velocity_y = 0
            on_ground = True

        elif char_y > -75:
            char_velocity_y += gravity
            on_ground = False
        else:
            char_y = -75
            char_velocity_y = 0
            on_ground = True
        if char_x < -230:
            char_x = -230
        elif char_x+10 > -30:
            char_x = -40



    if stage == 1:
        if char_x < -250:
            char_x = -250
        if char_x+10 > 250:
            if player_score >= 320:
                char_x = -200
                char_y = -210
                char_velocity_x = 0
                char_velocity_y = 0
                on_ground = True
                stage += 1
                coins = coins1
            else:
                char_x = 240

      

    if stage == 1:
        
        # Check collisions with coins
        for coin in coins[:]:
            if check_collision1(char_x, char_y, coin[0], coin[1]):
                player_score += 10
                coins.remove(coin)
                cn -= 1
                print(f"Coins needed for next stage: {cn}")
        for heal in hp[:]:
            if check_collision1(char_x, char_y, heal[0], heal[1]):
                if player_health < 900:
                    player_health += 100
                elif player_health >= 900:
                    player_health = 1000
                hp.remove(heal)
                update_health()

    if stage == 1:
        # Check collisions with thorns
        for thorn_x, thorn_y in thorns:
            if check_collision(char_x, char_y, thorn_x, thorn_y):
                player_health -= 10  # Decrease health on collision
                update_health()
                if boss_health == 0 or player_health == 0:
                    stage = 5  # Display updated health in console

    if stage == 2:
        if char_x < -250:
            char_x = -250
        if char_x+10 > 250:
            if player_score >= 740:
                char_x = -200
                char_y = -210
                char_velocity_x = 0
                char_velocity_y = 0
                on_ground = True
                stage += 1
            else:
                char_x = 240
    
    if stage == 2:
        
        # Check collisions with coins
        for coin in coins[:]:
            if check_collision1(char_x, char_y, coin[0], coin[1]):
                player_score += 10
                coins.remove(coin)
                cn1 -= 1
                print(f"Coins needed for next stage: {cn1}")
        for heal in hp1[:]:
            if check_collision1(char_x, char_y, heal[0], heal[1]):
                if player_health < 900:
                    player_health += 100
                elif player_health >= 900:
                    player_health = 1000
                hp1.remove(heal)
                update_health()
        for snake in snakes[:]:
            x, y = snake["s"]()
            for attack in attacks[:]:
                if check_collision_circle(attack["x"], attack["y"], attack["radius"], x, y, 5):
                    attacks.remove(attack)
                    snakes.remove(snake)
                    print(f"Snake killed")
        
    if stage == 3:
        if char_x < -250:
            char_x = -250
        if char_x+10 > 250:
            if player_score >= 740:
                char_x = -200
                char_y = -210
                char_velocity_x = 0
                char_velocity_y = 0
                on_ground = True
                stage += 1
            else:
                char_x = 240
      
      
    if stage == 4:
        move_projectiles()
        draw_projectiles()
        for attack in attacks[:]:
            if check_collision_circle(attack["x"], attack["y"], attack["radius"], 150, 0, 50):
                 boss_health -= 100
                 attacks.remove(attack)
                 print(f"Boss Health: {boss_health}")
                 
          
        for proj in projectiles[:]:
            if check_collision1(char_x, char_y, proj[0], proj[1], 5):
                 player_health -= 200
                 projectiles.remove(proj)
                 update_health()
    if boss_health <= 0 or player_health <= 0:
        stage = 5

    

    # Update each attack
    for attack in attacks:
        attack["x"] += attack["speed"] * attack["direction"]
    attacks[:] = [attack for attack in attacks if abs(attack["x"]) <= W_Width / 2]

    update_sparks()
    glutPostRedisplay()

def keyboard(key, x, y):
    global char_velocity_x, on_ground, char_velocity_y, attacks, facing_left, stage, game_paused
    if game_paused == True:
        return
    if key == b'a':  # Move left
        char_velocity_x = -max_speed
        facing_left = True
    elif key == b'd':  # Move right
        char_velocity_x = max_speed
        facing_left = False
    elif key == b' ' and on_ground:  # Jump
        char_velocity_y = jump_strength
        on_ground = False
    elif key == b'f':  # Attack
        # Use the character's direction to determine attack direction
        direction = -1 if facing_left else 1
        attacks.append({
            "x": char_x + (10 * direction),
            "y": char_y,
            "radius": 3,
            "direction": direction,
            "speed": 8
        })
        launch_sparks(char_x, char_y, count=10)

def keyboard_up(key, x, y):
    global char_velocity_x
    if key in [b'a', b'd']:
        char_velocity_x = 0


def timer(value):
    """Timer callback for animations."""
    current_time = glutGet(GLUT_ELAPSED_TIME)
    if not hasattr(timer, "last_spawn_time"):
        timer.last_spawn_time = 0
    if current_time - timer.last_spawn_time >= spawn_interval:
        spawn_projectile()
        timer.last_spawn_time = current_time
    glutPostRedisplay()
    glutTimerFunc(100, timer, 0)

def display():
    global stage, coins, fish_list
    glClear(GL_COLOR_BUFFER_BIT)
    draw_character(char_x, char_y)
    if stage == 1:
        draw_hollow_triangle()
        stage1()
        draw_coins()
        # Draw thorns
        for thorn_x, thorn_y in thorns:
            draw_thorn(thorn_x, thorn_y)
    elif stage == 2:
        glClearColor(0.13, 0.55, 0.13, 1)
        draw_hollow_triangle()
        stage2()
        draw_coins()
    elif stage == 3:
        glClearColor(0.529, 0.808, 0.922, 1)
        draw_hollow_triangle()
        for i in range(-250, 251, 10):
            glColor3f(0.06, 0.369, 0.612)  # Ground color
            drawBlock(i, -250)
            drawBlock(i, -240)
        for i in range(-250, 251, 10):
            glColor3f(0.11, 0.639, 0.925)
            drawBlock(i, -230)
        update_and_draw_fish(fish_list, char_x, char_y)
    elif stage == 4:
        glClearColor(0.0, 0.0, 0.0, 1)
        draw_hollow_triangle()
        stage4()
        move_projectiles()
        draw_projectiles()
    elif stage == 5:
        glClearColor(0.0, 0.0, 0.0, 1)
        stage5()
        
    # Draw attacks
    for attack in attacks:
        draw_circle(attack["x"], attack["y"], attack["radius"], (1, 0, 0))

    draw_sparks()
    glutSwapBuffers()


def mouseListener(button, state, x, y):
    global game_paused, W_Height
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        x, y = convert_coordinate(x, y)

        if -(W_Width/50) < x < (W_Width/50) and (W_Height/2.38) < y < (W_Height/2.17):
            game_paused = not game_paused  
            print("Game Paused" if game_paused else "Game Resumed")

        


def init():
    glClearColor(0.529, 0.808, 0.922, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-W_Width / 2, W_Width / 2, -W_Height / 2, W_Height / 2)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(W_Width, W_Height)
    glutCreateWindow(b"Adventurer's Quest")
    update_window_size()
    init()
    glutDisplayFunc(display)
    glutIdleFunc(update)
    glutMouseFunc(mouseListener)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutTimerFunc(100, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
