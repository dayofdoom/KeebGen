import json
import math
import matplotlib.pyplot as plt
import pathlib


def gen_plain_key(prev):
    # given a previous key and just a string for the next one
    # return the next key
    new_key = prev.copy()
    # Calculate some generated values
    new_key['width2'] = prev['width'] if new_key['width2'] == 0 else prev['width2']
    new_key['height2'] = prev['height'] if new_key['height2'] == 0 else prev['height2']
    return new_key

# keeb is a list of lists (rows) of dicts (keys)
# deserialize transforms it into a 1-D list of key objects
# arranged WRT a 2d plane


def deserialize(keeb):
    parsed_keeb = []
    current_key = {'x': 0,
                   'y':  0,
                   'width': 1,
                   'height': 1,
                   'x2': 0,
                   'y2': 0,
                   'width2':  1,
                   'height2':  1,
                   'rotation_x':  0,
                   'rotation_y': 0,
                   'rotation_angle':  0}
    for (r, row) in enumerate(keeb):
        if isinstance(row, list):
            for (i, item) in enumerate(row):
                if isinstance(item, str):
                    next_key = gen_plain_key(current_key)
                    parsed_keeb.append(next_key)
                    current_key['x'] += current_key['width']
                    current_key['width'] = current_key['height'] = 1
                    current_key['x2'] = current_key['y2'] = current_key['width2'] = current_key['height2'] = 0
                else:
                    if i > 0 and (item.get('r') or item.get('rx') or item.get('ry')):
                        raise ValueError(
                            "rotation can only be specified on the first key in a row", item)
                    if item.get('r'):
                        current_key['rotation_angle'] = item.get('r')
                    if item.get('rx'):
                        current_key['rotation_x'] = item.get('rx')
                    if item.get('ry'):
                        current_key['rotation_y'] = item.get('ry')
                    current_key['x'] += item.get('x', 0)
                    current_key['y'] += item.get('y', 0)
                    if item.get('w'):
                        current_key['width'] = current_key['width2'] = item.get(
                            'w')
                    if item.get('h'):
                        current_key['height'] = current_key['height2'] = item.get(
                            'h')
                    if item.get('x2'):
                        current_key['x2'] = item.get('x2')
                    if item.get('y2'):
                        current_key['y2'] = item.get('y2')
                    if item.get('w2'):
                        current_key['width2'] = item.get('w2')
                    if item.get('h2'):
                        current_key['height2'] = item.get('h2')
            current_key['y'] += 1
            current_key['x'] = current_key['rotation_x']
        else:
            # it's not a list so we don't care, just pass over meta stuff for now
            continue
    return parsed_keeb


# def get_parsed(key_data):
#     return [(*rotate_key(key), key['width']) for key in key_data]


# def offset_by_widths(xs, widths):
#     return [x + w/2 for (x, w) in zip(xs, widths)]

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    angle = angle if angle == 0 else 180-angle
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
    new_key['rotation_angle'] = -key['rotation_angle']
    return new_key


def offset_by_width(key):
    new_key = key.copy()
    new_key['x'] = new_key['x'] + new_key['width'] / 2
    return new_key


with open(pathlib.Path(__file__).parent / './keyboard-layout.json', 'r') as fp:
    key_data = deserialize(json.load(fp))

offset = [offset_by_width(key) for key in key_data]
rotated = [rotate_key(key) for key in offset]
xs = [key['x'] for key in rotated]
ys = [-key['y'] for key in rotated]
ngs = [key['rotation_angle'] + 90 for key in rotated]
# xs, ys, widths = [zip(*[[key['x'], -key['y'], key['width']]
#                         for key in rotated])]
# pairs = [pair for pair in zip(xs_off, ys_inv)]
plt.axis('equal')
plt.quiver(xs, ys, [0.5 for x in xs], [0.5 for y in ys], angles=ngs)
plt.show()


# print([*xs])
# print([*ys])
