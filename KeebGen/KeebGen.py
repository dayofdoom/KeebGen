import adsk.core
import adsk.fusion
import traceback
import math
from .Modules import ui_commands
from .Modules import Geometry
from .Modules import KLE
from .Modules import Switches
from .Modules import Config
from .Modules import Sketches
from .Modules import Layers


def main():
    # Some boilerplate extracting important fusion objects
    app = adsk.core.Application.get()
    doc = app.documents.add(
        adsk.core.DocumentTypes.FusionDesignDocumentType)
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    ui = app.userInterface
    # Get extrude features
    extrudes = rootComp.features.extrudeFeatures
    # Create sketch for main plate area
    sketches = rootComp.sketches

    keys = KLE.get_keys()

    bezel_sketch = Sketches.bezel_cutout(keys)
    bezel_hull_sketch = Sketches.bezel_hull(bezel_sketch)
    Layers.bezel(keys)
    # bezel_body = extrude_larger_body(bezel_hull_sketch)
    bezel_body_0 = extrude_larger_body(
        bezel_hull_sketch, 1,
        adsk.core.ValueInput.createByReal(Config.BEZEL_THICKNESS_0),
        adsk.core.ValueInput.createByReal(Config.PLATE_THICKNESS),
        adsk.fusion.ExtentDirections.PositiveExtentDirection)
    bezel_body_1 = extrude_larger_body(
        bezel_hull_sketch, 0,
        adsk.core.ValueInput.createByReal(Config.BEZEL_THICKNESS_1),
        adsk.core.ValueInput.createByReal(
            Config.PLATE_THICKNESS + Config.BEZEL_THICKNESS_0),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    plate_body = extrude_larger_body(
        bezel_hull_sketch, 0,
        adsk.core.ValueInput.createByReal(Config.PLATE_THICKNESS),
        adsk.core.ValueInput.createByReal(0),
        adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    cut_switch_cutouts(plate_body, keys)
    bezel_cutout = cut_bezel_cutouts(bezel_body_0, bezel_sketch)
    mid_sketch = Sketches.bezel_hull(bezel_sketch)
    mid_cutout = Sketches.bezel_hull(bezel_sketch)
    mid_layer = extrude_larger_body(
        mid_sketch, -0.2,
        adsk.core.ValueInput.createByReal(Config.PLATE_THICKNESS * 2),
        adsk.core.ValueInput.createByReal(0),
        adsk.fusion.ExtentDirections.NegativeExtentDirection
    )
    # Switches.place_switches(keys)


def run(context):
    """This function will be called by fusion as the "main" method."""
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        main()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def cut_switch_cutouts(plate_body, keys):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    ui = adsk.core.Application.get().userInterface

    # Get the root component of the active design
    rootComp = design.rootComponent
    extrudes = rootComp.features.extrudeFeatures

    sketchCutout = Sketches.switch_cutouts(keys)
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


def extrude_larger_body(inner_sketch, extra, thickness, offset, direction):

    innerCurves = adsk.core.ObjectCollection.create()
    curves = inner_sketch.sketchCurves
    for i in range(curves.count):
        innerCurves.add(curves.item(i))
    # assume a point in the negative xy quadrant is outside
    outside_point = adsk.core.Point3D.create(-10, -10, 0)
    if not extra == 0:
        offsetCurves = inner_sketch.offset(
            innerCurves, outside_point, extra)

    profs = inner_sketch.profiles
    profCollection = adsk.core.ObjectCollection.create()
    for i in range(profs.count):
        profCollection.add(profs.item(i))

    app = adsk.core.Application.get()

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    # Get the root component of the active design
    rootComp = design.rootComponent
    # Get extrude features
    extrudes = rootComp.features.extrudeFeatures
    extrudeInput = extrudes.createInput(
        profCollection, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extent_thickness = adsk.fusion.DistanceExtentDefinition.create(thickness)
    extrudeInput.setOneSideExtent(
        extent_thickness, direction)
    start_offset = adsk.fusion.OffsetStartDefinition.create(offset)
    extrudeInput.startExtent = start_offset
    extrude1 = extrudes.add(extrudeInput)
    # Get the extrusion body
    bezel_body = extrude1.bodies.item(0)
    offsetFaces = rootComp.features.offsetFacesFeatures
    bezel_body.name = "bezel_outline"
    return bezel_body
