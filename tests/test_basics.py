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
from imgbasics.cropping import _cropzone_draw


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

x = 5
y = 7
w = 14
h = 9

img2 = np.random.randint(0, 256, (20, 20))

cropzone = x, y, w, h
img_crop = imcrop(img2, cropzone)


def test_imcrop_1():
    """Check that output of imcrop in non-interactive mode has correct shape."""
    assert img_crop.shape == (h, w)


def test_imcrop_2():
    """Check that interactive option returns the same."""
    fig, ax = plt.subplots()
    ax.imshow(img2)
    _cropzone_draw(ax, cropzone, c='b')
    msg = 'Redefine blue crop zone (click slightly inside of rectangle)'
    img_crop_2, cropzone_2 = imcrop(img2, ax=ax, message=msg)
    assert (img_crop_2 == img_crop).all()


def test_imcrop_3():
    """Check that interactive option with draggable rectangle does the same."""
    fig, ax = plt.subplots()
    ax.imshow(img2)
    _cropzone_draw(ax, cropzone, c='b')
    msg = 'Redefine blue crop zone by dragging rectangle'
    img_crop_2, cropzone_2 = imcrop(img2, draggable=True, ax=ax, message=msg)
    assert img_crop_2.shape == img_crop.shape


# ====================== Test imcrop with a color image ======================


def test_imcrop_color():
    """Check that cropping works ok with a color image as well."""
    w = 236
    h = 71
    zone = 34, 125, w, h
    imgc = io.imread(datafolder / 'example_color.png')
    imgcrop = imcrop(imgc, zone)
    hcrop, wcrop, *_ = imgcrop.shape
    assert (hcrop, wcrop) == (h, w)
