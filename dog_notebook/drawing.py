"""Small Pillow drawings in scene coordinates. Written by Codex, 2026-10-24."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

COBALT = '#24489c'
TEAL = '#319a98'
RED = '#cf5044'
GRAY = '#888888'


class Canvas:
    """A square view: positive x right, positive y up; width in scene units."""

    def __init__(self, pixels=480, width=10):
        self.pixels = pixels
        self.width = width
        self.factor = pixels * 2 / width
        self.clear()

    def clear(self):
        self.image = Image.new('RGB', (self.pixels * 2,) * 2, 'white')
        self.pen = ImageDraw.Draw(self.image)

    def point(self, point):
        x, y = point[:2]
        middle = self.pixels
        return middle + x * self.factor, middle - y * self.factor

    def line(self, points, color=GRAY, width=2):
        points = [self.point(p) for p in points]
        if len(points) >= 2:
            self.pen.line(points, fill=color, width=max(1, round(width * 2)), joint='curve')

    def circle(self, center, radius, color=COBALT, fill=None, width=2):
        x, y = self.point(center)
        r = radius * self.factor
        self.pen.ellipse((x-r, y-r, x+r, y+r), outline=color, fill=fill,
                         width=max(1, round(width * 2)))

    def arrow(self, start, end, color=TEAL):
        start, end = np.asarray(start), np.asarray(end)
        delta = end - start
        length = np.linalg.norm(delta)
        if length > 1e-10:
            along = delta / length
            across = np.array([-along[1], along[0]])
            head = min(0.18, length / 3)
            self.line([start, end], color, 3)
            self.pen.polygon([self.point(p) for p in
                              (end, end-head*along+head/2*across,
                               end-head*along-head/2*across)], fill=color)

    def snapshot(self):
        return self.image.resize((self.pixels,) * 2, Image.Resampling.LANCZOS)


def save_movie(case, view, seconds, folder, name, fps=25):
    """Export the same drawing as a looping GIF, using Pillow's own encoder."""
    duration = case.values['duration']
    if not 0 < seconds <= duration:
        raise ValueError('Choose movie seconds within the positive solved duration.')
    destination = Path(folder)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / (name + '.gif')
    frames = [view.still(case, t) for t in np.arange(0, seconds, 1 / fps)]
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=round(1000 / fps), loop=0, disposal=2)
    return str(path)
