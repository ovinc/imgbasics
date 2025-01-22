"""Cropping image tools and related functions."""


import matplotlib.pyplot as plt
import matplotlib.patches as patches
from drapo import ginput, rinput


# ======================= IMCROP and related functions =======================


def _cropzone_draw(ax, cropzone, c='r', linewidth=2):
    """Draw cropzone on axes.

    Parameters
    ----------
    cropzone : (int, int, int, int)
        location of the cropping zone (x, y, width, height)
    c : str
        which color to use to draw the zone
    linewidth : int or float
        line width to use to draw the zone
    """
    x, y, w, h = cropzone
    rect = patches.Rectangle(
        (x - 1 / 2, y - 1 / 2),
        w,
        h,
        linewidth=linewidth,
        edgecolor=c,
        facecolor='none',
    )
    ax.add_patch(rect)
    ax.figure.canvas.draw()
    return rect


def imcrop(
    *args,
    color='r',
    c=None,
    cursor=None,
    draggable=False,
    message='Crop Image',
    ax=None,
    closefig=True,
    keep_rect=True,
    keep_lines=False,
    **kwargs,
):
    """Interactive (or not)image cropping function using Numpy and Matplotlib.

    Depending on how the function is called, the cropping is interactive
    (manual selection on image) or imperative (crop zone (x, y, w, h) as input):

    *INTERACTIVE*

    `img_crop, cropzone = imcrop(img)`
    Input --> image (numpy array or equivalent)
    Output --> tuple (cropped image, crop rectangle (x, y, w, h))

    *IMPERATIVE*

    `img_crop = imcrop(img, cropzone)`
    Input --> image (numpy array or equivalent), crop zone (x, y, w, h)
    Output --> cropped image

    Parameters
    ----------

    *args
        can be (img,) or (img, cropzone)
        See above.

    color : str
        color of lines / cursors in interactive mode

    c : str
        shortcut for color (overrides color if set)

    cursor : bool or None
        Whether to use or not a cursor to help selection
        If None (default), use by default but not in draggable mode
        If True, force in draggable mode,
        If False, no cursor at all.

    draggable : bool
        if True, use a draggable rectangle instead of clicks
        (only in interactive mode, see above)

    message : str
        message to show as title of the matplotlib window
        (only in interactive mode, see above)

    ax : plt.Axes or None
        if not None, image shown in the ax matplotlib axes
        (only in interactive mode, see above)

    closefig : bool
        if True (default), close figure at end of interactive selection

    keep_rect : bool
        if True (default) and not closefig, keep cropzone rectangle drawn on
        image after defining it.

    **kwargs
        any kwargs accepted by matplotlib imshow() method
        (e.g. cmap: colormap to display image in matplotlib imshow
              vmin, vmax: limiting pixel values to map cmap colors)

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
    sy, sx, *_ = img.shape  # size of image in pixels

    if len(args) == 2:
        interactive = False
        xmin, ymin, w, h = args[1]
    else:
        interactive = True

    if interactive:  # Interactive Drawing of Crop Rectangle -----------------

        clr = c if c is not None else color

        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.figure

        if 'cmap' not in kwargs and img.ndim < 3:
            kwargs['cmap'] = 'gray'

        ax.imshow(img, **kwargs)
        ax.set_title(message)
        ax.set_xlabel('Click 2 pts to define crop (opposite corners of rectangle)')

        # Manage cursor visibility depending on mode -------------------------

        if cursor is None:
            cursor_active = False if draggable else True
        else:
            cursor_active = cursor

        # --------------------------------------------------------------------

        if draggable:

            x_min, y_min, _w, _h = rinput(c=clr)

            x_max = x_min + _w
            y_max = y_min + _h

        else:

            clicks = []
            lines = []

            for i in range(2):  # two clicks for two corners

                [(x_click, y_click)] = ginput(1, cursor=cursor_active, c=clr)
                clicks.append((x_click, y_click))

                # now, draw for visual clues ---------------------------------

                x_draw, y_draw = round(x_click), round(y_click)

                # draw lines corresponding to click (the -1/2 are used so that
                # the lines extend to the edges of the pixels)
                l1, = ax.plot([-1 / 2, sx - 1 / 2], [y_draw, y_draw], ':', c=clr)
                l2, = ax.plot([x_draw, x_draw], [-1 / 2, sy - 1 / 2], ':', c=clr)
                lines.extend([l1, l2])

                fig.canvas.draw()

            [(x1, y1), (x2, y2)] = clicks

            x_min, x_max = sorted((x1, x2))
            y_min, y_max = sorted((y1, y2))

        # Now, get pixels correspongind to clicks (center of a pixel is a
        # round number)
        xmin, xmax, ymin, ymax = [int(round(z)) for z in (x_min, x_max,
                                                          y_min, y_max)]

        # Calculate witdh and height in pixels
        w = xmax - xmin + 1
        h = ymax - ymin + 1

        cropzone = xmin, ymin, w, h

        rect = _cropzone_draw(ax, cropzone, c=clr)

        if closefig:
            plt.pause(0.1)
            plt.close(fig)

        else:
            if not keep_rect:
                rect.remove()
            if not keep_lines and not draggable:
                for line in lines:
                    line.remove()

    # Now, in all cases, crop image to desired dimensions --------------------

    img_crop = img[ymin: ymin + h, xmin: xmin + w]

    if not interactive:
        return img_crop
    else:
        return img_crop, cropzone
