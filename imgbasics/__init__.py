"""Image analysis tools."""

from .cropping import imcrop
from .contours import closest_contour, contour_properties, contour_coords
from .contours import ContourError

from importlib_metadata import version

__author__ = 'Olivier Vincent'
__version__ = version("imgbasics")
__license__ = 'BSD 3-Clause'
