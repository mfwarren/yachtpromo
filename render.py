import os
import random
import subprocess
import time
import tempfile
import textwrap

from PIL import Image
import moviepy.audio.fx.all as afx
import moviepy.editor as mp
from moviepy.video.tools.segmenting import findObjects

from slides import TRANSITION_FRAMES
from add_captions import moveLetters, arrive, vortexout

MUSIC_FILES = []

for root, subdirs, files in os.walk('./music/'):
    for f in files:
        if f.endswith('.mp3'):
            MUSIC_FILES.append(os.path.join(root, f))


def render_slides(slides):
    """
    uses ffmpeg to render images to a mp4 temp file
    load file into moviepy VideoClip and return when complete
    """
    handle, export_file = tempfile.mkstemp('.mp4', dir='./tmp')
    cmd = f'ffmpeg -v -1 -y -f image2pipe -vcodec ppm -i pipe: -r 30 -b 5000k "{export_file}"'
    ffmpeg = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pipe = ffmpeg.stdin
    ffmpeg.stdout.close()

    prev_slide = slides[0]
    prev_slide.load()

    while slides:
        slide = slides.popleft()
        slide.load()

        for frame in range(TRANSITION_FRAMES):
            save_frame(Image.blend(prev_slide.frame(frame+TRANSITION_FRAMES+prev_slide.slide_frames),
                                            slide.frame(frame),
                                            frame/TRANSITION_FRAMES), pipe)
        for frame in range(slide.slide_frames):
            save_frame(slide.frame(frame+TRANSITION_FRAMES), pipe)

        prev_slide = slide

    pipe.close()
    time.sleep(5) # time to finsih writing to disk

    return mp.VideoFileClip(export_file)


def save_frame(image, pipe):
    print(".", end='', flush=True)
    image.save(pipe, 'ppm')


def render_audio(video):
    """
    Finds a random song and adds the audio track to the video clip
    adds a fade out at the end to avoid an abrupt end
    """
    song = random.choice(MUSIC_FILES)
    audio = mp.AudioFileClip(song)
    audio = audio.set_duration(video.duration)
    audio = afx.audio_fadeout(audio, 1.0)
    return video.set_audio(audio)


def caption_clip(text, size, position='center'):
    txt_clip = mp.TextClip(text, fontsize=70, color='white', stroke_color="black", font="fonts/MerriweatherSans-Regular.ttf",)
    txt_clip = mp.CompositeVideoClip([txt_clip.set_pos(position)], size=size)
    # .set_duration(10)
    letters = findObjects(txt_clip)
    return [mp.CompositeVideoClip(moveLetters(letters, arrive), size=size).subclip(0,5),
            mp.CompositeVideoClip(moveLetters(letters, vortexout), size=size).subclip(0,5)]

def unanimated_clip(text, size, position=('center', 'bottom'), duration=5):
    txt_clip = mp.TextClip(text, fontsize=70, color='white', bg_color="black", font="fonts/MerriweatherSans-Regular.ttf",)
    txt_clip = mp.CompositeVideoClip([txt_clip.set_pos(position)], size=size)
    return [txt_clip.set_duration(duration)]


def render_captions(video, meta_info):
    clip_sequence = []

    clip_sequence += caption_clip(meta_info['name'], video.size)
    clip_sequence += caption_clip(meta_info['summer_operations'], video.size, position=('center', 'bottom'))
    description_captions = textwrap.wrap(meta_info['description'], 50)
    for line in description_captions:
        clip_sequence += unanimated_clip(line, video.size, duration=(video.duration-20)/len(description_captions))

    txt_clip = mp.concatenate_videoclips(clip_sequence)
    video = mp.CompositeVideoClip([video, txt_clip])

    return video