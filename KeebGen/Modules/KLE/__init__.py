import json
import math
from .. import ui_commands
from .. import Config


def get_keys():
    file_name = ui_commands.file_select(
        'Select a JSON-serialized KLE file', '*.json')
    try:
        with open(file_name, 'r') as fp:
            keys = deserialize(json.load(fp))
    except FileNotFoundError:
        return

    keys = [offset_key(key) for key in keys]
    keys = [scale_key(Config.KEY_UNIT, key) for key in keys]
    return keys


def offset_key(key):
    new_key = key.copy()
    new_key['x'] = new_key['x'] + new_key['width'] / 2
    new_key['y'] = new_key['y'] + new_key['height'] / 2
    return new_key


def scale_key(scale, key):
    key = key.copy()
    key["x"] = scale * key["x"]
    key["y"] = -scale * key["y"]
    key["width"] = scale * key["width"]
    key["height"] = scale * key["height"]
    key['rotation_x'] = scale * key["rotation_x"]
    key['rotation_y'] = -scale * key["rotation_y"]
    key['rotation_angle'] = math.radians(-key["rotation_angle"])
    return key


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def deserialize(rows):
    # Initialize with defaults
    current = dotdict(dict(
        x=0, y=0, width=1, height=1,                   # position, size
        rotation_angle=0, rotation_x=0, rotation_y=0,  # rotation
    ))
    keys = []
    cluster = dotdict(dict(x=0, y=0))
    for r, row in enumerate(rows):
        if isinstance(row, list):
            for i, item in enumerate(row):
                if isinstance(item, str):
                    # Copy-construct the accumulated key
                    keys.append(dotdict(current.copy()))
                    # Set up for the next item
                    reset_current(current)
                else:
                    update_current_by_meta(
                        current, dotdict(item), cluster)
            # End of the row
            current.y += 1
        current.x = current.rotation_x
    return keys


def reset_current(current):
    current.x += current.width
    current.width = current.height = 1


def update_current_by_meta(current, meta, cluster):
    # Update rotation info
    if meta.r:
        current.rotation_angle = meta.r
    if meta.rx:
        current.rotation_x = cluster.x = meta.rx
        current.update(cluster)
    if meta.ry:
        current.rotation_y = cluster.y = meta.ry
        current.update(cluster)
    # Increment next position values
    current.x += meta.get('x', 0)
    current.y += meta.get('y', 0)
    # Store next dimensions
    if meta.w:
        current.width = meta.w
    if meta.h:
        current.height = meta.h
