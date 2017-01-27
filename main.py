#!/usr/bin/env python3.6
"""
I have a bunch of data and photos of charter boats (not included in this repository)
This script iterates through that dataset and generates a promotional video for each boat (provided there is enough data to create it)
"""

from collections import deque
import json
import http.client
import os
import sys
import random

from slides import KenBurnsSlide, IntroSlide
from render import render_slides, render_audio, render_captions
from upload_video import get_authenticated_service, initialize_upload


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
    return f'{boat_info["name"]}.mp4'


def image_paths_in(root: str):
    images = []
    for root, subdirs, files in os.walk(root):
        for f in files:
            if f[f.rfind('.'):] in ['.jpg', '.jpeg'] and \
                'brochure99' not in f:
                images.append(os.path.join(root, f))
    return images


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def upload_video(filename, boat_info):
    if not os.path.exists(filename):
        exit("file not found.")

    try:
        args = AttrDict()
        args.update({
            'file': filename,
            'title': boat_info['name'],
            'description': boat_info['link'] + '\n\n' + boat_info['description'] + '\n\nMusic by bensound.com',
            'category': 19,
            'keywords': 'charter, yacht,' + ','.join((boat_info['summer_operations'], boat_info['winter_operations'], boat_info['type'])),
            'logging_level': 'info',
            'privacyStatus': 'public'
        })
        youtube = get_authenticated_service(args)
        initialize_upload(youtube, args)
    except http.client.HTTPException as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))


def main():
    i = 0
    for root, subdirs, files in os.walk('./data/'):
        for f in files:
            if f == 'meta.json':
                i = i + 1
                print(f'Video {i}')
                if i > 10:
                    sys.exit()
                if i <= 4:
                    continue

                with open(os.path.join(root, f)) as boat_file:
                    boat_info = json.load(boat_file)
                pictures = image_paths_in(root)
                filename = make_video(boat_info, pictures)
                filename= f'{boat_info["name"]}.mp4'
                upload_video(filename, boat_info)


if __name__ == '__main__':
    main()