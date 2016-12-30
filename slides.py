
from PIL import Image
from PIL import ImageFont, ImageDraw, ImageStat

RESOLUTION = (1920, 1080)

SECONDS_PER_SLIDE = 6
FRAMES_PER_SECOND = 30
TRANSITION_FRAMES = 18

SLIDE_FRAMES = SECONDS_PER_SLIDE * FRAMES_PER_SECOND
NUM_FRAMES = SLIDE_FRAMES + (TRANSITION_FRAMES * 2)

FONT = ImageFont.truetype('./fonts/MerriweatherSans-Regular.ttf', 55)

class IntroSlide(object):
    """full size image to fit video resolution"""
    def __init__(self, filename):
        self.filename = filename
        self.num_frames = 1
        self.slide_frames = 1

    @property
    def image_width(self):
        return self.original.size[0]

    @property
    def image_height(self):
        return self.original.size[1]

    def load(self):
        self.original = Image.open(self.filename)

        # crop the image if necessary to cover full screen
        if (self.image_width/self.image_height) > (RESOLUTION[0]/RESOLUTION[1]):
            height = self.image_height
            width = int(self.image_height * RESOLUTION[0] / RESOLUTION[1])
        else:
            width = self.image_width
            height = int(self.image_width * RESOLUTION[1] / RESOLUTION[0])

        self.original = self.original.transform(RESOLUTION, Image.EXTENT, (0, 0, width, height), Image.BICUBIC)

    def frame(self, n):
        return self.original

class KenBurnsSlide(IntroSlide):
    def __init__(self, filename, start_scale, start_position, end_scale, end_position):
        self.filename = filename
        self.num_frames = NUM_FRAMES
        self.slide_frames = SLIDE_FRAMES
        self.start_scale = start_scale
        self.start_position = start_position
        self.end_scale = end_scale
        self.end_position = end_position


    def load(self):
        self.original = Image.open(self.filename)

        # if (self.image_width/self.image_height) > (RESOLUTION[0]/RESOLUTION[1]):
        #     width = self.image_width
        #     height = int(self.image_width * RESOLUTION[1] / RESOLUTION[0])
        # else:
        #     height = self.image_height
        #     width = int(self.image_height * RESOLUTION[0] / RESOLUTION[1])

        # if self.original.size != (width, height):
        #     img = Image.new('RGB', (width, height))
        #     x_offset = int((width - self.image_width) / 2)
        #     y_offset = int((height - self.image_height) / 2)
        #     img.paste(self.original, (x_offset, y_offset))
        #     self.original = img
        #     img.save('resized.jpg', 'jpeg')

    def frame(self, n):
        progress = n / self.num_frames

        def blendPoint(progress, p1, p2):
            return (p2[0]*progress + p1[0]*(1-progress), p2[1]*progress + p1[1]*(1-progress))
        scale = self.start_scale * (1-progress) + self.end_scale * progress
        pos = blendPoint(progress, self.start_position, self.end_position)

        width = self.image_width * scale
        height = self.image_height * scale
        center_x = self.image_width /2 # * pos[0]
        center_y = self.image_height #+ pos[1]
        # print(scale)

        img = self.original.transform(RESOLUTION, Image.EXTENT, (center_x - width/2, center_y - height/2, center_x + width/2, center_y + height/2), Image.BICUBIC)
        return img
