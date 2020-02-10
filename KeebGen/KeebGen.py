import adsk.core
import adsk.fusion
import traceback
import math
import json
from .Modules import ui_commands
from .Modules import geometry
from .Modules import KLE

# Standard MX switch is 1.905 cm from center to center
KEY_UNIT = 1.905
# and 1.4 cm plate cutout
SWITCH_DIAMETER = 1.4
# plate config
PLATE_THICKNESS = 0.3
# bezel config
BEZEL_THICKNESS_0 = 0.3
BEZEL_THICKNESS_1 = 0.3
# Distance from key 1.905 box to inner edge of bezel
BEZEL_KEY_BUFFER = 0.0475


def cut_switch_cutouts(plate_body, keys):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    ui = adsk.core.Application.get().userInterface

    # Get the root component of the active design
    rootComp = design.rootComponent
    extrudes = rootComp.features.extrudeFeatures
    sketches = rootComp.sketches
    sketchCutout = sketches.add(rootComp.xYConstructionPlane)
    sketchLinesCutout = sketchCutout.sketchCurves.sketchLines
    for key in keys:
        x = key['x']
        y = key['y']
        ng = math.radians(key['rotation_angle'])
        # ui.messageBox('angle degrees:{}\nangle radians{}'.format(
        #     key['rotation_angle'], ng))
        centerPointCutout = adsk.core.Point3D.create(x, y, 0)
        cornerPointCutout = adsk.core.Point3D.create(
            x + SWITCH_DIAMETER/2, y + SWITCH_DIAMETER/2, 0)
        rect = sketchLinesCutout.addCenterPointRectangle(centerPointCutout,
                                                         cornerPointCutout)
        centerPointRotation = adsk.core.Point3D.create(
            key["rotation_x"], key["rotation_y"], 0)
        sketchParts = adsk.core.ObjectCollection.create()
        for c in rect:
            sketchParts.add(c)
        # for p in sketchCutout.sketchPoints:
        #     sketchParts.add(p)
        ogTransform = sketchCutout.transform.copy()
        rotZ = adsk.core.Matrix3D.create()
        rotZ.setToRotation(
            ng,
            adsk.core.Vector3D.create(
                0, 0, 1
            ),
            centerPointRotation
        )
        ogTransform.transformBy(rotZ)
        sketchCutout.move(sketchParts, ogTransform)
    profCutout = sketchCutout.profiles
    profCollection = adsk.core.ObjectCollection.create()
    for i in range(profCutout.count):
        profCollection.add(profCutout.item(i))
    # Extrude Sample 7: Create a 2-side extrusion, whose 1st side is 100 mm distance extent, and 2nd side is 10 mm distance extent.
    extrudeInput = extrudes.createInput(
        profCollection, adsk.fusion.FeatureOperations.CutFeatureOperation)
    isChained = True
    extent_toentity = adsk.fusion.ToEntityExtentDefinition.create(
        plate_body, isChained)
    extent_toentity.isMinimumSolution = False
    extrudeInput.setOneSideExtent(
        extent_toentity, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    extrudes.add(extrudeInput)


def cut_bezel_cutouts(bezel_body, sketchCutout):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    # Get the root component of the active design
    rootComp = design.rootComponent
    extrudes = rootComp.features.extrudeFeatures
    profCutout = sketchCutout.profiles
    profCollection = adsk.core.ObjectCollection.create()
    for i in range(profCutout.count):
        profCollection.add(profCutout.item(i))
    # Extrude Sample 7: Create a 2-side extrusion, whose 1st side is 100 mm distance extent, and 2nd side is 10 mm distance extent.
    extrudeInput = extrudes.createInput(
        profCollection, adsk.fusion.FeatureOperations.CutFeatureOperation)

    isChained = True
    extent_toentity = adsk.fusion.ToEntityExtentDefinition.create(
        bezel_body, isChained)
    extent_toentity.isMinimumSolution = False
    extrudeInput.setOneSideExtent(
        extent_toentity, adsk.fusion.ExtentDirections.NegativeExtentDirection)
    start_offset = adsk.fusion.OffsetStartDefinition.create(
        adsk.core.ValueInput.createByString("9.00mm"))
    extrudeInput.startExtent = start_offset
    return extrudes.add(extrudeInput)


def sketch_bezel_cutout(keys):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    ui = adsk.core.Application.get().userInterface

    # Get the root component of the active design
    rootComp = design.rootComponent
    sketches = rootComp.sketches
    sketchCutout = sketches.add(rootComp.xYConstructionPlane)
    sketchLinesCutout = sketchCutout.sketchCurves.sketchLines
    for key in keys:
        x = key['x']
        y = key['y']
        ng = math.radians(key['rotation_angle'])
        # ui.messageBox('angle degrees:{}\nangle radians{}'.format(
        #     key['rotation_angle'], ng))
        centerPointCutout = adsk.core.Point3D.create(x, y, 0)
        cornerPointCutout = adsk.core.Point3D.create(
            x + key['width']/2 + BEZEL_KEY_BUFFER, y + key['height']/2 + BEZEL_KEY_BUFFER, 0)
        rect = sketchLinesCutout.addCenterPointRectangle(centerPointCutout,
                                                         cornerPointCutout)
        centerPointRotation = adsk.core.Point3D.create(
            key["rotation_x"], key["rotation_y"], 0)
        sketchParts = adsk.core.ObjectCollection.create()
        for c in rect:
            sketchParts.add(c)
        # for p in sketchCutout.sketchPoints:
        #     sketchParts.add(p)
        ogTransform = sketchCutout.transform.copy()
        rotZ = adsk.core.Matrix3D.create()
        rotZ.setToRotation(
            ng,
            adsk.core.Vector3D.create(
                0, 0, 1
            ),
            centerPointRotation
        )
        ogTransform.transformBy(rotZ)
        sketchCutout.move(sketchParts, ogTransform)
    return sketchCutout


def extrude_larger_body(single_profile_sketch, extra, thickness, offset, direction, already_offset=False):
    app = adsk.core.Application.get()

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    # Get the root component of the active design
    rootComp = design.rootComponent

    # Get extrude features
    extrudes = rootComp.features.extrudeFeatures
    innerCurves = adsk.core.ObjectCollection.create()
    single_profile_sketch.sketchCurves
    curves = single_profile_sketch.sketchCurves
    for i in range(curves.count):
        innerCurves.add(curves.item(i))
    # assume a point in the negative xy quadrant is outside
    outside_point = adsk.core.Point3D.create(-1, -1, 0)
    if not already_offset:
        offsetCurves = single_profile_sketch.offset(
            innerCurves, outside_point, extra)
    profs = single_profile_sketch.profiles
    profCollection = adsk.core.ObjectCollection.create()
    for i in range(profs.count):
        profCollection.add(profs.item(i))
    extrudeInput = extrudes.createInput(
        profCollection, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    # ui = adsk.core.Application.get().userInterface
    # ui.messageBox('Faces:\n{}'.format(plate_body.faces.count))
    # extent_toentity = adsk.fusion.ToEntityExtentDefinition.create(
    #     plate_body.faces.item(5), isChained)
    # extent_toentity.isMinimumSolution = True

    # Extrude Sample 1: A simple way of creating typical extrusions (extrusion that goes from the profile plane the specified distance).
    # Define a distance extent of 6 mm
    extent_thickness = adsk.fusion.DistanceExtentDefinition.create(thickness)
    extrudeInput.setOneSideExtent(
        extent_thickness, direction)
    start_offset = adsk.fusion.OffsetStartDefinition.create(offset
                                                            )
    extrudeInput.startExtent = start_offset
    extrude1 = extrudes.add(extrudeInput)
    # Get the extrusion body
    bezel_body = extrude1.bodies.item(0)
    offsetFaces = rootComp.features.offsetFacesFeatures
    bezel_body.name = "bezel_outline"
    return bezel_body


def sketch_bezel_hull(points):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    sketches = rootComp.sketches
    sketch = sketches.add(rootComp.xYConstructionPlane)
    point3ds = [adsk.core.Point3D.create(p.x, p.y, p.z) for p in points]
    sketch_points = [sketch.sketchPoints.add(p) for p in point3ds]
    for i in range(len(sketch_points) - 1):
        sketch.sketchCurves.sketchLines.addByTwoPoints(
            sketch_points[i], sketch_points[i+1])
    sketch.sketchCurves.sketchLines.addByTwoPoints(
        sketch_points[-1], sketch_points[0])
    return sketch


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
        file_name = ui_commands.file_select(
            'Select a JSON-serialized KLE file', '*.json')
        try:
            with open(file_name, 'r') as fp:
                keys = KLE.deserialize(json.load(fp))
        except FileNotFoundError:
            return

        keys = [KLE.offset_key(key) for key in keys]
        keys = [KLE.scale_key(KEY_UNIT, key) for key in keys]
        bezel_sketch = sketch_bezel_cutout(keys)
        # Start indexing at 1 because the first point is just the origin
        bezel_points = [bezel_sketch.sketchPoints.item(i).geometry
                        for i in range(1, bezel_sketch.sketchPoints.count)]
        bezel_hull_points = geometry.convex_hull(bezel_points)
        bezel_hull_sketch = sketch_bezel_hull(bezel_hull_points)
        # bezel_body = extrude_larger_body(bezel_hull_sketch)
        bezel_body_0 = extrude_larger_body(
            bezel_hull_sketch, 1,
            adsk.core.ValueInput.createByReal(BEZEL_THICKNESS_0),
            adsk.core.ValueInput.createByReal(PLATE_THICKNESS),
            adsk.fusion.ExtentDirections.PositiveExtentDirection)
        bezel_body_1 = extrude_larger_body(
            bezel_hull_sketch, 1,
            adsk.core.ValueInput.createByReal(BEZEL_THICKNESS_1),
            adsk.core.ValueInput.createByReal(
                PLATE_THICKNESS + BEZEL_THICKNESS_0),
            adsk.fusion.ExtentDirections.PositiveExtentDirection,
            already_offset=True)
        plate_body = extrude_larger_body(
            bezel_hull_sketch, 1,
            adsk.core.ValueInput.createByReal(PLATE_THICKNESS),
            adsk.core.ValueInput.createByReal(0),
            adsk.fusion.ExtentDirections.PositiveExtentDirection,
            already_offset=True
        )
        cut_switch_cutouts(plate_body, keys)
        bezel_cutout = cut_bezel_cutouts(bezel_body_0, bezel_sketch)
        orig_switch = import_switch_model().item(0)
        fix_first_switch(orig_switch, keys[0])

        badtrans = adsk.core.Matrix3D.create()
        rotZ = adsk.core.Matrix3D.create()
        rotZ.setToRotation(
            math.radians(keys[0]["rotation_angle"]),
            adsk.core.Vector3D.create(
                0, 0, 1
            ),
            adsk.core.Point3D.create(
                keys[0]["rotation_x"], keys[0]["rotation_y"], 0)
        )
        badtrans.translation = adsk.core.Vector3D.create(
            badtrans.translation.x + keys[0]["x"] + 0.7375,
            badtrans.translation.y + keys[0]["y"] + 0.7375,
            badtrans.translation.z + 0.1 + PLATE_THICKNESS)
        badtrans.transformBy(rotZ)
        for key in keys[1:]:
            add_switch(orig_switch, key, badtrans)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


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
        math.radians(key["rotation_angle"]),
        adsk.core.Vector3D.create(
            0, 0, 1
        ),
        adsk.core.Point3D.create(
            key["rotation_x"], key["rotation_y"], 0)
    )

    trans.translation = adsk.core.Vector3D.create(
        trans.translation.x + key["x"] + 0.7375,
        trans.translation.y + key["y"] + 0.7375,
        trans.translation.z + 0.1 + PLATE_THICKNESS)
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
        math.radians(key["rotation_angle"]),
        adsk.core.Vector3D.create(
            0, 0, 1
        ),
        adsk.core.Point3D.create(
            key["rotation_x"], key["rotation_y"], 0)
    )
    trans.translation = adsk.core.Vector3D.create(
        trans.translation.x + key["x"] + 0.7375,
        trans.translation.y + key["y"] + 0.7375,
        trans.translation.z + 0.1 + PLATE_THICKNESS)
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


def prompt_KLE_file_select():
    return ui_commands.file_select('Select a JSON-serialized KLE file', '*.json')


def prompt_switch_file_select():
    return ui_commands.file_select('Select a switch STEP file', '*.STEP')
