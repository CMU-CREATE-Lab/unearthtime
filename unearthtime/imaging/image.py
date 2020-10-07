from __future__ import annotations

from binascii import a2b_base64
from collections import namedtuple
from enum import Enum
from http.client import HTTPMessage
from io import BytesIO
from typing import Tuple, Final, Union
from urllib import request

import cv2 as cv
import imutils as im
from PIL import Image as PILImage
from numpy import array, ndarray
from skimage import io as skio
from skimage.metrics import mean_squared_error as mse
from skimage.metrics import structural_similarity as ssim

from .._algae.warnings import overridinginvalidinput
from .._algae.exceptions import UnearthtimeException
from .._algae.strings import ismalformedurl, noneorempty
from .._algae.utils import raiseif, isint

RGBColor = Tuple[int, int, int]

DEFAULT_HEIGHT: Final[int] = 360
DEFAULT_WIDTH: Final[int] = 640

DimensionType = Union[int, float, 'AspectRatio']

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


class Image:

    def __init__(self, image: ndarray, from_color_space: str = None, to_color_space: str = None):
        raiseif(
            not isinstance(image, ndarray),
            UnearthtimeException(f'Image is type [{type(image)}] and must be type `numpy.ndarray`')
        )

        self.__image, self.__color_space = Image.__resolve_image(image, from_color_space, to_color_space)
        self.__height = image.shape[0]
        self.__width = image.shape[1]

    def __copy__(self):
        return Image(self.__image.copy(), self.__color_space, self.__color_space)

    def __getattr__(self, attr):
        if hasattr(self.__image, attr):
            return getattr(self.__image, attr)

    def __abs__(self):
        return Image(self.__image.__abs__(), self.__color_space)

    def __add__(self, value, /):
        return Image(self.__image.__add__(value), self.__color_space)

    def __and__(self, value, /):
        return Image(self.__image.__and__(value), self.__color_space)

    def __bool__(self):
        return self.__image.__bool__()

    def __complex__(self):
        return self.__image.__complex__()

    def __contains__(self, value, /):
        return self.__image.__contains__(value)

    def __delitem__(self, value, /):
        self.__image.__delitem__(value)

    def __divmod__(self, value, /):
        d, m = self.__image.__divmod__(value)
        return Image(d, self.__color_space), Image(m, self.__color_space)

    def __eq__(self, value, /):
        return self.__image.__eq__(value)

    def __float__(self):
        return self.__image.__float__()

    def __floordiv__(self, value, /):
        return Image(self.__image.__floordiv__(value), self.__color_space)

    def __getitem__(self, value, /):
        return self.__image.__getitem__(value)

    def __ge__(self, value, /):
        return self.__image.__ge__(value)

    def __gt__(self, value, /):
        return self.__image.__gt__(value)

    def __iadd__(self, value, /):
        self.__image.__iadd__(value)
        return self

    def __iand__(self, value, /):
        self.__image.__iand__(value)
        return self

    def __ifloordiv__(self, value, /):
        self.__image.__ifloordiv__(value)
        return self

    def __ilshift__(self, value, /):
        self.__image.__ilshift__(value)
        return self

    def __imatmul__(self, value, /):
        self.__image.__imatmul__(value)
        return self

    def __imod__(self, value, /):
        self.__image.__imod__(value)
        return self

    def __imul__(self, value, /):
        self.__image.__imul__(value)
        return self

    def __index__(self):
        return self.__image.__index__()

    def __int__(self):
        return self.__image.__int__()

    def __invert__(self):
        return Image(self.__image.__invert__(), self.__color_space)

    def __ior__(self, value, /):
        self.__image.__ior__(value)
        return self

    def __ipow__(self, value, /):
        self.__image.__ipow__(value)
        return self

    def __irshift__(self, value, /):
        self.__image.__irshift__(value)
        return self

    def __isub__(self, value, /):
        self.__image.__isub__(value)
        return self

    def __iter__(self):
        return self.__image.__iter__()

    def __itruediv__(self, value, /):
        self.__image.__itruediv__(value)
        return self

    def __ixor__(self, value, /):
        self.__image.__ixor__(value)
        return self

    def __len__(self):
        return self.__image.__len__()

    def __le__(self, value, /):
        return self.__image.__le__(value)

    def __lshift__(self, value, /):
        return Image(self.__image.__lshift__(value), self.__color_space)

    def __lt__(self, value, /):
        return self.__image.__lt__(value)

    def __matmul__(self, value, /):
        return Image(self.__image.__matmul__(value), self.__color_space)

    def __mod__(self, value, /):
        return Image(self.__image.__mod__(value), self.__color_space)

    def __mul__(self, value, /):
        return Image(self.__image.__mul__(value), self.__color_space)

    def __neg__(self):
        return Image(self.__image.__neg__(), self.__color_space)

    def __ne__(self, value, /):
        return self.__image.__ne__(value)

    def __or__(self, value, /):
        return Image(self.__image.__or__(value), self.__color_space)

    def __pos__(self):
        return Image(self.__image.__pos__(), self.__color_space)

    def __pow__(self, value, /):
        return Image(self.__image.__pow__(value), self.__color_space)

    def __radd__(self, value, /):
        return Image(self.__image.__radd__(value), self.__color_space)

    def __rand__(self, value, /):
        return Image(self.__image.__rand__(value), self.__color_space)

    def __rdivmod__(self, value, /):
        d, m = self.__image.__rdivmod__(self, value)
        return Image(d, self.__color_space), Image(m, self.__color_space)

    def __rfloordiv__(self, value, /):
        return Image(self.__image.__rfloordiv__(value), self.__color_space)

    def __rlshift__(self, value, /):
        return Image(self.__image.__rlshift__(value), self.__color_space)

    def __rmatmul__(self, value, /):
        return Image(self.__image.__rmatmul__(value), self.__color_space)

    def __rmod__(self, value, /):
        return Image(self.__image.__rmod__(value), self.__color_space)

    def __rmul__(self, value, /):
        return Image(self.__image.__rmul__(value), self.__color_space)

    def __ror__(self, value, /):
        return Image(self.__image.__ror__(value), self.__color_space)

    def __rpow__(self, value, /):
        return Image(self.__image.__rpow__(value), self.__color_space)

    def __rrshift__(self, value, /):
        return Image(self.__image.__rrshift__(value), self.__color_space)

    def __rshift__(self, value, /):
        return Image(self.__image.__rshift__(value), self.__color_space)

    def __rsub__(self, value, /):
        return Image(self.__image.__rsub__(value), self.__color_space)

    def __rtruediv__(self, value, /):
        return Image(self.__image.__rtruediv__(value), self.__color_space)

    def __rxor__(self, value, /):
        return Image(self.__image.__rxor__(value), self.__color_space)

    def __setitem__(self, value, /):
        self.__image.__setitem__(value)

    def __sizeof__(self):
        return self.__image.__sizeof__()

    def __sub__(self, value, /):
        return Image(self.__image.__sub__(value), self.__color_space)

    def __truediv__(self, value, /):
        return Image(self.__image.__truediv__(value), self.__color_space)

    def __xor__(self, value, /):
        return Image(self.__image.__xor__(value), self.__color_space)

    @classmethod
    def from_base64(cls, base64: str, to_color_space: str = 'BGR'):
        return cls(array(PILImage.open(BytesIO(a2b_base64(base64)))), 'RGBA', to_color_space)

    @classmethod
    def from_bytes(cls, bytes_: bytes, to_color_space: str = 'BGR'):
        return cls(array(PILImage.open(BytesIO(bytes_))), 'RGBA', to_color_space)

    @classmethod
    def from_image(cls, img: PILImage, to_color_space: str = 'BGR'):
        return cls(array(img), img.mode, to_color_space)

    @classmethod
    def read_file(cls, fp: str, flags=None, to_color_space: str = 'BGR'):
        return cls(cv.imread(fp, flags), 'BGR', to_color_space=to_color_space)

    @classmethod
    def read_url(cls, url: str, from_color_space: str = 'BGR', to_color_space: str = 'BGR', plugin=None, **plugin_args):
        tcs = to_color_space.upper()

        img = skio.imread(url, as_gray=tcs in ('GRAY', 'GREY'), plugin=plugin, **plugin_args)

        if tcs in ('GRAY', 'GREY'):
            return cls(img, 'GRAY', 'GRAY')
        else:
            return cls(img, from_color_space, to_color_space)

    @property
    def array(self):
        return self.__image

    @property
    def color_space(self):
        return self.__color_space

    @property
    def height(self):
        return self.__height

    @property
    def width(self):
        return self.__width

    def as_image(self):
        return PILImage.fromarray(self.__image)

    def change_color_space(self, color_space: str):
        self.__image, self.__color_space = Image.__resolve_image(self.__image, self.__color_space, color_space)

    def compare_full(self, img: Image, rect_color: RGBColor = (0, 0, 255), line_thickness=1, line_type=cv.LINE_8):
        cim1, cim2 = self.with_color_space('BGR'), img.with_color_space('BGR')
        gim1, gim2 = cim1.with_color_space('GRAY'), cim2.with_color_space('GRAY')
        score, diff = gim1.compare_ssim(gim2, full=True)
        diff = (diff * 255).astype("uint8")
        threshold = cv.threshold(diff, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]
        contours = im.grab_contours(cv.findContours(threshold.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE))

        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)

            cv.rectangle(cim1.array, (x, y), (x + w, y + h), rect_color, line_thickness, line_type)
            cv.rectangle(cim2.array, (x, y), (x + w, y + h), rect_color, line_thickness, line_type)

        mse_ = mse(gim1.array, gim2.array)

        return {
            "mse": mse_,
            "ssim": score,
            "image1": cim1,
            "image2": cim2,
            "diff": diff,
            "threshold": threshold
        }

    def compare_mse(self, img: Image):
        return mse(self.with_color_space('GRAY').array, img.with_color_space('GRAY').array)

    def compare_ssim(self, img: Image, **kwargs):
        return ssim(self.with_color_space('GRAY').array, img.with_color_space('GRAY').array, **kwargs)

    def copy(self):
        return self.__copy__()

    def draw_rectangle(self, pt1, pt2, color: RGBColor = (0, 0, 255), line_thickness: int = 1, line_type: int = cv.LINE_8):
        cv.rectangle(self.__image, pt1, pt2, color, line_thickness, line_type)

    def save(self, fp: str = './', format_=None, **params):
        self.as_image().save(fp, format_, **params)

    def show(self, name: str):
        cv.imshow(name, self.__image)

    def with_color_space(self, color_space: str):
        return Image(self.__image.copy(), self.__color_space, color_space)

    @staticmethod
    def __resolve_image(image: ndarray, from_color_space: str, to_color_space: str):
        if from_color_space is not None:
            fcs = from_color_space.upper()
        else:
            fcs = 'GRAY' if image.ndim == 2 else 'RGB' if image.ndim == 3 else 'RGBA'

        if to_color_space is not None:
            tcs = to_color_space.upper()
        else:
            tcs = fcs

        raiseif(
            len(set([cs for cs in dir(cv) if f'COLOR_{fcs}' in cs])) == 0,
            UnearthtimeException(f':[{fcs}2{tcs}]: Invalid color space conversion.')
        )

        if fcs != tcs:
            if fcs == 'GREY':
                fcs = 'GRAY'

            if tcs == 'GREY':
                tcs = 'GRAY'

            cvtcs = f'COLOR_{fcs}2{tcs}'

            try:
                code = getattr(cv, cvtcs)
            except AttributeError:
                raise UnearthtimeException(f':[{fcs}2{tcs}]: Invalid color space conversion.')

            image = cv.cvtColor(image, code)

        return image, tcs
