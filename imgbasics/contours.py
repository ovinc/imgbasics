"""Image analysis based on iso-gray level contours."""


import numpy as np


# ========================= Custom Contour Exception =========================

class ContourError(Exception):
    pass

# ======================== General contour functions =========================


def contour_coords(contour, source='scikit'):
    """Extract x, y tuple of contour positions from contour data.

    Scikit has reversed x, y coordinates
    OpenCV has an unusual numpy array shape (npts, 1, 2)

    Parameters
    ----------
    contour : array_like
        Contour data.
    source : str
        Can be 'scikit' or 'opencv'.

    Returns
    -------
    tuple of numpy arrays
        (x, y) that can be used directly on an imshow() graph
    """
    if source == 'scikit':
        return contour[:, 1], contour[:, 0]
    elif source == 'opencv':
        contour = contour.squeeze()   # eliminate middle dimension in array
        return contour[:, 0], contour[:, 1]
    else:
        raise ValueError(f'{source} not a valid source for contour data.')


def contour_properties(x, y):
    """Returns centroid position, perimeter and area of a contour (x, y, p, a)

    Parameters
    ----------
    x : array_like
    y : array_like
        x, y are the coordinates of contour (must support math operations)

    Returns
    -------
    dict
        Dictionary with keys:
        - 'centroid': typle (x, y) of centroid position
        - 'perimeter': contour length (float)
        - 'area': signed area (float)

    Examples
    --------

    Test can be done with the following hexagon :

    >>> l = 1 / np.sqrt(3)
    >>> xp = np.array([1, 1, 0, -1, -1, 0]) / 2
    >>> yp = np.array([-l, l, 2 * l, l, -l, -2 * l]) / 2
    >>> x, y, p, a = contour_properties(xp, yp)

    should return
    x = 0, y = 0, p = 6/sqrt(3) ~ 3.4641, a = -sqrt(3)/2 ~ -0.8660

    (area is negative because the contour is anti-clockwise with respect to an
    imshow plot, and clockwise with respect to a standard plot.)
    """
    # shift data around approx. center of contour (useful?)
    xm, ym = np.mean(x), np.mean(y)
    x = x - xm
    y = y - ym

    # derivatives of x and y
    x_looped = np.append(x, x[0])   # loop in case contour is not closed
    y_looped = np.append(y, y[0])
    dx = np.diff(x_looped)
    dy = np.diff(y_looped)

    # signed area and perimeter are straightforward to calculate
    area = np.sum(y * dx - x * dy) / 2          # area
    perimeter = np.sum(np.sqrt(dx**2 + dy**2))  # perimeter

    # moments are needed for centroid position calculation
    Ma = np.sum((y * dx**2 - x**2 * dy) / 4 + x * y * dx / 2 + dx**2 * dy / 12)
    Mb = np.sum((y**2 * dx - x * dy**2) / 4 - x * y * dy / 2 - dy**2 * dx / 12)

    # centroid position
    xc = Ma / area + xm
    yc = Mb / area + ym

    return {
        'centroid': (xc, yc),
        'perimeter': perimeter,
        'area': area,
    }


def closest_contour(contours, position, edge=False, source='scikit'):
    """Finds the closest contour (skimage) to a certain position (tuple x, y)

    Parameters
    ----------
    contours : iterable of array_like
        list of contours obtained from skimage or opencv analysis
        (must be numpy arrays)
    position : tuple of floats
        position of point (x, y)
    edge : bool
        if True, returns the contour with the edge closest to the position
        if False (default), returns the contour with the average position
        closest to position.
    source : str
        Can be 'scikit' or 'opencv'

    Returns
    -------
    array_like
        Contour within the initial list that is the closest to position
    """
    if len(contours) == 0:
        raise ContourError('No Contours Available')

    if len(contours) == 1:  # just one contour, no need to sort contours
        contour, = contours
        return contour

    else:
        x, y = position
        dists = []  # will store distances to position

        for contour in contours:

            xcont, ycont = contour_coords(contour, source)

            # center mode: compare approx. center of contour to position
            if not edge:
                dists.append(np.hypot(x - xcont.mean(), y - ycont.mean()))
            # edge mode: compare closest point on contour edge to position
            else:
                localdists = np.hypot(xcont - x, ycont - y)
                dists.append(localdists.min())

        imin = dists.index(min(dists))  # returns only first index if several ok

        return contours[imin]
