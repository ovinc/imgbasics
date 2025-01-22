"""Image transformation functions mimicking Scikit-Image's ones but based on
OpenCV (much faster)"""

import numpy as np
import cv2

# Correspondence between interpolation orders and corresponding commands in cv2

ORDERS = {
    0: cv2.INTER_NEAREST,
    1: cv2.INTER_LINEAR,
    3: cv2.INTER_CUBIC,
    None: cv2.INTER_LINEAR,  # the last one is default
}


def rotate(image, angle, resize=False, center=None, order=None):
    """Rotation function similar to skimage.transform.rotate()

    Parameters
    ----------
    image : array_like
        image array (numpy array or equivalent)

    angle : float
        counter-clockwise rotation angle in degrees

    resize : bool
        if True, expand image size to fit rotated image entirely

    center : (float, float)
        coords of rotation center (ignored if resize is True)

    order : int or None
        interpolation order, can be:
            - 0 (nearest neighbor)
            - 1 (bilinear)
            - 3 (bicubic)
            (if None, defaults to bilinear)

    Returns
    -------
    array_like
        Rotated image array
    """

    sy, sx, *_ = image.shape  # size of image in pixels (note inversion y/x)

    try:
        interpolation_method = ORDERS[order]
    except KeyError:
        raise ValueError(f'{order} not a valid interpolation order.')

    # Calculate size of new frame if necessary ---------------------------------------------

    if resize:

        theta = np.deg2rad(angle)
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        # Projection legnths of rotated sides on original x and y
        lxx = abs(sx * cos_theta)
        lxy = abs(sx * sin_theta)
        lyx = abs(sy * sin_theta)
        lyy = abs(sy * cos_theta)

        sx_new = lxx + lyx
        sy_new = lxy + lyy

        output_size = int(sx_new), int(sy_new)

    else:

        output_size = sx, sy

    # Calculate rotation matrix --------------------------------------------------------

    if resize or center is None:
        center = (sx / 2, sy / 2)

    M = cv2.getRotationMatrix2D(center, angle, scale=1)  # no rescaling considered here

    if resize:  # Add translation to matrix so that the result fits into the new frame
        tranlsation = (sx_new - sx) / 2, (sy_new - sy) / 2
        M[:, 2] += tranlsation  # The last column of the matrix is the translation vector

    # Create rotated image ------------------------------------------------------------

    image_rotated = cv2.warpAffine(image, M, dsize=output_size, flags=interpolation_method)

    return image_rotated
