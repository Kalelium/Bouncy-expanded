# pygame -> engine, os -> helps with closing app, shared_resources -> stores info multiple files need at once, classes -> all classes
import pygame
import sys
from shared_resources import SCREEN_WIDTH, SCREEN_HEIGHT, screen, universal_scale as US
from classes import SimpleButton, Text, MultiSpriteImage, RicochetingSprite, RandomRectPlacer, ScaleManager

# pygame setup
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption('DVD Logo')

# colors (R, G, B) | 0 -> 255
white = (255, 255, 255)
gray = (128, 128, 128)
dark_blue_gray = (50, 55, 65)

# variables
s = ScaleManager(US)

bottom_panel = pygame.Rect(0, #left 
                            (SCREEN_HEIGHT * 5/6), #top
                            SCREEN_WIDTH, #width
                            (SCREEN_HEIGHT - SCREEN_HEIGHT * 5/6) #height
                           )

print(bottom_panel)

player_money = 0

# class definitions
dvd_logo = RicochetingSprite(surface = screen, 
                             coordinates = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 
                             speed = 4, 
                             scale = 3, 
                             use_center = False, 
                             image_path = 'assets/dvd_logo46x22.png', 
                             boundary_coordinates = (0, 0), 
                             boundary_width = SCREEN_WIDTH, 
                             boundary_height = SCREEN_HEIGHT*5/6)

currency_spawner = RandomRectPlacer(screen, 50 * US, 50 * US, None, (0, 0), SCREEN_WIDTH, SCREEN_HEIGHT*5/6)

player_money_text = Text(surface = screen, 
                        font = None, 
                        font_size = int(100), 
                        text_color = white,
                        text_content = '0', 
                        coordinates = (25, 925),
                        background_color = None,
                        bold = False, 
                        italic = False,
                        antialias = True, 
                        use_center = False)
print(player_money_text.coordinates)

blue_stars = MultiSpriteImage(screen, (SCREEN_WIDTH//2, SCREEN_HEIGHT//3), 12, True, 1, 6, 'assets/blue_stars.png', None)
blue_stars = MultiSpriteImage(surface = screen, 
                              coordinates = (SCREEN_WIDTH//2, SCREEN_HEIGHT//3), 
                              scale = 12, 
                              use_center = True, 
                              sprite_sheet_rows = None, 
                              sprite_sheet_columns = None, 
                              sprite_sheet_path = None,
                              folder_path = 'test images'
                              )

#upgrade_button = SimpleButton(screen, (SCREEN_WIDTH//2, SCREEN_HEIGHT*0.75), None, 10, 2, 'assets/upgrade_button.png', None, None)


running = True

# main loop 
while running:

    # player input
    mouse_position = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        # quits game when the topleft x button is pressed
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(dark_blue_gray)

    # RENDER YOUR GAME HERE
    #blue_stars.draw()

    pygame.draw.rect(screen, gray, bottom_panel)
    currency_spawner.spawn_rectangles(60, 1)
    dvd_logo.draw()

    collided_keys = []  # List to keep track of keys to remove

    for key, rect_info in list(currency_spawner.rect_dict.items()):
        _, rect = rect_info  # Unpack the color and rectangle
        if dvd_logo.rect.colliderect(rect):
            print("Rectanlge collected!")
            #blue_stars.trigger_image_change()
            player_money += 1
            player_money_text.text_content = f"{player_money}"
            collided_keys.append(key)  # Store the key of the collided rectangle

    # Remove collided rectangles
    for key in collided_keys:
        del currency_spawner.rect_dict[key]

    player_money_text.draw()
        

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
sys.exit()