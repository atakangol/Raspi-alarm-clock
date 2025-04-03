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

def display_images(images):
    pygame.init()
    screen = pygame.display.set_mode((480, 480))
    pygame.display.set_caption("NASA EPIC Images")
    clock = pygame.time.Clock()
    running = True
    index = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.blit(images[index], (0, 0))
        pygame.display.flip()
        index = (index + 1) % len(images)
        time.sleep(5)
    
    pygame.quit()

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
    

urls = check_for_new_imgs()
raw_images = read_images(urls)

read_images_from_file()

processed_images = process_images(raw_images)
if processed_images:
    display_images(processed_images)
else:
    print("No images to display.")
