"""Tests for the imgbasics module (pytest), basic functions (imcrop, etc.)"""

# Standard library
from pathlib import Path

# Non standard modules
from skimage import io

# Local module
import imgbasics
from imgbasics.transform import rotate


# =============================== Misc. config ===============================


datafolder = Path(imgbasics.__file__).parent / '..' / 'data'

img = io.imread(datafolder / 'example.png')
img_color = io.imread(datafolder / 'example_color.png')


# ========================== Test transform module ===========================


def test_transform_rotate():
    """23 degrees rotation with frame resize to fit all rotated image."""
    img_rot = rotate(img, angle=-23, resize=True, order=3)
    assert img_rot.shape == (569, 608)


def test_transform_rotate_color():
    """Same but with a color image, and no resize (same size before/after)."""
    img_rot = rotate(img_color, angle=-23)
    assert img_rot.shape == img_color.shape
