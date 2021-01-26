"""Tests for the imgbasics module (pytest), basic functions (imcrop, etc.)"""

# Standard library
from pathlib import Path

# Non standard modules
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, measure

# Local module
import imgbasics
from imgbasics import contour_properties, closest_contour, imcrop, contour_coords
from imgbasics.imcrop import _cropzone_draw


# =============================== Misc. config ===============================

datafolder = Path(imgbasics.__file__).parent / '..' / 'data'

# =========== Test contour properties calculations with a hexagon ============


def test_contprops():

    # Make hexagon
    lh = 1 / np.sqrt(3)
    xp = np.array([1, 1, 0, -1, -1, 0]) / 2
    yp = np.array([-lh, lh, 2 * lh, lh, -lh, -2 * lh]) / 2

    # Calculate properties of hexagon
    contprops = contour_properties(xp, yp)

    x, y = contprops['centroid']
    p = contprops['perimeter']
    a = contprops['area']

    assert round(x, 6) == 0
    assert round(y, 6) == 0
    assert round(p, 4) == 3.4641
    assert round(a, 4) == -0.8660


# =========== Test find closest contour to position on real image ============
# (also re-tests contour_properties on more realistic example)

img = io.imread(datafolder / 'example.png')
contours = measure.find_contours(img, 170)

def test_contours_1():

    c = closest_contour(contours, (221, 281))  # should select the lowest, white spot
    xs, ys = contour_coords(c, source='scikit')

    contprops = contour_properties(xs, ys)

    x, y = contprops['centroid']
    p = contprops['perimeter']
    a = contprops['area']

    assert round(x) == 232
    assert round(y) == 280
    assert round(p) == 54
    assert round(a) == -219


# ============== Test imcrop with a random numpy array as image ==============


img2 = np.random.randint(0, 256, (20, 20))
cropzone = [5, 7, 13, 11]
img_crop = imcrop(img2, cropzone)


def test_imcrop_1():  # check that output of imcrop has correct shape
    assert img_crop.shape == (11, 13)


def test_imcrop_2():  # check that interactive option returns the same
    fig, ax = plt.subplots()
    ax.imshow(img2)
    _cropzone_draw(ax, cropzone, linecolor='b')
    msg = 'Redefine blue crop zone (click slightly inside of rectangle)'
    img_crop_2, cropzone_2 = imcrop(img2, ax=ax, message=msg)
    assert (img_crop_2 == img_crop).all()
