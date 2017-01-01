#!/usr/bin/env python3.6
"""
I have a bunch of data and photos of charter boats (not included in this repository)
This script iterates through that dataset and generates a promotional video for each boat (provided there is enough data to create it)
"""

from collections import deque
import json
import os
import sys
import random

from slides import KenBurnsSlide, IntroSlide
from render import Renderer


def make_video(boat_info, pictures):
    print(boat_info['name'], len(pictures))
    slides = deque()
    slides.append(IntroSlide(pictures[0]))
    for picture in pictures:
        start_x = random.randrange(400, 1520)
        end_x = random.randrange(400, 1500)
        end_y = random.randrange(200, 800)
        start_y = random.randrange(200, 800)
        slides.append(KenBurnsSlide(picture, 1, (start_x, start_y), 1.4, (1000, 500)))

    Renderer(slides, f'{boat_info["name"]}.mp4')


def image_paths_in(root: str):
    images = []
    for root, subdirs, files in os.walk(root):
        for f in files:
            if f[f.rfind('.'):] in ['.png', '.jpg', '.jpeg']:
                images.append(os.path.join(root, f))
    return images


def main():
    for root, subdirs, files in os.walk('./data/'):
        for f in files:
            if f == 'meta.json':
                with open(os.path.join(root, f)) as boat_file:
                    boat_info = json.load(boat_file)
                pictures = image_paths_in(root)
                make_video(boat_info, pictures)
                sys.exit()


if __name__ == '__main__':
    main()