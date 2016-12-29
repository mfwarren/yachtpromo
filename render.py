import subprocess
from PIL import Image
from slides import TRANSITION_FRAMES

class Renderer(object):
    def __init__(self, slides, export_file):
        cmd = f'ffmpeg -v -1 -y -f image2pipe -vcodec ppm -i pipe: -r 30 -b 5000k "{export_file}"'
        self.ffmpeg = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.pipe = self.ffmpeg.stdin
        self.ffmpeg.stdout.close()

        prev_slide = slides[0]
        prev_slide.load()

        while slides:
            slide = slides.popleft()
            slide.load()

            for frame in range(TRANSITION_FRAMES):
                self.output_frame(Image.blend(prev_slide.frame(frame+TRANSITION_FRAMES+prev_slide.slide_frames),
                                              slide.frame(frame),
                                              frame/TRANSITION_FRAMES))
            for frame in range(slide.slide_frames):
                self.output_frame(slide.frame(frame+TRANSITION_FRAMES))

            prev_slide = slide

    def output_frame(self, image):
        print(".", end='', flush=True)
        image.save(self.pipe, 'ppm')
        # image.save('file.jpg', 'jpeg')


