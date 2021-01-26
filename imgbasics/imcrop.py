"""Cropping image tools and related functions."""


import matplotlib.pyplot as plt
import matplotlib.patches as patches
from drapo import Cursor


# ======================= IMCROP and related functions =======================


def _cropzone_draw(ax, cropzone, linecolor='r', linewidth=2):
    """Draw cropzone on axes."""
    x, y, w, h = cropzone
    rect = patches.Rectangle((x - 1 / 2, y - 1 / 2), w, h, linewidth=linewidth,
                             edgecolor=linecolor, facecolor='none')
    ax.add_patch(rect)
    ax.figure.canvas.draw()
    return rect


def imcrop(*args, cmap='gray', linecolor='r', closefig=True, cursor=True,
           message='Crop Image', ax=None):
    """Interactive (or not)image cropping function using Numpy and Matplotlib.

    The *args allow to use the function in the two following ways:

    img_crop, cropzone = imcrop(img)
    --- interactive mode where the crop zone is drawn on image img. Function
    then returns the cropped image and the crop rectangle x, y, width, height

    img_crop = imcrop(img, cropzone)
    --- crops image img according to a pre-defined crop rectangle (x, y, w, h)

    Other parameters:
    - cmap: colormap to display image in matplotlib imshow
    - linecolor: color of lines / cursors in interactive mode
    - closefig: if True (default), close figure at end of interactive selection
    - cursor: if True (default), cursor around mouse to help interact. select.
    - message: message to show as title of the matplotlib window (interactive)
    - ax: if not None, image shown in the ax matplotlib axes (interactive mode)

    Note: when selecting, the pixels taken into account are those which have
    their centers closest to the click, not their edges closest to the click.
    For example, to crop to a single pixel, one needs to click two times in
    this pixel (possibly at the same location). For images with few pixels,
    this results in a visible offset between the dotted lines plotted after the
    clicks (running through the centers of the pixels clicked) and the final
    rectangle which runs along the edges of all pixels selected.

    Contrary to the Matlab imcrop function, the cropped rectangle is really of
    the width and height requested (w*h), not w+1 and h+1 as in Matlab.
    """
    img = args[0]  # load image
    sy, sx = img.shape  # size of image in pixels

    if len(args) == 2:
        interactive = False
        x, y, w, h = args[1]
    else:
        interactive = True

    if interactive:  # Interactive Drawing of Crop Rectangle -----------------

        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.figure

        ax.imshow(img, cmap=cmap)
        ax.set_title(message)
        ax.set_xlabel('Click 2 pts to define crop (opposite corners of rectangle)')

        if cursor:
            Cursor()

        clicks = []

        for i in range(2):  # two clicks for two corners

            [(x_click, y_click)] = plt.ginput(1)

            x, y = round(x_click), round(y_click)

            clicks.append((x, y))

            # draw lines corresponding to click (the -1/2 are used so that the
            # lines extend to the edges of the pixels)
            ax.plot([-1 / 2, sx - 1 / 2], [y, y], ':', color=linecolor)
            ax.plot([x, x], [-1 / 2, sy - 1 / 2], ':', color=linecolor)

            fig.canvas.draw()

        [(x1, y1), (x2, y2)] = clicks

        x = int(min(x1, x2))  # coordinates of crop rectangle
        y = int(min(y1, y2))

        w = int(max(x1, x2)) - x + 1  # width and height of crop rectangle
        h = int(max(y1, y2)) - y + 1
        # +1 takes into account pixel size so that cropbox size is w*h px**2

        cropzone = x, y, w, h

        _cropzone_draw(ax, cropzone, linecolor)

        if closefig:
            plt.pause(0.2)
            plt.close(fig)

    # Now, in all cases, crop image to desired dimensions --------------------

    img_crop = img[y: y + h, x: x + w]

    if not interactive:
        return img_crop
    else:
        return img_crop, cropzone
