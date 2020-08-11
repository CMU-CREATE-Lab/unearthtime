"""The image module defines methods for downloading and handling images.

Attributes:
    - `DEFAULT_HEIGHT` : `int` = 360
    - `DEFAULT_WIDTH` : `int` = 640
    - `DimensionType` : `AspectRatio`, `float`, `int`
    - `ImageType` : `bytes`, `PIL.Image.Image`, `numpy.ndarray`, `str`, `Thumbnail`
    - `Dimension` : `namedtuple(width, height)`
"""

from __future__ import annotations

import urllib.request as request
from binascii import a2b_base64
from collections import namedtuple
from enum import Enum
from http.client import HTTPMessage
from io import BytesIO
from typing import Final, Tuple, Union

from PIL import Image
from cv2 import cvtColor, COLOR_BGR2GRAY, COLOR_RGB2GRAY
from numpy import array, ndarray
from skimage import io as skio
from skimage.metrics import structural_similarity as ssim

from .._algae.exceptions import UnearthtimeException
from .._algae.strings import ismalformedurl, noneorempty
from .._algae.utils import isint, raiseif
from .._algae.warnings import overridinginvalidinput

__all__ = ['DEFAULT_HEIGHT', 'DEFAULT_HEIGHT', 'AspectRatio', 'img_cmp', 'to_array', 'to_gray', 'to_img']

DEFAULT_HEIGHT: Final[int] = 360
DEFAULT_WIDTH: Final[int] = 640

DimensionType = Union[int, float, 'AspectRatio']
ImageType = Union[bytes, Image.Image, ndarray, str, 'Thumbnail']

Dimension = namedtuple('Dimension', ['width', 'height'])


class AspectRatio(Enum):
    """The width to height ratio of an image."""
    ONExTHREE = 1 / 3
    NINExSIXTEEN = 0.5625
    THREExFIVE = 0.6
    TWOxTHREE = 2 / 3
    THREExFOUR = 0.75
    FOURxFIVE = 0.8
    ONExONE = 1.0
    FIVExFOUR = 1.25
    FOURxTHREE = 4 / 3
    THREExTWO = 1.5
    FIVExTHREE = 5 / 3
    SIXTEENxNINE = 16 / 9
    THREExONE = 3.0

    @staticmethod
    def resolve_dimensions(width: DimensionType, height: DimensionType = None) -> Dimension:
        """Determines the dimensions of an image.

        The dimensions returned will be two integers determined based on the input
        width and height. At least one of `width` and `height` must be an `int`.
        If both `width` and `height` are `int` types, they are treated as the exact
        dimensions of the image. Only one of `width` and `height` can be a `float`
        or `AspectRatio`.

        Parameters:
            - `width` : `int`, `float`, `AspectRatio`
            - `height` : `int`, `float`, `AspectRatio` = None

        Returns:
            - `Dimension`

        """
        if isint(width):
            width = int(width) if width > 0 else DEFAULT_WIDTH

            if height is None:
                height = width
            elif isint(height):
                height = int(height)
            elif isinstance(height, float) and height > 0.0:
                height = round(width * height)
            elif isinstance(height, AspectRatio):
                height = round(width * height.value)
            else:
                overridinginvalidinput(height, AspectRatio.SIXTEENxNINE.value)
                height = round(width * AspectRatio.SIXTEENxNINE.value)
        elif isint(height):
            height = int(height) if height > 0 else DEFAULT_HEIGHT

            if width is None:
                width = height
            elif isinstance(width, float) and width > 0.0:
                width = round(width * height)
            elif isinstance(width, AspectRatio):
                width = round(width.value * height)
            else:
                overridinginvalidinput(width, AspectRatio.NINExSIXTEEN.value)
                width = round(height * AspectRatio.NINExSIXTEEN.value)
        else:
            overridinginvalidinput((width, height), (DEFAULT_WIDTH, DEFAULT_HEIGHT))
            width, height = DEFAULT_WIDTH, DEFAULT_HEIGHT

        return Dimension(width, height)


class Thumbnail:
    """A downloadable thumbnail image"""

    def __init__(self, url: str, dimension: Dimension):
        """
        Parameters:
            - `url` : `str`
            - `dimension` : `Dimension`

        Raises:
            - `UnearthtimeException` : Invalid `url`.

        """
        raiseif(
            ismalformedurl(url),
            UnearthtimeException(':[%s]: Invalid URL.' % url)
        )

        self.__png = None
        self.__url = url
        self.__dim = dimension

    @property
    def height(self) -> int:
        """The height of the image"""
        return self.__dim.height

    @property
    def png(self) -> Union[Tuple[str, HTTPMessage], None]:
        """The downloaded png of the thumbnail.
        Note:
            - If this is `None`, then the image hasn't been downloaded,
            and can be downloaded using the `download_png(path)` method.
        """
        return self.__png

    @property
    def url(self) -> str:
        """The URL of the image to be downloaded."""
        return self.__url

    @property
    def width(self) -> int:
        """The width of the thumbnail."""
        return self.__dim.width

    def download_png(self, path: str) -> Tuple[str, HTTPMessage]:
        """Downloads the thumbnail as a png.

        Parameters:
            - `path` : `str`

        Returns:
            - (`str`, `http.client.HTTPMessage`)
        """
        if (self.__png is None or self.__png[0] != path) and not noneorempty(path):
            self.__png = request.urlretrieve(self.__url, path)

        return self.__png


def img_cmp(img1: ImageType, img2: ImageType) -> float:
    """Compares two images using structural similarity.

    Parameters:
        - `img1` : `bytes`, `PIL.Image.Image`, `ndarray`, `str`, `Thumbnail`
        - `img2` : `bytes`, `PIL.Image.Image`, `ndarray`, `str`, `Thumbnail`

    Returns:
        - `float`
    """
    return ssim(to_gray(img1), to_gray(img2)) if img1 is not None and img2 is not None else -1.0


def to_array(img: ImageType) -> ndarray:
    """Converts an image to an `ndarray`.

    Parameters:
        - `img` : `bytes`, `PIL.Image.Image`, `ndarray`, `str`, `Thumbnail`

    Returns:
        - `ndarray`
    """
    return img if isinstance(img, ndarray) else array(to_img(img))


def to_gray(img: ImageType):
    """Converts an image to grayscale.

        Parameters:
            - `img` : `bytes`, `PIL.Image.Image`, `ndarray`, `str`, `Thumbnail`

        Returns:
            - `ndarray`
    """
    if isinstance(img, Image.Image):
        return cvtColor(array(img), COLOR_RGB2GRAY)
    elif isinstance(img, ndarray):
        return cvtColor(img, COLOR_RGB2GRAY)
    elif isinstance(img, bytes):
        return cvtColor(array(Image.open(BytesIO(img))), COLOR_RGB2GRAY)
    elif isinstance(img, str):
        return cvtColor(array(Image.open(BytesIO(a2b_base64(img)))), COLOR_RGB2GRAY)
    else:
        return cvtColor(skio.imread(img.url), COLOR_BGR2GRAY)


def to_img(img: ImageType) -> Image.Image:
    """Converts an image to a PIL Image.

            Parameters:
                - `img` : `bytes`, `PIL.Image.Image`, `ndarray`, `str`, `Thumbnail`

            Returns:
                - `PIL.Image.Image`
        """
    if isinstance(img, Image.Image):
        return img
    elif isinstance(img, ndarray):
        return Image.fromarray(img, 'RGB')
    elif isinstance(img, bytes):
        return Image.open(BytesIO(img))
    elif isinstance(img, str):
        return Image.open(BytesIO(a2b_base64(img)))
    else:
        return Image.fromarray(skio.imread(img.url), 'RGB')
