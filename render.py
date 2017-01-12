import os
import random
import subprocess
import time
import tempfile

from PIL import Image
import moviepy.audio.fx.all as afx
import moviepy.editor as mp
from moviepy.video.tools.segmenting import findObjects

from slides import TRANSITION_FRAMES

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
    time.sleep(1) # time to finsih writing to disk

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


def render_captions(video, meta_info):
    txt_clip = mp.TextClip(meta_info['name'], fontsize=70, color='white', font="fonts/MerriweatherSans-Regular.ttf",)
    txt_clip = txt_clip.set_pos('center').set_duration(10)
    video = mp.CompositeVideoClip([video, txt_clip])
    # txtClip = TextClip(meta_info['name'], color='white', font="MerriweatherSans",
    #                    kerning=5, fontsize=100)
    # cvc = CompositeVideoClip([txtClip.set_pos('center')],
    #                          size=video.size, transparent=True)

    # letters = findObjects(cvc)

    # clips = [ CompositeVideoClip( moveLetters(letters,funcpos),
    #                             size = screensize).subclip(0,5)
    #         for funcpos in [vortex, cascade, arrive, vortexout] ]
    return video