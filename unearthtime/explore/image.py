from __future__ import annotations
from _algae.utils import raiseif
from _algae.exceptions import UnearthtimeException
from _algae.strings import noneorempty

from binascii import a2b_base64
from cv2 import cvtColor, COLOR_BGR2GRAY, COLOR_RGB2GRAY
from enum import Enum
from functools import singledispatchmethod as overloaded
from io import BytesIO
from numpy import array, ndarray
from PIL import Image
from skimage import io as skio
from skimage.metrics import structural_similarity as ssim
from typing import Final, Tuple, Union

import urllib.request as request

__all__ = ['DEFAULT_WIDTH', 'DEFAULT_HEIGHT', 'AspectRatio', 'Thumbnail', 'togray', 'img_cmp']

DEFAULT_WIDTH: Final[int] = 640
DEFAULT_HEIGHT: Final[int] = 360

Dimension = Union[int, float, 'AspectRatio']
ImageType = Union[bytes, str, 'Thumbnail']

class AspectRatio(Enum):
    ONExONE = 1.0
    ONExTHREE = 1/3
    TWOxTHREE = 2/3
    THREExONE = 3.0
    THREExTWO = 1.5
    THREExFOUR = 0.75
    THREExFIVE = 0.6
    FOURxTHREE = 4/3
    FOURxFIVE = 0.8
    FIVExTHREE = 5/3
    FIVExFOUR = 1.25
    NINExSIXTEEN = 0.5625
    SIXTEENxNINE = 16/9

    @staticmethod
    def resolve_dimensions(width: Dimension, height: Dimension = None) -> Tuple[int, int]:

        if isinstance(width, int) or hasattr(width, '__index__'):
            w = n_width if (n_width := width.__index__()) > 0 else DEFAULT_WIDTH

            if isinstance(height, int) or hasattr(height, '__index__'):
                h = height.__index__()
            elif isinstance(height, float) and height > 0.0:
                h = round(w * height)
            elif isinstance(height, AspectRatio):
                h = round(w * height.value)
            elif height is None:
                h = w
            else:
                h = round(w * AspectRatio.SIXTEENxNINE.value)

        elif isinstance(height, int) or hasattr(height, '__index__'):
            h = n_height if (n_height := height.__index__()) > 0 else DEFAULT_HEIGHT

            if isinstance(width, float) and width > 0.0:
                w = round(h * width)
            elif isinstance(width, AspectRatio):
                w = round(h * width.value)
            elif width is None:
                w = h
            else:
                w = round(h * AspectRatio.NINExSIXTEEN.value)

        else:

            w = DEFAULT_WIDTH
            h = DEFAULT_HEIGHT

        return w, h


class Thumbnail(object):

    def __init__(self, url: str, width: Dimension, height: Dimension):
        self.__png = None
        self.__url = url
        self.__width, self.__height = AspectRatio.resolve_dimensions(
            width, height)

    @property
    def height(self) -> int: return self.__height

    @property
    def URL(self) -> str: return self.__url

    @property
    def width(self) -> int: return self.__width

    def download_png(self, path: str):
        if (self.__png is None or self.__png[0] != path) and not (noneorempty(self.__url) or noneorempty(path)):
            self.__png = request.urlretrieve(self.__url, path)

def toimg(img: ImageType):
    if isinstance(img, Image.Image):
        return img
    elif isinstance(img, ndarray):
        return Image.fromarray(img, 'RGB')
    elif isinstance(img, bytes):
        return Image.open(BytesIO(img))
    elif isinstance(img, str):
        return Image.open(BytesIO(a2b_base64(img)))
    elif isinstance(img, Thumbnail):
        return Image.fromarray(skio.imread(img.URL), 'RGB')
    
def toarray(img: ImageType):
    if isinstance(img, ndarray):
        return img
    else:
        return array(toimg(img))

def togray(img: ImageType) -> ndarray:
    if isinstance(img, Image.Image):
        return cvtColor(array(img), COLOR_RGB2GRAY)
    elif isinstance(img, ndarray):
        return cvtColor(img, COLOR_RGB2GRAY)
    elif isinstance(img, bytes):
        return cvtColor(array(Image.open(BytesIO(img))), COLOR_RGB2GRAY)
    elif isinstance(img, str):
        return cvtColor(array(Image.open(BytesIO(a2b_base64(img)))), COLOR_RGB2GRAY)
    elif isinstance(img, Thumbnail):
        return cvtColor(skio.imread(img.URL), COLOR_BGR2GRAY)

def imgcmp(img1: ImageType, img2: ImageType) -> float:
    return ssim(togray(img1), togray(img2)) if (img1 is not None and img2 is not None) else -1.0