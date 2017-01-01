
from collections import namedtuple

from PIL import Image
from PIL import ImageFont, ImageDraw, ImageStat

SECONDS_PER_SLIDE = 6
FRAMES_PER_SECOND = 30
TRANSITION_FRAMES = 18

SLIDE_FRAMES = SECONDS_PER_SLIDE * FRAMES_PER_SECOND
NUM_FRAMES = SLIDE_FRAMES + (TRANSITION_FRAMES * 2)

FONT = ImageFont.truetype('./fonts/MerriweatherSans-Regular.ttf', 55)

Point = namedtuple('Point', ['x', 'y'])

RESOLUTION = Point(1920, 1080)
ASPECT_RATIO = RESOLUTION.x / RESOLUTION.y


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
        self.start_position_factor = start_position
        self.end_scale = end_scale
        self.end_position_factor = end_position

    def load(self):
        self.original = Image.open(self.filename)
        self.start_position = self.image_width * self.start_position_factor[0], self.image_height * self.start_position_factor[1]
        self.end_position = self.image_width * self.end_position_factor[0], self.image_height * self.end_position_factor[1]

    def frame(self, n):
        progress = n / self.num_frames

        center = interpolate_position(progress, self.start_position, self.end_position)
        scale = interpolate_scale(progress, self.start_scale, self.end_scale)

        rect = contained_rect(self.image_width, self.image_height, center, ASPECT_RATIO)
        rect = scale_rect(rect, scale)

        img = self.original.transform(RESOLUTION, Image.EXTENT, (rect[0].x, rect[0].y, rect[1].x, rect[1].y), Image.BICUBIC)
        return img


def scale_rect(rect, scale):
    '''rect contains two points. apply the scale factor but keep the rectangle centered'''
    width = rect[1].x - rect[0].x
    height = rect[1].y - rect[0].y
    delta_x = (width - (width * scale)) / 2
    delta_y = (height - (height * scale)) / 2
    return Point(rect[0].x + delta_x, rect[0].y + delta_y), Point(rect[1].x - delta_x, rect[1].y - delta_y)


def contained_rect(image_width, image_height, center_point, aspect_ratio):
    """
    given a point (x,y) inside an image with width and height
    find the largest rectangle that will fit inside the image matching the aspect ratio
    that has the center point.
    """
    width = min(center_point.x, image_width - center_point.x)
    height = min(center_point.y, image_height - center_point.y)
    if (width / height) > aspect_ratio:
        # too wide
        width = aspect_ratio * height
    else:
        height = width / aspect_ratio
    return Point(center_point.x - width, center_point.y - height), Point(center_point.x + width, center_point.y + height)


def interpolate_position(progress, p1, p2):
    """
    progress is a float between 0,1
    return a position that is a linear interpolation between p1 and p2
    """
    return Point(p2[0]*progress + p1[0]*(1-progress), p2[1]*progress + p1[1]*(1-progress))


def interpolate_scale(progress, start, end):
    return start * (1-progress) + end * progress