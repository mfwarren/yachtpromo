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
from render import render_slides, render_audio


def make_video(boat_info, pictures):
    print(boat_info['name'], len(pictures))
    slides = deque()
    slides.append(IntroSlide(pictures[0]))
    for picture in pictures:
        start_x = random.random() * 0.5 + 0.25
        end_x = random.random() * 0.5 + 0.25
        end_y = random.random() * 0.5 + 0.25
        start_y = random.random() * 0.5 + 0.25
        slides.append(KenBurnsSlide(picture, 0.8, (start_x, start_y), 1.0, (end_x, end_y)))

    video_clip = render_slides(slides)
    video_clip = render_audio(video_clip)
    video_clip = render_captions(video_clip, boat_info)
    video_clip.write_videofile(f'{boat_info["name"]}.mp4')


def image_paths_in(root: str):
    images = []
    for root, subdirs, files in os.walk(root):
        for f in files:
            if f[f.rfind('.'):] in ['.jpg', '.jpeg'] and \
                'brochure99' not in f:
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