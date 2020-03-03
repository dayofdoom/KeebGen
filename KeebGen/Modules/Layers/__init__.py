import adsk.core
import adsk.fusion
from .. import Config
from .. import Sketches


def full_case(keys):
    elevation = 0
    layer_attrs = {'bottom': {}, 'mid_1': {}, 'mid_0': {},
                   'plate': {}, 'bezel_1': {}, 'bezel_0': {}}
    layer_attrs['bottom']['elevation'] = elevation
    layer_attrs['bottom']['thickness'] = Config.BOTTOM_THICKNESS
    elevation += Config.BOTTOM_THICKNESS
    layer_attrs['mid_1']['elevation'] = elevation
    layer_attrs['mid_1']['thickness'] = Config.MID_THICKNESS_1
    elevation += Config.MID_THICKNESS_1
    layer_attrs['mid_0']['elevation'] = elevation
    layer_attrs['mid_0']['thickness'] = Config.MID_THICKNESS_0
    elevation += Config.MID_THICKNESS_0
    layer_attrs['plate']['elevation'] = elevation
    layer_attrs['plate']['thickness'] = Config.PLATE_THICKNESS
    elevation += Config.PLATE_THICKNESS
    layer_attrs['bezel_1']['elevation'] = elevation
    layer_attrs['bezel_1']['thickness'] = Config.BEZEL_THICKNESS_1
    elevation += Config.BEZEL_THICKNESS_1
    layer_attrs['bezel_0']['elevation'] = elevation
    layer_attrs['bezel_0']['thickness'] = Config.BEZEL_THICKNESS_0
    elevation += Config.BEZEL_THICKNESS_0

    # the first time we compute the bezel, remember the outline for
    # the other layers
    bezel_body_0, outline = bezel(keys, layer_attrs['bezel_0']['elevation'],
                                  layer_attrs['bezel_0']['thickness'])
    bezel_body_0.name = "BEZEL_0"
    bezel_body_1, _ = bezel(keys, layer_attrs['bezel_1']['elevation'],
                            layer_attrs['bezel_1']['thickness'])
    bezel_body_1.name = "BEZEL_1"

    plate_body = plate(outline, keys, layer_attrs['plate']['elevation'],
                       layer_attrs['plate']['thickness'])
    plate_body.name = "PLATE"

    mid_body_0 = mid(outline, keys, layer_attrs['mid_0']['elevation'],
                     layer_attrs['mid_0']['thickness'])
    mid_body_0.name = "MID_0"
    mid_body_1 = mid(outline, keys, layer_attrs['mid_1']['elevation'],
                     layer_attrs['mid_1']['thickness'])
    mid_body_1.name = "MID_1"

    bottom_body = bottom(outline, layer_attrs['bottom']['elevation'],
                         layer_attrs['bottom']['thickness'])
    bottom_body.name = "BOTTOM"


def extrude_with_cutout(body_sketch, cutout_sketch, elevation, thickness):
    # Setup
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    extrudes = rootComp.features.extrudeFeatures

    # Extrude the main body
    body_profiles = body_sketch.profiles
    bodyProfCollection = adsk.core.ObjectCollection.create()
    for i in range(body_profiles.count):
        bodyProfCollection.add(body_profiles.item(i))
    bodyExtrudeInput = extrudes.createInput(
        bodyProfCollection, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extent_thickness = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(thickness))
    bodyExtrudeInput.setOneSideExtent(
        extent_thickness, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    elevation_extent = adsk.fusion.OffsetStartDefinition.create(
        adsk.core.ValueInput.createByReal(elevation))
    bodyExtrudeInput.startExtent = elevation_extent
    body_extrusion = extrudes.add(bodyExtrudeInput)
    extruded_body = body_extrusion.bodies.item(0)

    # Extrude cutout from the main body
    cutout_profiles = cutout_sketch.profiles
    cutoutProfCollection = adsk.core.ObjectCollection.create()
    for i in range(cutout_profiles.count):
        cutoutProfCollection.add(cutout_profiles.item(i))
    cutoutExtrudeInput = extrudes.createInput(
        cutoutProfCollection, adsk.fusion.FeatureOperations.CutFeatureOperation)
    isChained = True
    extent_to_body = adsk.fusion.ToEntityExtentDefinition.create(
        extruded_body, isChained)
    extent_to_body.isMinimumSolution = False
    cutoutExtrudeInput.setOneSideExtent(
        extent_to_body, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    cutoutExtrudeInput.startExtent = elevation_extent
    extrudes.add(cutoutExtrudeInput)

    # Return the body created by the extrusion
    return extruded_body


def extrude_basic(body_sketch, elevation, thickness):
    # Setup
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    extrudes = rootComp.features.extrudeFeatures

    # Extrude the main body
    body_profiles = body_sketch.profiles
    bodyProfCollection = adsk.core.ObjectCollection.create()
    for i in range(body_profiles.count):
        bodyProfCollection.add(body_profiles.item(i))
    bodyExtrudeInput = extrudes.createInput(
        bodyProfCollection, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extent_thickness = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(thickness))
    bodyExtrudeInput.setOneSideExtent(
        extent_thickness, adsk.fusion.ExtentDirections.PositiveExtentDirection)
    elevation_extent = adsk.fusion.OffsetStartDefinition.create(
        adsk.core.ValueInput.createByReal(elevation))
    bodyExtrudeInput.startExtent = elevation_extent
    body_extrusion = extrudes.add(bodyExtrudeInput)
    extruded_body = body_extrusion.bodies.item(0)

    # Return the body created by the extrusion
    return extruded_body


def bezel(keys, elevation, thickness):
    # Make the relevant sketches
    bezel_sketch = Sketches.bezel_cutout(keys)
    bezel_sketch.name = "bezel"
    bezel_hull_sketch = Sketches.bezel_hull(bezel_sketch)
    bezel_hull_sketch.name = "bezel-hull"
    offset_sketch = Sketches.offset_sketch(bezel_hull_sketch, 1)
    offset_sketch.name = "bezel-hull-plus-10mm"

    # Extrude and return
    bezel_body = extrude_with_cutout(offset_sketch,
                                     bezel_sketch, elevation, thickness)
    return bezel_body, offset_sketch


def mid(outline_sketch, keys, elevation, thickness):
    # Make the relevant sketches
    bezel_sketch = Sketches.bezel_cutout(keys)
    bezel_sketch.name = "temp-bezel(mid)"
    bezel_hull_sketch = Sketches.bezel_hull(bezel_sketch)
    bezel_hull_sketch.name = "temp-bezel-hull(mid)"

    # Extrude and return
    mid_body = extrude_with_cutout(outline_sketch,
                                   bezel_hull_sketch, elevation, thickness)
    return mid_body


def plate(outline_sketch, keys, elevation, thickness):
    switch_cutout = Sketches.switch_cutouts(keys)
    # Extrude and return
    plate_body = extrude_with_cutout(outline_sketch,
                                     switch_cutout, elevation, thickness)
    return plate_body


def bottom(outline_sketch, elevation, thickness):
    # Extrude and return
    mid_body = extrude_basic(outline_sketch, elevation, thickness)
    return mid_body
