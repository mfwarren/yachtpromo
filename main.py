#!/usr/bin/env python3.6
"""
I have a bunch of data and photos of charter boats (not included in this repository)
This script iterates through that dataset and generates a promotional video for each boat (provided there is enough data to create it)
"""

import json
import os


def make_video(boat_info, pictures):
    print(boat_info['name'], len(pictures))
    # TODO


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


if __name__ == '__main__':
    main()