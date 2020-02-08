# Author-Autodesk Inc.
# Description-Simple script display a message.

import adsk.core  # pylint: disable=import-error
import traceback
import json
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
                    update_current_by_meta(current, dotdict(item), cluster)
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


def add_switch(rootComp, occ, xPos, yPos, ng):
    # transform = adsk.core.Matrix3D.create()
    ogTransform = occ.transform
    rotY = adsk.core.Matrix3D.create()
    rotY.setToRotation(
        math.radians(ng),
        adsk.core.Vector3D.create(
            0, 0, 1
        ),
        adsk.core.Point3D.create(0, 0, 0)
    )
    ogTransform.transformBy(rotY)
    ogTransform.translation = adsk.core.Vector3D.create(ogTransform.translation.x + (
        1.905 * xPos), ogTransform.translation.y + (1.905 * yPos), ogTransform.translation.z)
    # [success, origin, axis] = occ.component.zConstructionAxis.geometry.getData()
    # ui.messageBox(str(x))
    # ogTransform.translation = ogTransform.translation.setToRotation(
    #    math.radians(ng), axis, origin)

    newOcc = rootComp.occurrences.addExistingComponent(
        occ.component, ogTransform)
    newOcc.transform = ogTransform
    # newOcc.transformBy()
    # newTrans = newOcc.transform
    # newTrans.translation = rotY
    # newOcc2 = rootComp.occurrences.addExistingComponent(
    #     newOcc.component, newTrans)
    # newOcc2.transform = newTrans


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        design = app.activeProduct
        rootComp = design.rootComponent
        comp = design.activeComponent
        features = rootComp.features

        switch_collection = adsk.core.ObjectCollection.create()
        mx_switch_occ = import_switch_model(app).item(0)
        swocc_transf = mx_switch_occ.transform
        switch_collection.add(mx_switch_occ.bRepBodies)
        ui.messageBox('collection:\n{}'.format(switch_collection.objectType))
        return
        min_bb = mx_switch_occ.boundingBox.minPoint
        max_bb = mx_switch_occ.boundingBox.maxPoint
        mid_point = adsk.core.Point3D.create(
            (min_bb.x + max_bb.x) / 2,
            (min_bb.x + max_bb.x) / 2,
            (min_bb.x + max_bb.x) / 2
        )
        rot_axis = adsk.core.InfiniteLine3D.create(
            mid_point,
            adsk.core.Vector3D.create(0, 0, 1)
        )
# try it this way: http://help.autodesk.com/view/fusion360/ENU/?caas=caas/discussion/t5/Fusion-360-API-and-Scripts/Is-it-possible-to-Rotate-a-body-by-multiple-angles-as-you-can-do-in-the-Move-UI/td-p/6234792.html

        switch_collection = adsk.core.ObjectCollection.create()
        mx_switch_occ = import_switch_model(app).item(0)
        swocc_transf = mx_switch_occ.transform
        switch_collection.add(mx_switch_occ.bRepBodies)
        trans = adsk.core.Matrix3D.create()

        rotY = adsk.core.Matrix3D.create()
        rotY.setToRotation(
            math.pi,
            adsk.core.Vector3D.create(
                0, 1, 0
            ),
            adsk.core.Point3D.create(0, 0, 0)
        )
        trans.transformBy(rotY)
        rotX = adsk.core.Matrix3D.create()
        rotX.setToRotation(
            math.pi/2,
            adsk.core.Vector3D.create(
                1, 0, 0
            ),
            adsk.core.Point3D.create(0, 0, 0)
        )
        trans.transformBy(rotX)

        # ui.messageBox('about to apply')

        swocc_transf.transform = trans
        fixed_rot_occ = rootComp.occurrences.addExistingComponent(
            mx_switch_occ.component, swocc_transf.transform)

        # rotY = adsk.core.Matrix3D.create()
        # rotY.setToRotation(math.pi/2, adsk.core.Vector3D.create(0,
        #                                                         1, 0), adsk.core.Point3D.create(0, 0, 0))
        # trans.transformBy(rotY)

        # moveInput = rootComp.features.moveFeatures.createInput(
        #     switch_collection, trans)
        # ui.messageBox('collection:\n{}'.format(switch_collection.objectType))
        # ui.messageBox('transform:\n{}'.format(trans.objectType))
        # ui.messageBox('move input:\n{}'.format(moveInput.objectType))
        # rootComp.features.moveFeatures.add(moveInput)

        # ui.messageBox('count:\n{}'.format(occ.objectType))
        try:
            with open(prompt_KLE_file_select(ui), 'r') as fp:
                keys = deserialize(json.load(fp))
        except FileNotFoundError:
            return

        keys = [offset_key(key) for key in keys]
        keys = [rotate_key(key) for key in keys]
        # xs = [key['x'] for key in keys]
        # ys = [-key['y'] for key in keys]
        # ngs = [-key['rotation_angle'] + 90 for key in keys]

        for key in keys:
            x = key['x']
            y = -key['y']
            ng = -key['rotation_angle']
            # xpos += size
            add_switch(rootComp, fixed_rot_occ, x, y, ng)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def prompt_file_select(ui, title, filter):
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


def prompt_KLE_file_select(ui):
    prompt_file_select(ui, 'Select a JSON-serialized KLE file', '*.json')


def prompt_switch_file_select(ui):
    prompt_file_select(ui, 'Select a switch STEP file', '*.STEP')


def import_switch_model(app):
    ui = app.userInterface
    design = app.activeProduct
    rootComp = design.rootComponent
    try:

        # Import a selected STEP file into the root component
        stepImportOptions = app.importManager.createSTEPImportOptions(
            prompt_switch_file_select(ui)
        )
        # this version of the method returns the imported model ref
        return app.importManager.importToTarget2(stepImportOptions, rootComp)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
