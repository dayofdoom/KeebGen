import adsk.core
import adsk.fusion
import traceback
import math
import json


def cut_switch_cutout(plate_body, x, y, radians):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    # Get the root component of the active design
    rootComp = design.rootComponent
    extrudes = rootComp.features.extrudeFeatures
    sketches = rootComp.sketches
    # Create another sketch

    sketchCutout = sketches.add(rootComp.xYConstructionPlane)
    sketchLinesCutout = sketchCutout.sketchCurves.sketchLines
    centerPointCutout = adsk.core.Point3D.create(x, y, 0)
    cornerPointCutout = adsk.core.Point3D.create(x + 0.7, y + 0.7, 0)
    sketchLinesCutout.addCenterPointRectangle(centerPointCutout,
                                              cornerPointCutout)
    sketchParts = adsk.core.ObjectCollection.create()
    for c in sketchCutout.sketchCurves:
        sketchParts.add(c)
    for p in sketchCutout.sketchPoints:
        sketchParts.add(p)
    ogTransform = sketchCutout.transform
    rotZ = adsk.core.Matrix3D.create()
    rotZ.setToRotation(
        radians,
        adsk.core.Vector3D.create(
            0, 0, 1
        ),
        centerPointCutout
    )
    ogTransform.transformBy(rotZ)
    sketchCutout.move(sketchParts, ogTransform)
    # Get the profile defined by the vertical circle
    profCutout = sketchCutout.profiles.item(0)
    # Extrude Sample 7: Create a 2-side extrusion, whose 1st side is 100 mm distance extent, and 2nd side is 10 mm distance extent.
    extrudeInput = extrudes.createInput(
        profCutout, adsk.fusion.FeatureOperations.CutFeatureOperation)
    isChained = True
    extent_toentity = adsk.fusion.ToEntityExtentDefinition.create(
        plate_body, isChained)
    extent_toentity.isMinimumSolution = False
    extrudeInput.setOneSideExtent(
        extent_toentity, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    extrudes.add(extrudeInput)


def extrude_plate(bx0, bx1, by0, by1):
    app = adsk.core.Application.get()

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    # Get the root component of the active design
    rootComp = design.rootComponent

    # Get extrude features
    extrudes = rootComp.features.extrudeFeatures

    # Create sketch for main plate area
    sketches = rootComp.sketches
    sketch = sketches.add(rootComp.xYConstructionPlane)
    sketchLines = sketch.sketchCurves.sketchLines
    corner0 = adsk.core.Point3D.create(bx0, by0, 0)
    corner1 = adsk.core.Point3D.create(bx1, by1, 0)
    sketchLines.addTwoPointRectangle(corner0, corner1)

    # Get the profile defined by the recangle
    prof = sketch.profiles.item(0)

    # Extrude Sample 1: A simple way of creating typical extrusions (extrusion that goes from the profile plane the specified distance).
    # Define a distance extent of 3 mm
    distance = adsk.core.ValueInput.createByReal(0.3)
    extrude1 = extrudes.addSimple(
        prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # Get the extrusion body
    plate_body = extrude1.bodies.item(0)
    plate_body.name = "plate_outline"
    return plate_body


def file_select(title, filter):
    ui = adsk.core.Application.get().userInterface
    # Set styles of file dialog.
    fileDlg = ui.createFileDialog()
    fileDlg.isMultiSelectEnabled = False
    fileDlg.title = title
    fileDlg.filter = filter

    # Show file open dialog
    dlgResult = fileDlg.showOpen()
    if dlgResult == adsk.core.DialogResults.DialogOK:
        return fileDlg.filename
    else:
        raise FileNotFoundError


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Create a document.
        doc = app.documents.add(
            adsk.core.DocumentTypes.FusionDesignDocumentType)

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get the root component of the active design
        rootComp = design.rootComponent

        # Get extrude features
        extrudes = rootComp.features.extrudeFeatures

        # Create sketch for main plate area
        sketches = rootComp.sketches
        file_name = file_select(
            'Select a JSON-serialized KLE file', '*.json')
        try:
            with open(file_name, 'r') as fp:
                keys = deserialize(json.load(fp))
        except FileNotFoundError:
            return

        keys = [offset_key(key) for key in keys]
        keys = [rotate_key_position(key) for key in keys]
        bx0 = min(key["x"] for key in keys) * 1.905 - 1
        bx1 = max(key["x"] for key in keys) * 1.905 + 1
        by0 = min(-key["y"] for key in keys) * 1.905 - 1
        by1 = max(-key["y"] for key in keys) * 1.905 + 1
        # ui.messageBox('{}, {}; {}, {}'.format(bx0, by0, bx1, by1))

        plate_body = extrude_plate(bx0, bx1, by0, by1)

        for key in keys:
            x = key['x'] * 1.905
            y = -key['y'] * 1.905
            ng = math.radians(-key['rotation_angle'])
            # xpos += size
            # ui.messageBox('{}, {}; {}, {}\n{}, {}'.format(
            #     bx0, by0, bx1, by1, x, y))
            cut_switch_cutout(plate_body, x, y, ng)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


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


def rotate_key_position(key):
    dx, dy = rotate((key['rotation_x'], key['rotation_y']),
                    (key['x'], key['y']), math.radians(key['rotation_angle']))
    new_key = key.copy()
    new_key['x'] = dx
    new_key['y'] = dy
    new_key['rotation_angle'] = key['rotation_angle']
    return new_key


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
