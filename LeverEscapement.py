#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

# Command inputs
_description = adsk.core.TextBoxCommandInput.cast(None)
_standard = adsk.core.DropDownCommandInput.cast(None)
_numTeeth = adsk.core.TextBoxCommandInput.cast(None)
_lockingDiam = adsk.core.ValueCommandInput.cast(None)
_holeDiam = adsk.core.ValueCommandInput.cast(None)
_thickness = adsk.core.ValueCommandInput.cast(None)
_majorDiam = adsk.core.TextBoxCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_handlers = []

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        cmdDef = _ui.commandDefinitions.itemById('adskLeverEscapementPythonScript')
        if not cmdDef:
            # Create a command definition.
            cmdDef = _ui.commandDefinitions.addButtonDefinition('adskLeverEscapementPythonScript', 'Lever Escapement', 'Creates an escape wheel and a pallet fork component.', 'resources/LeverEscapement')

        # Connect to the command created event.
        onCommandCreated = EscapementCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command.
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class EscapementCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # when the command is done, terminate the script.
            # this will release all globals which will remove all event handlers.
            adsk.terminate()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class EscapementCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()

            defaultUnits = des.unitsManager.defaultLengthUnits

            # Determine whether to use inches or millimeters as the intial default.
            global _units
            if defaultUnits == 'in' or defaultUnits == 'ft':
                _units = 'in'
            else:
                _units = 'mm'

            # Define the default values and get the previous values from the attributes.
            if _units == 'in':
                standard = 'English'
            else:
                standard = 'Metric'
            standardAttrib = des.attributes.itemByName('LeverEscapement', 'standard')
            if standardAttrib:
                standard = standardAttrib.value

            if standard == 'English':
                _units = 'in'
            else:
                _units = 'mm'

            numTeeth = '15'
            numTeethAttrib = des.attributes.itemByName('LeverEscapement', 'numTeeth')
            if numTeethAttrib:
                numTeeth = numTeethAttrib.value

            lockingDiam = '3' # 3[cm] = 30.0[mm]
            lockingDiamAttrib = des.attributes.itemByName('LeverEscapement', 'lockingDiam')
            if lockingDiamAttrib:
                lockingDiam = lockingDiamAttrib.value

            holeDiam = '0.15' # 0.15[cm] = 1.5[mm]
            holeDiamAttrib = des.attributes.itemByName('LeverEscapement', 'holeDiam')
            if holeDiamAttrib:
                holeDiam = holeDiamAttrib.value

            thickness = '1'
            thicknessAttrib = des.attributes.itemByName('LeverEscapement', 'thickness')
            if thicknessAttrib:
                thickness = thicknessAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            global _description, _standard, _numTeeth, _lockingDiam, _holeDiam, _thickness, _majorDiam, _errMessage

            # Define the command dialog.
            _description = inputs.addTextBoxCommandInput('description', '', '', 2, True)
            _description.isFullWidth = True

            _standard = inputs.addDropDownCommandInput('standard', 'Standard', adsk.core.DropDownStyles.TextListDropDownStyle)
            if standard == "English":
                _standard.listItems.add('English', True)
                _standard.listItems.add('Metric', False)
            else:
                _standard.listItems.add('English', False)
                _standard.listItems.add('Metric', True)

            _numTeeth = inputs.addTextBoxCommandInput('numTeeth', 'Number of Teeth', numTeeth, 1, True)

            _lockingDiam = inputs.addValueInput('lockingDiam', 'locking Diameter', _units, adsk.core.ValueInput.createByReal(float(lockingDiam)))

            _holeDiam = inputs.addValueInput('holeDiam', 'Hole Diameter', _units, adsk.core.ValueInput.createByReal(float(holeDiam)))

            _thickness = inputs.addValueInput('thickness', 'Wheel Thickness', _units, adsk.core.ValueInput.createByReal(float(thickness)))

            _majorDiam = inputs.addTextBoxCommandInput('majorDiam', 'Major Diameter', '', 1, True)

            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

            # Connect to the command related events.
            onExecute = EscapementCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

            onInputChanged = EscapementCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            # onValidateInputs = EscapementCommandValidateInputsHandler()
            # cmd.validateInputs.add(onValidateInputs)
            # _handlers.append(onValidateInputs)
            ## TBA

            onDestroy = EscapementCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class EscapementCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            attribs.add('LeverEscapement', 'standard', _standard.selectedItem.name)
            attribs.add('LeverEscapement', 'numTeeth', _numTeeth.text)
            attribs.add('LeverEscapement', 'lockingDiam', str(_lockingDiam.value))
            attribs.add('LeverEscapement', 'holeDiam', str(_holeDiam.value))
            attribs.add('LeverEscapement', 'thickness', str(_thickness.value))

            numTeeth = int(_numTeeth.text)
            lockingDiam = _lockingDiam.value
            holeDiam = _holeDiam.value
            thickness = _thickness.value

            # create the pallet and escape wheel.
            drawWheelAndPallet(des, numTeeth, lockingDiam, holeDiam, thickness)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the inputChanged event.
class EscapementCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            global _units
            if changedInput.id == 'standard':
                if _standard.selectedItem.name == 'English':
                    _units = 'in'
                elif _standard.selectedItem.name == 'Metric':
                    _units = 'mm'

                # Set each one to it's current value because otherwised if the user
                # has edited it, the value won't update in the dialog because
                # apparently it remembers the units when the value was edited.
                # Setting the value using the API resets this.
                _lockingDiam.value = _lockingDiam.value
                _lockingDiam.unitType = _units
                _holeDiam.value = _holeDiam.value
                _holeDiam.unitType = _units
                _thickness.value = _thickness.value
                _thickness.unitType = _units

            # Update the major diameter value.
            ## TBA

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# # Event handler for the validateInputs event.
# class GearCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
#     def __init__(self):
#         super().__init__()
#     def notify(self, args):
#         try:
#             ## TBA


def drawWheelAndPallet(design, numTeeth, lockingDiam, holeDiam, thickness):
    try:
        # Get occurences in the root component.
        occs = design.rootComponent.occurrences

        # Add new components to the occurences.
        mat = adsk.core.Matrix3D.create()
        wheelOcc  = occs.addNewComponent(mat) # for escape wheel
        palletOcc = occs.addNewComponent(mat) # for pallet

        # Get objects of new compornents.
        wheelComp = adsk.fusion.Component.cast(wheelOcc.component)
        palletComp = adsk.fusion.Component.cast(palletOcc.component)

        wheelComp.name = "escape wheel"
        palletComp.name = "pallet"

        # Create new sketches in each component.
        baseSketch = wheelComp.sketches.add(wheelComp.xYConstructionPlane)
        wheelSketch = wheelComp.sketches.add(wheelComp.xYConstructionPlane)
        palletSketch = palletComp.sketches.add(palletComp.xYConstructionPlane)

        baseSketch.name = "constructions"
        wheelSketch.name = "escape wheel"
        palletSketch.name = "pallet"

        # Define a normal vector for rotation axis.
        normal = baseSketch.xDirection.crossProduct(baseSketch.yDirection)
        normal.transformBy(baseSketch.transform)

        # Define a matrix for rotation.
        transform = adsk.core.Matrix3D.create()

        # Draw a line AO as center line.
        pointA = adsk.core.Point3D.create(0, 0, 0) # pivot of the wheel.
        pointO = adsk.core.Point3D.create(0, (lockingDiam/2.0)/math.cos(math.radians(30.0)), 0) # pivot of the pallet.
        lineAO = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointA, pointO)
        lineAO.isConstruction = True

        # Draw a locking circle.
        lockingCircle = baseSketch.sketchCurves.sketchCircles.addByCenterRadius(pointA, lockingDiam/2)
        lockingCircle.isConstruction = True

        # Draw a line OD.
        transform.setToRotation(math.radians(-60), normal, pointO)
        pointD = adsk.core.Point3D.create(pointA.x, pointA.y, pointA.z)
        pointD.transformBy(transform)
        lineOD = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointO, pointD)
        lineOD.isConstruction = True

        # Draw a line OE.
        transform.setToRotation(math.radians(60), normal, pointO)
        pointE = adsk.core.Point3D.create(pointA.x, pointA.y, pointA.z)
        pointE.transformBy(transform)
        lineOE = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointO, pointE)
        lineOE.isConstruction = True

        # Draw a line AC.
        transform.setToRotation(math.radians(-29), normal, pointA)
        pointC = adsk.core.Point3D.create(pointO.x, pointO.y, pointO.z)
        pointC.transformBy(transform)
        lineAC = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointA, pointC)
        lineAC.isConstruction = True

        # Draw a line AT.
        transform.setToRotation(math.radians(-7), normal, pointA)
        pointT = adsk.core.Point3D.create(pointC.x, pointC.y, pointC.z)
        pointT.transformBy(transform)
        lineAT = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointA, pointT)
        lineAT.isConstruction = True

        # Draw a line AY.
        transform.setToRotation(math.radians(-4), normal, pointA)
        pointY = adsk.core.Point3D.create(pointT.x, pointT.y, pointT.z)
        pointY.transformBy(transform)
        lineAY = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointA, pointY)
        lineAY.isConstruction = True

        # Draw a line OK.
        transform.setToRotation(math.radians(10), normal, pointO)
        pointK = adsk.core.Point3D.create(pointE.x, pointE.y, pointE.z)
        pointK.transformBy(transform)
        lineOK = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointO, pointK)
        lineOK.isConstruction = True

        # Draw an arc HL.
        pointL = lineAC.geometry.intersectWithCurve(lineOE.geometry)[0]
        arcHL = baseSketch.sketchCurves.sketchArcs.addByCenterStartSweep(pointO, pointL, math.radians(30))
        arcHL.isConstruction = True

        # Draw a line FG.
        pointG = lineOK.geometry.intersectWithCurve(arcHL.geometry)[0]
        transform.setToRotation(math.radians(90), normal, pointG)
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(lineOK)
        copiedEntities = baseSketch.copy(inputEntities, transform) # create a temporary line of FG perpendicular to the line OK.
        tempLineFG = next((entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)), None) # get the line from copied entity.

        transform.setToRotation(math.radians(-2), normal, pointO)
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(lineOK)
        copiedEntities = baseSketch.copy(inputEntities, transform) # create a temporary line of OF for getting point F.
        tempLineOF = next((entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)), None) # get the line from copied entity.

        pointF = tempLineOF.geometry.intersectWithCurve(tempLineFG.geometry)[0] # get the point F as intersection of 2 temporary lines.
        tempLineFG.deleteMe()
        tempLineOF.deleteMe()
        lineOF = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointO, pointF)
        lineOF.isConstruction = True
        lineFG = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointF, pointG)
        lineFG.isConstruction = True

        # Draw a line Fa, for incline of the pallet.
        point_a = lineAY.geometry.intersectWithCurve(lockingCircle.geometry)[0]
        lineFa = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointF, point_a)
        lineFa.isConstruction = True

        # Draw a major circle.
        pointJ = lineAT.geometry.intersectWithCurve(lineFa.geometry)[0]
        baseSketch.sketchPoints.add(pointJ)
        majorRadius = math.sqrt((pointJ.x - pointA.x)**2+(pointJ.y - pointA.y)**2+(pointJ.z - pointA.z)**2)
        majorCircle = baseSketch.sketchCurves.sketchCircles.addByCenterRadius(pointA, majorRadius)
        majorCircle.isConstruction = True

        # Draw a line AB.
        transform.setToRotation(math.radians(31), normal, pointA)
        pointB = adsk.core.Point3D.create(0, majorRadius, 0)
        pointB.transformBy(transform)
        lineAB = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointA, pointB)
        lineAB.isConstruction = True

        # Draw a line AM.
        transform.setToRotation(math.radians(-7), normal, pointA)
        pointM = adsk.core.Point3D.create(pointB.x, pointB.y, pointB.z)
        pointM.transformBy(transform)
        lineAM = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointA, pointM)
        lineAM.isConstruction = True

        # Draw a line AN.
        transform.setToRotation(math.radians(4), normal, pointA)
        pointN = adsk.core.Point3D.create(pointB.x, pointB.y, pointB.z)
        pointN.transformBy(transform)
        lineAN = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointA, pointN)
        lineAN.isConstruction = True

        # Draw an arc VP (but point P isn't defined yet).
        pointV = lineOD.geometry.intersectWithCurve(lineAM.geometry)[0]
        arcVP = baseSketch.sketchCurves.sketchArcs.addByCenterStartSweep(pointO, pointV, math.radians(30))
        arcVP.isConstruction = True

        # Define a point P by using the arc VP, and draw a line OP.
        transform.setToRotation(math.radians(10), normal, pointO)
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(lineOD)
        copiedEntities = baseSketch.copy(inputEntities, transform) # create a temporary line of OP for getting point P.
        tempLineOP = next((entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)), None) # get the line from copied entity.

        pointP = tempLineOP.geometry.intersectWithCurve(arcVP.geometry)[0]
        tempLineOP.deleteMe()

        lineOP = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointO, pointP)
        lineOP.isConstruction = True

        # Draw a line RW.
        pointR = lineOD.geometry.intersectWithCurve(lineAB.geometry)[0]
        vectorOD = adsk.core.Vector3D.create(pointD.x - pointO.x, pointD.y - pointO.y, pointD.z - pointO.z)
        vectorPerpendicularOD = adsk.core.Vector3D.create(vectorOD.y, -vectorOD.x, vectorOD.z)
        vectorPerpendicularOD.scaleBy(0.1)

        pointW = adsk.core.Point3D.create(pointR.x + vectorPerpendicularOD.x, pointR.y + vectorPerpendicularOD.y, pointR.z + vectorPerpendicularOD.z)
        lineRW = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointR, pointW)
        lineRW.isConstruction = True

        # Draw a line OQ.
        transform.setToRotation(math.radians(2), normal, pointO)
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(lineOD)
        copiedEntities = baseSketch.copy(inputEntities, transform) # create a temporary line of OQ for getting point Q.
        tempLineOQ = next((entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)), None) # get the line from copied entity.

        transform.setToRotation(math.radians(-13.5-90), normal, pointR)
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(lineOD)
        copiedEntities = baseSketch.copy(inputEntities, transform) # create a temporary line of enter pallet for getting point Q.
        tempEnterPalletLockingFace = next((entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)), None) # get the line from copied entity.

        pointQ = tempLineOQ.geometry.intersectWithCurve(tempEnterPalletLockingFace.geometry)[0]
        tempEnterPalletLockingFace.deleteMe()
        tempLineOQ.deleteMe()

        lineOQ = baseSketch.sketchCurves.sketchLines.addByTwoPoints(pointO, pointQ)
        lineOQ.isConstruction = True

        # Draw pallets.
        palletAxisHoleCIrcle = palletSketch.sketchCurves.sketchCircles.addByCenterRadius(pointO, holeDiam/2)

        # Draw the face of enter pallet.
        enterPalletInclineFace = palletSketch.sketchCurves.sketchLines.addByTwoPoints(pointQ, pointP)

        transform.setToRotation(math.radians(-13.5), normal, pointR)
        vectorRW = adsk.core.Vector3D.create(pointW.x - pointR.x, pointW.y - pointR.y, pointW.z - pointR.z)
        vectorEnterPalletLockingFace = adsk.core.Vector3D.create(vectorRW.x, vectorRW.y, vectorRW.z)
        vectorEnterPalletLockingFace.transformBy(transform)
        vectorEnterPalletLockingFace.normalize()
        enterPalletLockingFace = palletSketch.sketchCurves.sketchLines.addByTwoPoints(pointQ, adsk.core.Point3D.create(pointQ.x + vectorEnterPalletLockingFace.x,
                                                                                                                       pointQ.y + vectorEnterPalletLockingFace.y,
                                                                                                                       pointQ.z + vectorEnterPalletLockingFace.z))
        enterPalletAnotherFace = palletSketch.sketchCurves.sketchLines.addByTwoPoints(pointP, adsk.core.Point3D.create(pointP.x + vectorEnterPalletLockingFace.x,
                                                                                                                       pointP.y + vectorEnterPalletLockingFace.y,
                                                                                                                       pointP.z + vectorEnterPalletLockingFace.z))

        # Draw the face of exit pallet.
        exitPalletInclineFace = palletSketch.sketchCurves.sketchLines.addByTwoPoints(pointF, pointJ)

        transform.setToRotation(math.radians(-15), normal, pointF)
        vectorFG = adsk.core.Vector3D.create(pointG.x - pointF.x, pointG.y - pointF.y, pointG.z - pointF.z)
        vectorExitPalletLockingFace = adsk.core.Vector3D.create(vectorFG.x, vectorFG.y, vectorFG.z)
        vectorExitPalletLockingFace.transformBy(transform)
        vectorExitPalletLockingFace.normalize()
        exitPalletLockingFace = palletSketch.sketchCurves.sketchLines.addByTwoPoints(pointF, adsk.core.Point3D.create(pointF.x + vectorExitPalletLockingFace.x,
                                                                                                                    pointF.y + vectorExitPalletLockingFace.y,
                                                                                                                    pointF.z + vectorExitPalletLockingFace.z))
        exitPalletAnotherFace = palletSketch.sketchCurves.sketchLines.addByTwoPoints(pointJ, adsk.core.Point3D.create(pointJ.x + vectorExitPalletLockingFace.x,
                                                                                                                    pointJ.y + vectorExitPalletLockingFace.y,
                                                                                                                    pointJ.z + vectorExitPalletLockingFace.z))
        # Draw the face of wheel teeth.
        wheelAxisHoleCircle  = wheelSketch.sketchCurves.sketchCircles.addByCenterRadius(pointA, holeDiam/2)

        transform.setToRotation(math.radians(-24), normal, pointR)
        pointX = adsk.core.Point3D.create(pointA.x, pointA.y, pointA.z)
        pointX.transformBy(transform)
        wheelTeethInclineFace = wheelSketch.sketchCurves.sketchLines.addByTwoPoints(pointN, pointR)
        tempWheelTeethLockingFace = wheelSketch.sketchCurves.sketchLines.addByTwoPoints(pointR, pointX)
        tempWheelTeethLockingFace.isConstruction = True

        teethRootRadius = majorRadius*2/3
        teethRootCircle = wheelSketch.sketchCurves.sketchCircles.addByCenterRadius(pointA, teethRootRadius)
        teethRootCircle.isConstruction = True

        pointZ = tempWheelTeethLockingFace.geometry.intersectWithCurve(teethRootCircle.geometry)[0]
        wheelTeethLockingFace = wheelSketch.sketchCurves.sketchLines.addByTwoPoints(pointR, pointZ)
        tempWheelTeethLockingFace.deleteMe()

        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(wheelTeethInclineFace)
        inputEntities.add(wheelTeethLockingFace)

        for i in range(1, 16):
            transform.setToRotation(math.radians(360/15), normal, pointA)
            copiedEntities = wheelSketch.copy(inputEntities, transform)
            copiedSketchLine = [entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)]
            controlPoints = [inputEntities.item(0).geometry.startPoint, inputEntities.item(0).geometry.endPoint, copiedSketchLine[1].geometry.endPoint]
            wheelTeethAnotherFace = wheelSketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

            evaluator = wheelTeethAnotherFace.evaluator
            _, wheelTeethAnotherFaceStartPoint, _ = evaluator.getEndPoints()
            wheelSketch.sketchCurves.sketchArcs.addFillet(wheelTeethAnotherFace, wheelTeethAnotherFaceStartPoint, inputEntities.item(0), inputEntities.item(0).geometry.startPoint, 0.005)

            if i == 15:
                copiedSketchLine[0].deleteMe()
                copiedSketchLine[1].deleteMe()
            else:
                inputEntities = adsk.core.ObjectCollection.create()
                inputEntities.add(copiedSketchLine[0])
                inputEntities.add(copiedSketchLine[1])

    except Exception as error:
        _ui.messageBox("Failed : " + str(error))
        return None