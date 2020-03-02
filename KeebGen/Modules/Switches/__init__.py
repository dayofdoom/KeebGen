
import math
import traceback
import adsk.core
import adsk.fusion
from .. import ui_commands
from .. import Config


def place_switches(keys):
    orig_switch = import_switch_model().item(0)
    fix_first_switch(orig_switch, keys[0])

    badtrans = adsk.core.Matrix3D.create()
    rotZ = adsk.core.Matrix3D.create()
    rotZ.setToRotation(
        keys[0]["rotation_angle"],
        adsk.core.Vector3D.create(
            0, 0, 1
        ),
        adsk.core.Point3D.create(
            keys[0]["rotation_x"], keys[0]["rotation_y"], 0)
    )
    badtrans.translation = adsk.core.Vector3D.create(
        badtrans.translation.x + keys[0]["x"] + 0.7375,
        badtrans.translation.y + keys[0]["y"] + 0.7375,
        badtrans.translation.z + 0.1 + Config.PLATE_THICKNESS)
    badtrans.transformBy(rotZ)
    for key in keys[1:]:
        add_switch(orig_switch, key, badtrans)


def fix_first_switch(switch, key):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    switch_collection = adsk.core.ObjectCollection.create()
    for i in range(switch.bRepBodies.count):
        switch_collection.add(switch.bRepBodies.item(i))
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
    rotZ = adsk.core.Matrix3D.create()
    rotZ.setToRotation(
        key["rotation_angle"],
        adsk.core.Vector3D.create(
            0, 0, 1
        ),
        adsk.core.Point3D.create(
            key["rotation_x"], key["rotation_y"], 0)
    )

    trans.translation = adsk.core.Vector3D.create(
        trans.translation.x + key["x"] + 0.7375,
        trans.translation.y + key["y"] + 0.7375,
        trans.translation.z + 0.1 + Config.PLATE_THICKNESS)
    trans.transformBy(rotZ)
    moveInput = rootComp.features.moveFeatures.createInput(
        switch_collection, trans)
    rootComp.features.moveFeatures.add(moveInput)


def add_switch(occ, key, badtrans):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    trans = occ.transform.copy()
    goodtrans = badtrans.copy()
    goodtrans.invert()
    trans.transformBy(goodtrans)
    rotZ = adsk.core.Matrix3D.create()
    rotZ.setToRotation(
        key["rotation_angle"],
        adsk.core.Vector3D.create(
            0, 0, 1
        ),
        adsk.core.Point3D.create(
            key["rotation_x"], key["rotation_y"], 0)
    )
    trans.translation = adsk.core.Vector3D.create(
        trans.translation.x + key["x"] + 0.7375,
        trans.translation.y + key["y"] + 0.7375,
        trans.translation.z + 0.1 + Config.PLATE_THICKNESS)
    trans.transformBy(rotZ)
    newOcc = rootComp.occurrences.addExistingComponent(
        occ.component, trans)
    newOcc.transform = trans
    return


def import_switch_model():
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = app.activeProduct
    rootComp = design.rootComponent
    try:

        # Import a selected STEP file into the root component
        stepImportOptions = app.importManager.createSTEPImportOptions(
            prompt_switch_file_select()
        )
        # this version of the method returns the imported model ref
        return app.importManager.importToTarget2(stepImportOptions, rootComp)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def prompt_switch_file_select():
    return ui_commands.file_select('Select a switch STEP file', '*.STEP')
