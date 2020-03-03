import adsk.core
import adsk.fusion
from .. import Config
from .. import Geometry


def switch_cutouts(keys):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    sketches = rootComp.sketches
    sketchCutout = sketches.add(rootComp.xYConstructionPlane)
    sketchLinesCutout = sketchCutout.sketchCurves.sketchLines
    for key in keys:
        x = key['x']
        y = key['y']
        ng = key['rotation_angle']
        centerPointCutout = adsk.core.Point3D.create(x, y, 0)
        cornerPointCutout = adsk.core.Point3D.create(
            x + Config.SWITCH_DIAMETER/2, y + Config.SWITCH_DIAMETER/2, 0)
        rect = sketchLinesCutout.addCenterPointRectangle(centerPointCutout,
                                                         cornerPointCutout)
        centerPointRotation = adsk.core.Point3D.create(
            key["rotation_x"], key["rotation_y"], 0)
        sketchParts = adsk.core.ObjectCollection.create()
        for c in rect:
            sketchParts.add(c)
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
    sketchCutout.name = "switch-cutouts"
    return sketchCutout


def bezel_cutout(keys):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    # Get the root component of the active design
    rootComp = design.rootComponent
    sketches = rootComp.sketches
    sketchCutout = sketches.add(rootComp.xYConstructionPlane)
    sketchLinesCutout = sketchCutout.sketchCurves.sketchLines
    for key in keys:
        x = key['x']
        y = key['y']
        ng = key['rotation_angle']
        # ui.messageBox('angle degrees:{}\nangle radians{}'.format(
        #     key['rotation_angle'], ng))
        centerPointCutout = adsk.core.Point3D.create(x, y, 0)
        cornerPointCutout = adsk.core.Point3D.create(
            x + key['width']/2 + Config.BEZEL_KEY_BUFFER,
            y + key['height']/2 + Config.BEZEL_KEY_BUFFER,
            0
        )
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
    sketchCutout.name = "bezel-cutout"
    return sketchCutout


def bezel_hull(bezel_sketch):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    sketches = rootComp.sketches
    sketch = sketches.add(rootComp.xYConstructionPlane)

    # Start indexing at 1 because the first point is just the origin
    bezel_points = [bezel_sketch.sketchPoints.item(i).geometry
                    for i in range(1, bezel_sketch.sketchPoints.count)]
    points = Geometry.convex_hull(bezel_points)

    point3ds = [adsk.core.Point3D.create(p.x, p.y, p.z) for p in points]
    sketch_points = [sketch.sketchPoints.add(p) for p in point3ds]
    for i in range(len(sketch_points) - 1):
        sketch.sketchCurves.sketchLines.addByTwoPoints(
            sketch_points[i], sketch_points[i+1])
    sketch.sketchCurves.sketchLines.addByTwoPoints(
        sketch_points[-1], sketch_points[0])
    return sketch


def offset_sketch(closed_sketch, offset_amount):
    innerCurves = adsk.core.ObjectCollection.create()
    curves = closed_sketch.sketchCurves
    for i in range(curves.count):
        innerCurves.add(curves.item(i))
    # assume a point in the negative xy quadrant is outside
    outside_point = adsk.core.Point3D.create(-10, -10, 0)
    offsetCurves = closed_sketch.offset(
        innerCurves, outside_point, offset_amount)
    # outerCurves = adsk.core.ObjectCollection.create()
    # for i in range(offsetCurves.count):
    #     outerCurves.add(offsetCurves.item(i))

    # copy the offset curves over to a new sketch
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    sketches = rootComp.sketches
    outerSketch = sketches.add(rootComp.xYConstructionPlane)
    closed_sketch.copy(offsetCurves, adsk.core.Matrix3D.create(), outerSketch)
    outerSketch.name = closed_sketch.name + \
        "-offset-" + str(offset_amount / 10) + "mm"
    for i in range(offsetCurves.count):
        offsetCurves.item(i).deleteMe()
    return outerSketch
