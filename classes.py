import pygame
import random
import os 
from shared_resources import screen
pygame.mixer.init()


class ScaleManager():
	'''
	Use:
		A class for scaling single ints and tuples

	Attributes:
		scale: number used for scaling everything esle

	CURRENTLY USELESS!!
	
	'''
	def __init__(self, scale: int):
		self.scale = scale

	def scale_number(self, number: int) -> tuple:
		return int(number * self.scale)

	def scale_tuple(self, values: tuple[int, int]) -> tuple[int, int]:
		return (int(values[0] * self.scale), int(values[1] * self.scale))


'''  
	    HOW TO USE BUTTONS IN MAIN GAME LOOP - MAKE SURE TO SET ACTION TO FALSE AT END

			if play_button.action:
        print("Play button clicked!")
        # Perform the action, e.g., start the game
        play_button.action = False  # Reset action flag after handling
							^^^^^^^
	'''
	

'''
    # Get mouse position and button states
    mouse_position = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

'''
class SimpleButton:
	def __init__(self, surface: pygame.Surface, coordinates: tuple[int, int], darkness_factor: int | None, shift_amount: int, scale: int, image_path: str, held_image_path: str | None, sound_effect_path: str | None):

		# used for calculations
		self.surface = surface
		self.coordinates = coordinates
		self.shift_amount = shift_amount
		self.darkness_factor = 0.50 if darkness_factor is None else darkness_factor # between 0 and 1

		# sound (SOUND AS A NOTICABLE DELAY FOR SOME REASON)
		self.sound = None if sound_effect_path is None else pygame.mixer.Sound(sound_effect_path)

		# surfaces and rects
		self.image = self._scale_image(image_path, scale)
		self.held_image = None if held_image_path is None else self._scale_image(held_image_path, scale)
		self.darked_image = None if self.held_image != None else self._darken_image(self.image, self.darkness_factor)
		self.rect = self.image.get_rect(center=self.coordinates)

		# button functionality
		self.action = False
		self.held = False
		self.shifted = False
	
	def _scale_image(self, image_path: str, scale: float) -> pygame.image:
		"""Loads and scales ricocheting image using scale"""
		return pygame.transform.scale(pygame.image.load(image_path), (pygame.image.load(image_path).get_width() * scale, pygame.image.load(image_path).get_height() * scale))


	def _darken_image(image, darkness_factor):
		# copies original image so it doesn't get changed
		image = image.copy()
		# creates blank surface the same size as the image sent
		dark_surface = pygame.Surface(image.get_size()).convert_alpha()
		# makes the surface black and makes transparent based on 'darkness_facotr'
		dark_surface.fill((0, 0, 0, int(255 *  darkness_factor)))
		# blend the dark surface with the image sent to make the orignal image darker
		image.blit(dark_surface, (0,0), special_flags=pygame.BLEND_RGBA_SUB)
		return image

	
	def update_state(self, mouse_position, mouse_buttons):
		if self.rect.collidepoint(mouse_position):
			if mouse_buttons[0]: # left click is held down down
				if self.shifted == False:
					self.rect.y += self.shift_amount # shift button downwards when held
					self.shifted = True
				self.held = True
				

			elif self.held: # left click is releases
				if self.shifted:
					self.rect.y -= self.shift_amount # moves button back to normal place
					self.shifted = False
				self.held = False
				self.action = True

				# if there's a sound effect it will play
				if self.sound:
					self.sound.play()

		else: # resets held state when mouse leaves button !!!!!!!!!!!!is this needed?!!!!!!!!!!!!!!
			self.held = False
	

	def draw(self):
		if self.held: # if the button is held
			if self.held_image == None: # if there's no picture the first image will be darkened
				self.surface.blit(self.darked_image, self.rect.topleft)

			else: # if there's a held down image it will be displayed
				self.surface.blit(self.held_image, self.rect.topleft)

		else: # if the button isn't held, display default image
			self.surface.blit(self.image, self.rect.topleft)


	def update_state_and_draw(self, mouse_position, mouse_buttons):
		self.update_state(mouse_position, mouse_buttons)
		self.draw()


class MultiSpriteImage:
	'''
	Use:
		A class for managing and displaying multiple sprite images one after another,
		allowing for seamless transitions between images from either an EVEN sprite sheet 
		or a folder of images. 
	
	Attributes:
		surface (pygame.Surface): The surface to draw on
		coordinates (tuple[int,int]): Where to draw the images (topleft)
		scale (float): Multiplied to sprite length and width to resize it
		use_center (bool): Coordinates will now be for the center instead of the topleft
		sprite_sheet_rows (int | None): Used for calculations with SPRITE SHEETS
		sprite_sheet_columns (int | None): Used for calculations with SPRITE SHEETS
		sprite_sheet_path (str | None): Relative path to sprite sheet if one is being used
		folder_path (str | None): Relative path to folder with images if one is being used
		sprites (list[pygame.Surface]): List of sprites
		image_to_display (int): The index of the image to display
		change_image (bool): Checks to see if the current image should be changed

		image_amount (int): The amount of images, used for calculations
		counter (int): Used for sprite sheet calculations
		row_completions (int): Used for sprite sheet calculations

	Dependencies:
		Requires the 'pygame' and 'os' modules.

	'''

	def __init__(self, 
			  surface: pygame.Surface, 
			  coordinates: tuple[int, int], 
			  scale: float, 
			  use_center: bool, 
			  sprite_sheet_rows: int | None, 
			  sprite_sheet_columns: int | None, 
			  sprite_sheet_path: str | None, 
			  folder_path: str | None) -> None:

		# coordinates and scale
		self.surface: pygame.Surface = surface
		self.coordinates: tuple[int, int] = coordinates
		self.scale: float = scale
		self.use_center: bool = use_center

		# to display specific images and flip through them
		self.image_amount: int = 0
		self.image_to_display: int = 0 
		self.change_image: bool  = False

		# sprite list
		self.sprites: list[pygame.Surface] = []

		# folder or sprite sheet
		self.sprite_sheet: None | pygame.Surface = None if sprite_sheet_path is None else self._load_and_scale_sprite_sheet(sprite_sheet_path) 
		self.folder_path: None | str = None if folder_path is None else folder_path

		# folder image extraction
		if folder_path:
			self._load_sprites_from_folder()

		# sprite sheet image extraction
		if self.sprite_sheet:
			self.counter: int = 0
			self.row_completions: int = 0
			self.sprite_sheet_rows: int = sprite_sheet_rows
			self.sprite_sheet_columns: int = sprite_sheet_columns
			self._load_sprites_from_sprite_sheet()

	# private func, don't worry about it 
	def _load_and_scale_sprite_sheet(self, path: str | None) -> pygame.Surface | None:
		"""Loads and scales sprite sheet using self.scale"""
		return pygame.transform.scale(pygame.image.load(path), (pygame.image.load(path).get_width() * self.scale, pygame.image.load(path).get_height() * self.scale))



	# Private method for splitting a sprite sheet into individual sprites.
	def _load_sprites_from_sprite_sheet(self) -> None:
		"""Cuts images from sprite sheet into self.sprites as a list"""
		self.image_amount = self.sprite_sheet_rows * self.sprite_sheet_columns

		while self.counter < self.image_amount:
			subsurface_rect = pygame.Rect(self.counter%self.sprite_sheet_columns*self.sprite_sheet.get_width()/self.sprite_sheet_columns, 
							self.row_completions*self.sprite_sheet.get_height(), 
							self.sprite_sheet.get_width()/self.sprite_sheet_columns, 
							self.sprite_sheet.get_height()/self.sprite_sheet_rows)
			
			self.sprites.append(self.sprite_sheet.subsurface(subsurface_rect))

			if self.counter%self.sprite_sheet_columns == self.sprite_sheet_columns - 1:
				self.row_completions += 1
			self.counter += 1

	# Private method for loading individual sprites from a folder
	def _load_sprites_from_folder(self) -> None:
		"""Loads folder images into self.sprites as list"""
		allowed_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tga", ".ppm", ".pgm", ".xpm")

		# Get all filenames in the folder
		files_in_folder = [file_name for file_name in os.listdir(self.folder_path) if file_name.endswith(allowed_extensions)]

		# Sort the files alphabetically (same order on all opperating systems :) )
		files_in_folder.sort()

		for file_name in files_in_folder:
			file_path = os.path.join(self.folder_path, file_name)
			self.image_amount += 1
			self.sprites.append(self._load_and_scale_sprite_sheet(file_path))

	def trigger_image_change(self) -> None:
		"""Triggers the next image in the self.sprites list 
		to be drawn during the next draw() function call"""
		self.change_image = True

	def draw_specific_image(self, image_index: int) -> None:
		"""Draw a specific image using the image's index"""
		self.image_to_display = image_index

	def draw(self) -> None:
		"""Draw the MultiSpriteImage"""
		if self.change_image:
			self.image_to_display += 1
			self.change_image = False
		
		# if it works, it works. Don't you dare look at this long line of math 
		if self.use_center:
			self.surface.blit(self.sprites[self.image_to_display % self.image_amount], (self.coordinates[0] - self.sprites[self.image_to_display % self.image_amount].get_width()//2, self.coordinates[1] - self.sprites[self.image_to_display % self.image_amount].get_height()//2))
		else:
			self.surface.blit(self.sprites[self.image_to_display % self.image_amount], self.coordinates)


class RicochetingSprite:
	'''
	Use:
		A class for making a square picture bounce inside of a rectangle boundry
		in a DVD logo type of way

	Attributes: 
		surface (pygame.Surface): The surface to draw on 
		coordinates (tuple[int, int]): Where the bouncing image is placed (top left point)
		speed (float): The amount of pixels the bouncing image will move per frame 
		scale (float): Gets multiplied to the bouncing image's length & width to resize it
		use_center (bool): Use center for coordinate changes instead of top left point
		image_path (str): Image directory
		boundary_coordinates (tuple[int, int]): The top left coordinate of the boundary
		boundary_width (float): How long the boundary is
		boundary_height (float): How tall the boundary is 

		horizontal_collision (bool): True if bouncing image horizontally collides (1 frame)
		vertical_collision (bool): True if bouncing image vertically collides (1 frame)

	
	'''
	def __init__(self, 
			  surface: pygame.Surface, 
			  coordinates: tuple[int, int], 
			  speed: float, 
			  scale: float, 
			  use_center: bool, 
			  image_path: str, 
			  boundary_coordinates: tuple[int, int], 
			  boundary_width: float, 
			  boundary_height: float):

		self.surface: pygame.Surface = surface
		self.coordinates: tuple[int, int] = coordinates
		self.speed: float = speed
		self.scale: float = scale
		self.use_center: bool = use_center
		self.image_path = image_path
		self.horitzontal_collision: bool = False
		self.vertical_collision: bool  = False

		print(f'Ricocheting sprite troubleshooting path:{self.image_path}, scale:{self.scale}')
		# load, scale, and get rect of image
		self.image: pygame.Surface = self._scale_image(self.image_path, self.scale)

		self.rect: pygame.rect = self.image.get_rect()
		self.rect.center = coordinates #tuple[int, int]

		# sets initial direction
		self.x_direction: str = 'right'
		self.y_direction: str = 'up'

		# checks for perfect corner hit
		self.corner_hit = False

		# creates boundary rect
		self.boundary = pygame.Rect((boundary_coordinates),(boundary_width, boundary_height))

	def _scale_image(self, image_path: str, scale: float) -> pygame.image:
		"""Loads and scales ricocheting image using scale"""
		return pygame.transform.scale(pygame.image.load(image_path), (pygame.image.load(image_path).get_width() * scale, pygame.image.load(image_path).get_height() * scale))


	def _check_boundaries(self):

		# if both are true a corner hit happened :)
		if self.corner_hit == True:
			self.corner_hit = False

		# reset
		self.horitzontal_collision = False
		self.vertical_collision = False
		

		# checks if the next movement will take the sprite out of bounds
		if self.rect.right + self.speed > self.boundary.right:
			self.x_direction = 'left'
			self.horitzontal_collision = True
		elif self.rect.left - self.speed < self.boundary.left:
			self.x_direction = 'right'
			self.horitzontal_collision = True

		if self.rect.top + self.speed < self.boundary.top:
			self.y_direction = 'down'
			self.vertical_collision = True
		elif self.rect.bottom - self.speed > self.boundary.bottom:
			self.y_direction = 'up'
			self.vertical_collision = True

		# Checks for corner hits (when both horizontal and vertical boundaries are hit)
		if self.horitzontal_collision and self.vertical_collision:
			self.corner_hit = True
			print("Corner hit detected!")  # You can replace this with your desired action.

	def _move(self):
		# moves sprite based on current direction [left, right, up, down]
		if self.x_direction == 'right':
			self.rect.x += self.speed

		elif self.x_direction == 'left':
			self.rect.x -= self.speed

		if self.y_direction == 'up':
			self.rect.y -= self.speed

		elif self.y_direction == 'down':
			self.rect.y += self.speed

	def draw(self):
		# moves sprite based on current direction [left, right, up, down]
		self._check_boundaries()
		self._move()

		# draws the image after the calculations are done :3
		self.surface.blit(self.image, self.rect)




class RandomRectPlacer:
	'''
	random module is required for this to work
	'''
	def __init__(self, surface, rect_width: int | float, rect_height: int | float, color: tuple[int, int, int] | None, boundary_coordinates: tuple[int, int], boundary_width: int, boundary_height: int) -> None:
		
		self.surface = surface
		self.rect_width = rect_width
		self.rect_height = rect_height
		self.color = color 
		self.boundary_coordinates = boundary_coordinates
		self.boundary_width = boundary_width
		self.boundary_height = boundary_height
		self.rect_dict = {}
		self.frame = 0
		self.rect_number = 0


	def spawn_rectangles(self, fps, delay: int):
		frames_to_wait = fps * delay

		if self.frame == frames_to_wait:
			self.rect_number += 1

			# Generate a random color once when creating the rectangle
			color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
			print(self.boundary_height)
			print(self.rect_height)
			new_rect = pygame.Rect(random.randint(0, int(self.boundary_width - self.rect_width)), random.randint(0, int(self.boundary_height - self.rect_height)), self.rect_width, self.rect_height)

			self.rect_dict[f"rect: {self.rect_number}"] = [color, new_rect] # key: rect, value: color

		for rectangle_info in self.rect_dict.values():
			color, rect = rectangle_info

			if self.color is not None:
				pygame.draw.rect(self.surface, self.color, rect)
			else:
				pygame.draw.rect(self.surface, color, rect)

		if self.frame == frames_to_wait:
			self.frame = 0
		
		self.frame += 1



class Text: 
	def __init__(self, surface, font, font_size, text_color, text_content="", coordinates=(0, 0), background_color=None, bold=False, italic=False, antialias=True, use_center=False):
		self.surface = surface
		self.font = pygame.font.Font(font, font_size)
		self.font.set_bold(bold)
		self.font.set_italic(italic)
		self.text_color = text_color
		self.text_content = text_content
		self.coordinates = coordinates
		self.background_color = background_color
		self.antialias = antialias
		self.use_center = use_center

		# gets the rect so text can be position with self.rect.blah
		self.text_surface = self.font.render(self.text_content, self.antialias, self.text_color, self.background_color)
		self.rect = self.text_surface.get_rect()
		if self.use_center:
			self.rect.center = self.coordinates
		else:
			self.rect.topleft = self.coordinates

	
	def draw(self):
		if self.use_center:
			# Render the text to get the surface
			text_surface = self.font.render(self.text_content, self.antialias, self.text_color, self.background_color)
			# Get the rectangle of the text surface
			text_rect = text_surface.get_rect()
			# Set the center of the rectangle to the desired position
			text_rect.center = self.coordinates
			# Blit the text surface to the screen using the rect's topleft as the position
			self.surface.blit(text_surface, text_rect.topleft)
		else:
			text_surface = self.font.render(self.text_content, self.antialias, self.text_color, self.background_color)
			self.surface.blit(text_surface, self.rect.topleft)



# Functions DO NOT USE THESE, MAKE FUNCTIONS IN CLASS INSTEAD 
def darken_image(image, darkness_factor):
	# copies original image so it doesn't get changed
	image = image.copy()
	# creates blank surface the same size as the image sent
	dark_surface = pygame.Surface(image.get_size()).convert_alpha()
	# makes the surface black and makes transparent based on 'darkness_facotr'
	dark_surface.fill((0, 0, 0, int(255 *  darkness_factor)))
	# blend the dark surface with the image sent to make the orignal image darker
	image.blit(dark_surface, (0,0), special_flags=pygame.BLEND_RGBA_SUB)
	return image

def scale_image(image_path, scale):
	return pygame.transform.scale(pygame.image.load(image_path), (pygame.image.load(image_path).get_width() * scale, pygame.image.load(image_path).get_height() * scale))


'''
function for scaling 

def _load_and_scale_sprite_sheet(self, path: str | None) -> pygame.Surface | None:
	"""Loads and scales sprite sheet using self.scale"""
	return pygame.transform.scale(pygame.image.load(path), (pygame.image.load(path).get_width() * self.scale, pygame.image.load(path).get_height() * self.scale))



'''