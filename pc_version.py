import json
import datetime
from datetime import timedelta
import requests
import io
import time
import pygame
from urllib.request import urlopen

from common_funs import *


    
def display_images(images, click_handler):
    pygame.init()
    screen = pygame.display.set_mode((480, 480))
    pygame.display.set_caption("NASA EPIC Images")
    clock = pygame.time.Clock()
    running = True
    index = 0

    state=1
    alarm_time=None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                state, params = click_handler(pos,state, index, len(images))  # Use the handler here
                index=params['new_index']
                if state==3: alarm_time=params['alarm_time']
                else: alarm_time=None
        if alarm_time and alarm_time <= datetime.datetime.now() < (alarm_time + timedelta(minutes=1)):
            state = 4
            
        #print((state, index, images,alarm_time))
        screen.blit(get_display_image(state, index, images,alarm_time), (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

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
pygame.init()

if processed_images:
    display_images(raw_images   ,handle_click)
else:
    print("No images to display.")
