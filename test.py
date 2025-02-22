import json
import datetime
import requests
import io
from urllib.request import urlopen
import time

import pygame

def check_for_new_imgs():
    response = requests.get("https://epic.gsfc.nasa.gov/api/enhanced")
    imjson = response.json()
    urls = []
    for photo in imjson:
        dt = datetime.datetime.strptime(photo["date"], "%Y-%m-%d %H:%M:%S")
        imageurl = "https://epic.gsfc.nasa.gov/archive/enhanced/"+str(dt.year)+ "/"+str(dt.month).zfill(2)+"/"+str(dt.day).zfill(2)+"/jpg/"+photo["image"]+".jpg"
        urls.append(imageurl)   
    return urls

    
def save_photos(urls):
    counter=0
    for imageurl in urls:
        # Create a surface object, draw image on it..
        image_file = io.BytesIO(urlopen(imageurl).read())
        image = pygame.image.load(image_file)
        # Crop out the centre 830px square from the image to make globe fill screen
        cropped = pygame.Surface((830,830))
        cropped.blit(image,(0,0),(125,125,830,830))
        cropped = pygame.transform.scale(cropped, (480,480))

        pygame.image.save(cropped,"./images/"+str(counter)+".jpg")
        counter+=1
    print("photos saved")
