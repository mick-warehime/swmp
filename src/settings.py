# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
RED = (255, 0, 0)
DARKBLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

HUDBLUE1 = (64, 127, 177)
HUDBLUE2 = (0, 50, 100)
HUDGREEN1 = (85, 170, 85)
HUDGREEN2 = (10, 68, 10)
HUDGREY = (60, 60, 60)
HUDDARK = (40, 40, 40)

# game settings
WIDTH = 800  # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 600  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = BROWN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Effects
FLASH_DURATION = 50
NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (500, 500)

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1
