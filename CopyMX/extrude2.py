import adsk.core
import adsk.fusion
import traceback


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

        # Create sketch
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xZConstructionPlane)
        sketchCircles = sketch.sketchCurves.sketchCircles
        centerPoint = adsk.core.Point3D.create(0, 0, 0)
        circle = sketchCircles.addByCenterRadius(centerPoint, 5.0)

        # Get the profile defined by the circle
        prof = sketch.profiles.item(0)

        # Create another sketch
        sketchVertical = sketches.add(rootComp.yZConstructionPlane)
        sketchCirclesVertical = sketchVertical.sketchCurves.sketchCircles
        centerPointVertical = adsk.core.Point3D.create(0, 1, 0)
        cicleVertical = sketchCirclesVertical.addByCenterRadius(
            centerPointVertical, 0.5)

        # Get the profile defined by the vertical circle
        profVertical = sketchVertical.profiles.item(0)

        # Extrude Sample 1: A simple way of creating typical extrusions (extrusion that goes from the profile plane the specified distance).
        # Define a distance extent of 5 cm
        distance = adsk.core.ValueInput.createByReal(5)
        extrude1 = extrudes.addSimple(
            prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # Get the extrusion body
        body1 = extrude1.bodies.item(0)
        body1.name = "simple"

        # Get the state of the extrusion
        health = extrude1.healthState
        if health == adsk.fusion.FeatureHealthStates.WarningFeatureHealthState or health == adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState:
            message = extrude1.errorOrWarningMessage

        # Get the state of timeline object
        timeline = design.timeline
        timelineObj = timeline.item(timeline.count - 1)
        health = timelineObj.healthState
        message = timelineObj.errorOrWarningMessage

        # Create another sketch
        sketch = sketches.add(rootComp.xZConstructionPlane)
        sketchCircles = sketch.sketchCurves.sketchCircles
        centerPoint = adsk.core.Point3D.create(0, 0, 0)
        circle1 = sketchCircles.addByCenterRadius(centerPoint, 13.0)
        circle2 = sketchCircles.addByCenterRadius(centerPoint, 15.0)
        outerProfile = sketch.profiles.item(1)

        # Create taperAngle value inputs
        deg0 = adsk.core.ValueInput.createByString("0 deg")
        deg2 = adsk.core.ValueInput.createByString("2 deg")
        deg5 = adsk.core.ValueInput.createByString("5 deg")

        # Create distance value inputs
        mm10 = adsk.core.ValueInput.createByString("10 mm")
        mm100 = adsk.core.ValueInput.createByString("100 mm")

        # Extrude Sample 2: Create an extrusion that goes from the profile plane with one side distance extent
        extrudeInput = extrudes.createInput(
            outerProfile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # Create a distance extent definition
        extent_distance = adsk.fusion.DistanceExtentDefinition.create(mm100)
        extrudeInput.setOneSideExtent(
            extent_distance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
        # Create the extrusion
        extrude2 = extrudes.add(extrudeInput)
        # Get the body of the extrusion
        body2 = extrude2.bodies.item(0)
        body2.name = "distance, from profile"
        # Create taperAngle value inputs
        deg0 = adsk.core.ValueInput.createByString("0 deg")
        deg2 = adsk.core.ValueInput.createByString("2 deg")
        deg5 = adsk.core.ValueInput.createByString("5 deg")

        # Extrude Sample 7: Create a 2-side extrusion, whose 1st side is 100 mm distance extent, and 2nd side is 10 mm distance extent.
        extrudeInput = extrudes.createInput(
            profVertical, adsk.fusion.FeatureOperations.CutFeatureOperation)
        isChained = True
        extent_toentity = adsk.fusion.ToEntityExtentDefinition.create(
            body2, isChained)
        extent_toentity.isMinimumSolution = False
        extent_distance_2 = adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByString("1cm"))
        extrudeInput.setOneSideExtent(
            extent_toentity, adsk.fusion.ExtentDirections.PositiveExtentDirection)
        extrude7 = extrudes.add(extrudeInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
