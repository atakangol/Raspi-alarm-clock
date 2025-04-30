import json
import datetime
from datetime import timedelta
import requests
import io
import time
import pygame
from urllib.request import urlopen

def check_for_new_imgs():
    response = requests.get("https://epic.gsfc.nasa.gov/api/enhanced")
    imjson = response.json()
    urls = []
    for photo in imjson:
        dt = datetime.datetime.strptime(photo["date"], "%Y-%m-%d %H:%M:%S")
        imageurl = f"https://epic.gsfc.nasa.gov/archive/enhanced/{dt.year}/{str(dt.month).zfill(2)}/{str(dt.day).zfill(2)}/jpg/{photo['image']}.jpg"
        urls.append(imageurl)
    return urls

def read_images(urls):
    images = []
    for imageurl in urls:
        try:
            image_file = io.BytesIO(urlopen(imageurl).read())
            image = pygame.image.load(image_file)
            images.append(image)
        except Exception as e:
            print(f"Error loading image: {e}")
    return images

def process_images(images):
    processed_images = []
    for image in images:
        cropped = pygame.Surface((830, 830))
        cropped.blit(image, (0, 0), (125, 125, 830, 830))
        cropped = pygame.transform.scale(cropped, (480, 480))
        processed_images.append(cropped)
    return processed_images

def read_images_from_file():
    images = []
    for i in range(8):  # Varsayılan olarak 8 resim okuyor
        try:
            image_path = f"images/{i}.jpg"
            image = pygame.image.load(image_path)
            images.append(image)
        except Exception as e:
            print(f"Error loading image from file {image_path}: {e}")
    return images


def create_empty_surface(size, color, transparent=False):
    """Create an empty surface with specified background color
    
    Args:
        size: (width, height) tuple
        color: (R, G, B) or (R, G, B, A) tuple
        transparent: Whether to support transparency
        
    Returns:
        pygame.Surface
    """
    if transparent and len(color) == 3:
        color = (*color, 255)  # Add full opacity if not specified
    
    if transparent:
        surface = pygame.Surface(size, pygame.SRCALPHA)
    else:
        surface = pygame.Surface(size)
    
    surface.fill(color)
    return surface

def add_text_to_surface( surface,  text, 
    position=(0, 0),  color=(255, 255, 255),  font_size=30,    font_name=None, anchor="topleft", outline=False,  outline_color=(0, 0, 0),  outline_width=1
    ):
    """
    Adds text to a pygame surface and returns the modified surface.
    
    Parameters:
        surface (pygame.Surface): The surface to modify
        text (str): Text to display
        position (tuple): (x, y) coordinates
        color (tuple): RGB color for text
        font_size (int): Size of font
        font_name (str): Name of font (None uses default)
        anchor (str): Positioning anchor ('topleft', 'topright', 'center', etc.)
        outline (bool): Whether to add outline
        outline_color (tuple): RGB color for outline
        outline_width (int): Outline thickness
        
    Returns:
        pygame.Surface: Modified surface with text
    """
    # Create font object
    try:
        font = pygame.font.SysFont(font_name, font_size)
    except:
        font = pygame.font.Font(font_name, font_size)  # Fallback for custom fonts
    
    # Render the text
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    # Set position based on anchor
    if hasattr(text_rect, anchor):  # Check if anchor is valid
        setattr(text_rect, anchor, position)
    else:
        text_rect.topleft = position  # Default to topleft
    
    # Add outline if requested
    if outline:
        # Create outline by rendering multiple times with offsets
        outline_surface = font.render(text, True, outline_color)
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:  # Skip the center position
                    outline_rect = text_rect.copy()
                    outline_rect.x += dx
                    outline_rect.y += dy
                    surface.blit(outline_surface, outline_rect)
    
    # Blit the main text
    surface.blit(text_surface, text_rect)
    
    return surface


def get_display_image(state, index, images, alarm_time=None):
    """
    Returns the image to display based on the current state and image index.
    """
    if state == 1:  # Idle - just rotate images
        surface = add_text_to_surface(
            images[index].copy(),
           datetime.datetime.now().strftime("%H:%M"),
            position=(300, 75),
            font_size=50,
            color=(255, 0, 0),
            outline=True,
            outline_color=(0, 0, 0),
            outline_width=2
        )
        return surface

    elif state == 2:  # Alarm menu
        surface = create_empty_surface((480, 480), (0, 255, 0, 128), True)
        surface = add_text_to_surface(surface,
                           "Alarm Menu:\nSet or Cancel",
                           position=(240, 240),
                            font_size=100,
                            color=(255, 0, 0),
                             )
        return surface

    elif state == 3:  # Active alarm (waiting for time)
        # Show the alarm's set time at the top
        if alarm_time:
            surface = add_text_to_surface(
            images[index].copy(),
             datetime.datetime.now().strftime("%H:%M"),
            position=(300, 75),
            font_size=50,
            color=(255, 0, 0),
            outline=True,
            outline_color=(0, 0, 0),
            outline_width=2
             )
            surface = add_text_to_surface(
            surface,
             "*"+alarm_time.strftime("%H:%M")+"*",
            position=(100, 75),
            font_size=50,
            color=(255, 0, 0),
            outline=True,
            outline_color=(0, 0, 0),
            outline_width=2
             )
            return surface

    elif state == 4:  # Sound alarm
        surface =create_empty_surface((480, 480), (0, 255, 0, 128), True)
        surface = add_text_to_surface(surface,
                           "WAKE UP!",
                           position=(240, 240),
                            font_size=100,
                            color=(255, 0, 0),
                             )
        return surface

    else:
        return images[index]



def handle_click(pos, current_state, image_index, total_images):
    """
    Handle user input based on the current UI state and click position.
    States:
    1 - Idle
    2 - Alarm Menu
    3 - Active Alarm
    4 - Sound Alarm
    Returns: (new_state, params: dict new_index,alarm_time etc.)
    """

    print(f"Mouse clicked at: {pos} in state {current_state}")

    x, y = pos

    if current_state == 1:
        # Anywhere on screen goes to alarm menu
        print("→ State 1: Going to Alarm Menu")
        return 2, {'new_index':image_index}

    elif current_state == 2:
        # Example layout:
        # Top half: "Set Alarm" (go to active)
        # Bottom half: "Cancel" (go back to idle)
        if y < 240:
            print("→ State 2: Set Alarm")
            alarm_time = (datetime.datetime.now() + timedelta(minutes=1)).replace(second=0, microsecond=0)
            print(alarm_time)
            return 3,  {'new_index': image_index, 'alarm_time': alarm_time}
        else:
            print("→ State 2: Cancel Alarm Menu")
            return 1,  {'new_index':image_index}

    elif current_state == 3:
        # Split screen horizontally into two buttons
        # Top: "Cancel Alarm"
        # Bottom: "Keep Alarm"
        if y < 240:
            print("→ State 3: Cancel Alarm, return to Idle")
            return 1,  {'new_index':image_index}
        else:
            print("→ State 3: Keep Alarm Active")
            return 3,  {'new_index':(image_index + 1) % total_images}

    elif current_state == 4:
        # Anywhere cancels alarm
        print("→ State 4: Alarm Acknowledged, returning to Idle")
        return 1, {'new_index':image_index}

    print("→ No valid action detected")
    return current_state, {'new_index':image_index}