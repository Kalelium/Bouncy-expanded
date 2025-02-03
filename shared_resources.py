import pygame
pygame.init()

screen_info = pygame.display.Info()
universal_scale = 1
scale = 0.75

tolerance = 0.1
user_aspect_ratio = screen_info.current_w / screen_info.current_h
desired_aspect_ratio = 16/9
desired_height_multiplier = 9/16

if abs(user_aspect_ratio - desired_aspect_ratio) < tolerance:
    # user already has 16:9 screen
    print('Screen IS 16:9')
    SCREEN_WIDTH = screen_info.current_w * scale
    SCREEN_HEIGHT = screen_info.current_h * scale
    universal_scale = 1

else:
    # user doesn't have 16:9 screen ratio
    print('Screen is NOT 16:9')
    corrected_screen_height = screen_info.current_w * desired_height_multiplier
    SCREEN_WIDTH = screen_info.current_w * scale
    SCREEN_HEIGHT = corrected_screen_height * scale
    universal_scale = screen_info.current_w / 1920

print(f'''
Window Screen width = {SCREEN_WIDTH}
Window Screen height = {SCREEN_HEIGHT}

      
      ''')

'''
16:9 resolutions
small)  1280x720
medium) 1920x1080
large)  2560x1440

16:10 reolutions
small)  1280x800
medium) 1920x1200
large)  2569x1600
'''

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

