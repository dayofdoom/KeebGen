import json
import matplotlib.pyplot as plt
import pathlib
import math


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def deserialize(rows):
    # Initialize with defaults
    current = dotdict(dict(
        x=0, y=0, x2=0, y2=0,                         # position
        width=1, height=1, width2=1, height2=1,       # size
        rotation_angle=0, rotation_x=0, rotation_y=0,  # rotation
    ))
    keys = []
    cluster = dotdict(dict(x=0, y=0))
    for (r, row) in enumerate(rows):
        if isinstance(row, list):
            for k, key in enumerate(row):
                if isinstance(key, str):
                    newKey = dotdict(current.copy())
                    newKey.width2 = current.width if newKey.width2 == 0 else current.width2
                    newKey.height2 = current.height if newKey.height2 == 0 else current.height2
                    # Add the key!
                    keys.append(newKey)

                    # Set up for the next key
                    current.x += current.width
                    current.width = current.height = 1
                    current.x2 = current.y2 = current.width2 = current.height2 = 0

                else:
                    key = dotdict(key)
                    if key.r:
                        current.rotation_angle = key.r
                    if key.rx:
                        current.rotation_x = cluster.x = key.rx
                        current.update(cluster)
                    if key.ry:
                        current.rotation_y = cluster.y = key.ry
                        current.update(cluster)
                    if key.x:
                        current.x += key.x
                    if key.y:
                        current.y += key.y
                    if key.w:
                        current.width = current.width2 = key.w
                    if key.h:
                        current.height = current.height2 = key.h
                    if key.x2:
                        current.x2 = key.x2
                    if key.y2:
                        current.y2 = key.y2
                    if key.w2:
                        current.width2 = key.w2
                    if key.h2:
                        current.height2 = key.h2
            # End of the row
            current.y += 1
        current.x = current.rotation_x
    return keys


def offset_key(key):
    new_key = key.copy()
    new_key['x'] = new_key['x'] + new_key['width'] / 2
    new_key['y'] = new_key['y'] + new_key['height'] / 2
    return new_key


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    # angle = angle if angle == 0 else 180-angle
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def rotate_key(key):
    dx, dy = rotate((key['rotation_x'], key['rotation_y']),
                    (key['x'], key['y']), math.radians(key['rotation_angle']))
    new_key = key.copy()
    new_key['x'] = dx
    new_key['y'] = dy
    new_key['rotation_angle'] = key['rotation_angle']
    return new_key


with open(pathlib.Path(__file__).parent / './keyboard-layout.json', 'r') as fp:
    keys = deserialize(json.load(fp))

keys = [offset_key(key) for key in keys]
keys = [rotate_key(key) for key in keys]
xs = [key['x'] for key in keys]
ys = [-key['y'] for key in keys]
ngs = [-key['rotation_angle'] + 90 for key in keys]
plt.axis('equal')
plt.quiver(xs, ys, [1 for x in xs], [1 for y in ys], angles=ngs)
plt.show()
