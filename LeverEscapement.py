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

class Points:
    pass

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
            # drawWheelAndPallet(des, numTeeth, lockingDiam, holeDiam, thickness)
            wheelAndPallets = WheelAndPallets(des, numTeeth, lockingDiam, holeDiam, thickness)
            wheelAndPallets.drawConstructions()
            wheelAndPallets.drawWheel()
            wheelAndPallets.drawPallets()

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

class WheelAndPallets:
    def __init__(self, design, numTeeth, lockingDiam, holeDiam, thickness):
        self.__design = design
        self.__numTeeth = numTeeth
        self.__lockingDiam = lockingDiam
        self.__holeDiam = holeDiam
        self.__thickness = thickness

        self.__points = Points()

        # Get occurences in the root component.
        self.__occs = self.__design.rootComponent.occurrences

        # Add new components to the occurences.
        self.__wheelOcc = self.__occs.addNewComponent(adsk.core.Matrix3D.create())
        self.__palletOcc = self.__occs.addNewComponent(adsk.core.Matrix3D.create())

        # Get objects of new compornents.
        self.__wheelComp = adsk.fusion.Component.cast(self.__wheelOcc.component)
        self.__palletComp = adsk.fusion.Component.cast(self.__palletOcc.component)

        self.__wheelComp.name = "escape wheel"
        self.__palletComp.name = "pallet"

        # Create new sketches in each component.
        self.__baseSketch = self.__wheelComp.sketches.add(self.__wheelComp.xYConstructionPlane)
        self.__wheelSketch = self.__wheelComp.sketches.add(self.__wheelComp.xYConstructionPlane)
        self.__palletSketch =  self.__palletComp.sketches.add(self.__palletComp.xYConstructionPlane)

        self.__baseSketch.name = "constructions"
        self.__wheelSketch.name = "escape wheel"
        self.__palletSketch.name = "pallet"

        # Define a normal vector for rotation axis.
        self.__normal = self.__baseSketch.xDirection.crossProduct(self.__baseSketch.yDirection)
        self.__normal.transformBy(self.__baseSketch.transform)

    def drawConstructions(self):
        # Define a matrix for rotation.
        transform = adsk.core.Matrix3D.create()

        # Draw a line AO as center line.
        self.__points.A = adsk.core.Point3D.create(0, 0, 0) # pivot of the wheel.
        self.__points.O = adsk.core.Point3D.create(0, (self.__lockingDiam/2.0)/math.cos(math.radians(30.0)), 0) # pivot of the pallet.
        lineAO = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.O)
        lineAO.isConstruction = True

        # Draw a locking circle.
        lockingCircle = self.__baseSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__lockingDiam/2)
        lockingCircle.isConstruction = True

        # Draw a line OD.
        transform.setToRotation(math.radians(-60), self.__normal, self.__points.O)
        self.__points.D = adsk.core.Point3D.create(self.__points.A.x, self.__points.A.y, self.__points.A.z)
        self.__points.D.transformBy(transform)
        lineOD = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.D)
        lineOD.isConstruction = True

        # Draw a line OE.
        transform.setToRotation(math.radians(60), self.__normal, self.__points.O)
        self.__points.E = adsk.core.Point3D.create(self.__points.A.x, self.__points.A.y, self.__points.A.z)
        self.__points.E.transformBy(transform)
        lineOE = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.E)
        lineOE.isConstruction = True

        # Draw a line AC.
        transform.setToRotation(math.radians(-29), self.__normal, self.__points.A)
        self.__points.C = adsk.core.Point3D.create(self.__points.O.x, self.__points.O.y, self.__points.O.z)
        self.__points.C.transformBy(transform)
        lineAC = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.C)
        lineAC.isConstruction = True

        # Draw a line AT.
        transform.setToRotation(math.radians(-7), self.__normal, self.__points.A)
        self.__points.T = adsk.core.Point3D.create(self.__points.C.x, self.__points.C.y, self.__points.C.z)
        self.__points.T.transformBy(transform)
        lineAT = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.T)
        lineAT.isConstruction = True

        # Draw a line AY.
        transform.setToRotation(math.radians(-4), self.__normal, self.__points.A)
        self.__points.Y = adsk.core.Point3D.create(self.__points.T.x, self.__points.T.y, self.__points.T.z)
        self.__points.Y.transformBy(transform)
        lineAY = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.Y)
        lineAY.isConstruction = True

        # Draw a line OK.
        transform.setToRotation(math.radians(10), self.__normal, self.__points.O)
        self.__points.K = adsk.core.Point3D.create(self.__points.E.x, self.__points.E.y, self.__points.E.z)
        self.__points.K.transformBy(transform)
        lineOK = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.K)
        lineOK.isConstruction = True

        # Draw an arc HL.
        self.__points.L = lineAC.geometry.intersectWithCurve(lineOE.geometry)[0]
        arcHL = self.__baseSketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.O, self.__points.L, math.radians(30))
        arcHL.isConstruction = True

        # Draw a line FG.
        self.__points.G = lineOK.geometry.intersectWithCurve(arcHL.geometry)[0]
        transform.setToRotation(math.radians(90), self.__normal, self.__points.G)
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(lineOK)
        copiedEntities = self.__baseSketch.copy(inputEntities, transform) # create a temporary line of FG perpendicular to the line OK.
        tempLineFG = next((entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)), None) # get the line from copied entity.

        transform.setToRotation(math.radians(-2), self.__normal, self.__points.O)
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(lineOK)
        copiedEntities = self.__baseSketch.copy(inputEntities, transform) # create a temporary line of OF for getting point F.
        tempLineOF = next((entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)), None) # get the line from copied entity.

        self.__points.F = tempLineOF.geometry.intersectWithCurve(tempLineFG.geometry)[0] # get the point F as intersection of 2 temporary lines.
        tempLineFG.deleteMe()
        tempLineOF.deleteMe()
        lineOF = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.F)
        lineOF.isConstruction = True
        lineFG = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.G)
        lineFG.isConstruction = True

        # Draw a line Fa, for incline of the pallet.
        self.__points.a = lineAY.geometry.intersectWithCurve(lockingCircle.geometry)[0]
        lineFa = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.a)
        lineFa.isConstruction = True

        # Draw a major circle.
        self.__points.J = lineAT.geometry.intersectWithCurve(lineFa.geometry)[0]
        self.__baseSketch.sketchPoints.add(self.__points.J)
        self.__majorRadius = math.sqrt((self.__points.J.x - self.__points.A.x)**2+(self.__points.J.y - self.__points.A.y)**2+(self.__points.J.z - self.__points.A.z)**2)
        majorCircle = self.__baseSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__majorRadius)
        majorCircle.isConstruction = True

        # Draw a line AB.
        transform.setToRotation(math.radians(31), self.__normal, self.__points.A)
        self.__points.B = adsk.core.Point3D.create(0, self.__majorRadius, 0)
        self.__points.B.transformBy(transform)
        lineAB = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.B)
        lineAB.isConstruction = True

        # Draw a line AM.
        transform.setToRotation(math.radians(-7), self.__normal, self.__points.A)
        self.__points.M = adsk.core.Point3D.create(self.__points.B.x, self.__points.B.y, self.__points.B.z)
        self.__points.M.transformBy(transform)
        lineAM = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.M)
        lineAM.isConstruction = True

        # Draw a line AN.
        transform.setToRotation(math.radians(4), self.__normal, self.__points.A)
        self.__points.N = adsk.core.Point3D.create(self.__points.B.x, self.__points.B.y, self.__points.B.z)
        self.__points.N.transformBy(transform)
        lineAN = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.N)
        lineAN.isConstruction = True

        # Draw an arc VP (but point P isn't defined yet).
        self.__points.V = lineOD.geometry.intersectWithCurve(lineAM.geometry)[0]
        arcVP = self.__baseSketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.O, self.__points.V, math.radians(30))
        arcVP.isConstruction = True

        # Define a point P by using the arc VP, and draw a line OP.
        transform.setToRotation(math.radians(10), self.__normal, self.__points.O)
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(lineOD)
        copiedEntities = self.__baseSketch.copy(inputEntities, transform) # create a temporary line of OP for getting point P.
        tempLineOP = next((entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)), None) # get the line from copied entity.

        self.__points.P = tempLineOP.geometry.intersectWithCurve(arcVP.geometry)[0]
        tempLineOP.deleteMe()

        lineOP = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.P)
        lineOP.isConstruction = True

        # Draw a line RW.
        self.__points.R = lineOD.geometry.intersectWithCurve(lineAB.geometry)[0]
        vectorOD = adsk.core.Vector3D.create(self.__points.D.x - self.__points.O.x, self.__points.D.y - self.__points.O.y, self.__points.D.z - self.__points.O.z)
        vectorPerpendicularOD = adsk.core.Vector3D.create(vectorOD.y, -vectorOD.x, vectorOD.z)
        vectorPerpendicularOD.scaleBy(0.1)

        self.__points.W = adsk.core.Point3D.create(self.__points.R.x + vectorPerpendicularOD.x, self.__points.R.y + vectorPerpendicularOD.y, self.__points.R.z + vectorPerpendicularOD.z)
        lineRW = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, self.__points.W)
        lineRW.isConstruction = True

        # Draw a line OQ.
        transform.setToRotation(math.radians(2), self.__normal, self.__points.O)
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(lineOD)
        copiedEntities = self.__baseSketch.copy(inputEntities, transform) # create a temporary line of OQ for getting point Q.
        tempLineOQ = next((entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)), None) # get the line from copied entity.

        transform.setToRotation(math.radians(-13.5-90), self.__normal, self.__points.R)
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(lineOD)
        copiedEntities = self.__baseSketch.copy(inputEntities, transform) # create a temporary line of enter pallet for getting point Q.
        tempEnterPalletLockingFace = next((entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)), None) # get the line from copied entity.

        self.__points.Q = tempLineOQ.geometry.intersectWithCurve(tempEnterPalletLockingFace.geometry)[0]
        tempEnterPalletLockingFace.deleteMe()
        tempLineOQ.deleteMe()

        lineOQ = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.Q)
        lineOQ.isConstruction = True

    def drawWheel(self):
         # Define a matrix for rotation.
        transform = adsk.core.Matrix3D.create()

        # Draw the face of wheel teeth.
        wheelAxisHoleCircle  = self.__wheelSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__holeDiam/2)

        transform.setToRotation(math.radians(-24), self.__normal, self.__points.R)
        self.__points.X = adsk.core.Point3D.create(self.__points.A.x, self.__points.A.y, self.__points.A.z)
        self.__points.X.transformBy(transform)
        wheelTeethInclineFace = self.__wheelSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.N, self.__points.R)
        tempWheelTeethLockingFace = self.__wheelSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, self.__points.X)
        tempWheelTeethLockingFace.isConstruction = True

        teethRootRadius = self.__majorRadius*2/3
        teethRootCircle = self.__wheelSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, teethRootRadius)
        teethRootCircle.isConstruction = True

        self.__points.Z = tempWheelTeethLockingFace.geometry.intersectWithCurve(teethRootCircle.geometry)[0]
        wheelTeethLockingFace = self.__wheelSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, self.__points.Z)
        tempWheelTeethLockingFace.deleteMe()

        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(wheelTeethInclineFace)
        inputEntities.add(wheelTeethLockingFace)

        for i in range(1, 16):
            transform.setToRotation(math.radians(360/15), self.__normal, self.__points.A)
            copiedEntities = self.__wheelSketch.copy(inputEntities, transform)
            copiedSketchLine = [entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)]
            controlPoints = [inputEntities.item(0).geometry.startPoint, inputEntities.item(0).geometry.endPoint, copiedSketchLine[1].geometry.endPoint]
            wheelTeethAnotherFace = self.__wheelSketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

            evaluator = wheelTeethAnotherFace.evaluator
            _, wheelTeethAnotherFaceStartPoint, _ = evaluator.getEndPoints()
            self.__wheelSketch.sketchCurves.sketchArcs.addFillet(wheelTeethAnotherFace, wheelTeethAnotherFaceStartPoint, inputEntities.item(0), inputEntities.item(0).geometry.startPoint, 0.005)

            if i == 15:
                copiedSketchLine[0].deleteMe()
                copiedSketchLine[1].deleteMe()
            else:
                inputEntities = adsk.core.ObjectCollection.create()
                inputEntities.add(copiedSketchLine[0])
                inputEntities.add(copiedSketchLine[1])

    def drawPallets(self):
        # Define a matrix for rotation.
        transform = adsk.core.Matrix3D.create()

        palletAxisHoleCIrcle = self.__palletSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.O, self.__holeDiam/2)

        # Draw the face of enter pallet.
        enterPalletInclineFace = self.__palletSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, self.__points.P)

        transform.setToRotation(math.radians(-13.5), self.__normal, self.__points.R)
        vectorRW = adsk.core.Vector3D.create(self.__points.W.x - self.__points.R.x, self.__points.W.y - self.__points.R.y, self.__points.W.z - self.__points.R.z)
        vectorEnterPalletLockingFace = adsk.core.Vector3D.create(vectorRW.x, vectorRW.y, vectorRW.z)
        vectorEnterPalletLockingFace.transformBy(transform)
        vectorEnterPalletLockingFace.normalize()
        enterPalletLockingFace = self.__palletSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, adsk.core.Point3D.create(self.__points.Q.x + vectorEnterPalletLockingFace.x,
                                                                                                                                       self.__points.Q.y + vectorEnterPalletLockingFace.y,
                                                                                                                                       self.__points.Q.z + vectorEnterPalletLockingFace.z))
        enterPalletAnotherFace = self.__palletSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.P, adsk.core.Point3D.create(self.__points.P.x + vectorEnterPalletLockingFace.x,
                                                                                                                                       self.__points.P.y + vectorEnterPalletLockingFace.y,
                                                                                                                                       self.__points.P.z + vectorEnterPalletLockingFace.z))

        # Draw the face of exit pallet.
        exitPalletInclineFace = self.__palletSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.J)

        transform.setToRotation(math.radians(-15), self.__normal, self.__points.F)
        vectorFG = adsk.core.Vector3D.create(self.__points.G.x - self.__points.F.x, self.__points.G.y - self.__points.F.y, self.__points.G.z - self.__points.F.z)
        vectorExitPalletLockingFace = adsk.core.Vector3D.create(vectorFG.x, vectorFG.y, vectorFG.z)
        vectorExitPalletLockingFace.transformBy(transform)
        vectorExitPalletLockingFace.normalize()
        exitPalletLockingFace = self.__palletSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, adsk.core.Point3D.create(self.__points.F.x + vectorExitPalletLockingFace.x,
                                                                                                                                      self.__points.F.y + vectorExitPalletLockingFace.y,
                                                                                                                                      self.__points.F.z + vectorExitPalletLockingFace.z))
        exitPalletAnotherFace = self.__palletSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, adsk.core.Point3D.create(self.__points.J.x + vectorExitPalletLockingFace.x,
                                                                                                                                      self.__points.J.y + vectorExitPalletLockingFace.y,
                                                                                                                                      self.__points.J.z + vectorExitPalletLockingFace.z))