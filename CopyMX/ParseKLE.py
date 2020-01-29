import json
import math


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def rotate_key(key):
    return rotate((key['rotation_x'], key['rotation_y']), (key['x'], key['y']), math.radians(key['rotation_angle']))


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


def get_parsed():
    with open('./layout.txt', 'r') as fp:
        return [rotate_key(key) for key in deserialize(json.load(fp))]


print(get_parsed())
