import json
import datetime
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

def display_images(images, click_handler):
    pygame.init()
    screen = pygame.display.set_mode((480, 480))
    pygame.display.set_caption("NASA EPIC Images")
    clock = pygame.time.Clock()
    running = True
    index = 0

    state=1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                state, index = click_handler(pos,state, index, len(images))  # Use the handler here

        screen.blit(get_display_image(state, index, images), (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def create_text_image(text, bg_color, text_color, size=(480, 480), font_size=36):
    """
    Creates a Pygame Surface with the given text.
    """
    font = pygame.font.SysFont(None, font_size)
    surface = pygame.Surface(size)
    surface.fill(bg_color)

    lines = text.split("\n")
    y = 100
    for line in lines:
        rendered_text = font.render(line, True, text_color)
        rect = rendered_text.get_rect(center=(size[0] // 2, y))
        surface.blit(rendered_text, rect)
        y += font_size + 10

    return surface


def get_display_image(state, index, images, alarm_time='07:00:00'):
    """
    Returns the image to display based on the current state and image index.
    """
    if state == 1:  # Idle - just rotate images
        return images[index]

    elif state == 2:  # Alarm menu
        return create_text_image("Alarm Menu:\nSet or Cancel", (255, 255, 255), (255, 0, 0))

    elif state == 3:  # Active alarm (waiting for time)
        # Show the alarm's set time at the top
        if alarm_time:
            time_text = f"Alarm set for: {alarm_time.strftime('%H:%M:%S')}"
            time_image = create_text_image(time_text, (0, 0, 0), (255, 255, 255), size=(480, 50), font_size=24)
            # Create a new surface combining the time text on top and the image below
            surface = pygame.Surface((480, 480))
            surface.fill((0, 0, 0))  # Black background
            surface.blit(time_image, (0, 0))  # Blit the time text
            surface.blit(images[index], (0, 50))  # Blit the image below the time text
            return surface

    elif state == 4:  # Sound alarm
        return create_text_image("WAKE UP!", (255, 255, 255), (255, 0, 0))

    else:
        return images[index]





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
    
def handle_click(pos, current_state, image_index, total_images, current_time=None):
    """
    Handle user input based on the current UI state and click position.
    States:
    1 - Idle
    2 - Alarm Menu
    3 - Active Alarm
    4 - Sound Alarm
    Returns: (new_state, new_index)
    """

    print(f"Mouse clicked at: {pos} in state {current_state}")

    x, y = pos

    if current_state == 1:
        # Anywhere on screen goes to alarm menu
        print("→ State 1: Going to Alarm Menu")
        return 2, image_index

    elif current_state == 2:
        # Example layout:
        # Top half: "Set Alarm" (go to active)
        # Bottom half: "Cancel" (go back to idle)
        if y < 240:
            print("→ State 2: Set Alarm")
            return 3, image_index
        else:
            print("→ State 2: Cancel Alarm Menu")
            return 1, image_index

    elif current_state == 3:
        # Split screen horizontally into two buttons
        # Top: "Cancel Alarm"
        # Bottom: "Keep Alarm"
        if y < 240:
            print("→ State 3: Cancel Alarm, return to Idle")
            return 1, image_index
        else:
            print("→ State 3: Keep Alarm Active")
            return 3, (image_index + 1) % total_images

    elif current_state == 4:
        # Anywhere cancels alarm
        print("→ State 4: Alarm Acknowledged, returning to Idle")
        return 1, image_index

    print("→ No valid action detected")
    return current_state, image_index



#urls = check_for_new_imgs()
#raw_images = read_images(urls)
"""
States:
    1 - Idle
    2 - Alarm Menu
    3 - Active Alarm
    4 - Sound Alarm
"""
raw_images = read_images_from_file()

processed_images = process_images(raw_images)
if processed_images:
    display_images(processed_images,handle_click)
else:
    print("No images to display.")
