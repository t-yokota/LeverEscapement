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
_numTeeth = adsk.core.TextBoxCommandInput.cast(None)
_lockingDiam = adsk.core.ValueCommandInput.cast(None)
_holeDiam = adsk.core.ValueCommandInput.cast(None)
_thickness = adsk.core.ValueCommandInput.cast(None)
_majorDiam = adsk.core.TextBoxCommandInput.cast(None)
_pivotDistBetweenWheelAndPallets = adsk.core.TextBoxCommandInput.cast(None)
_pivotDistBetweenLeverAndRoller = adsk.core.ValueCommandInput.cast(None)
_leverWidth = adsk.core.ValueCommandInput.cast(None)
_rollerAngleRaitoToLeverAngle = adsk.core.ValueCommandInput.cast(None)
_balanceRollerDiamRaitoToSatefyRollerDiam = adsk.core.ValueCommandInput.cast(None)
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
            cmdDef = _ui.commandDefinitions.addButtonDefinition('adskLeverEscapementPythonScript', 'Lever Escapement', 'Creates components for an escape wheel, a pallet lever, and a balance roller.', 'resources/LeverEscapement')

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

            global _units
            _units = 'mm'

            # Define the default values and get the previous values from the attributes.
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

            wheelAndPallets = WheelAndPallets(des, int(numTeeth), float(lockingDiam), float(holeDiam), float(thickness))
            majorDiam = str(round(wheelAndPallets.getMajorDiameterOfWheel()*10, 3)) + " mm"

            pivotDistBetweenWheelAndPallets = str(round(wheelAndPallets.getPivotDistance()*10, 3)) + "mm"

            pivotDistBetweenLeverAndRoller = str(wheelAndPallets.getPivotDistance())
            pivotDistBetweenLeverAndRollerAttrib = des.attributes.itemByName('LeverEscapement', 'pivotDistBetweenLeverAndRoller')
            if pivotDistBetweenLeverAndRollerAttrib:
                pivotDistBetweenLeverAndRoller = pivotDistBetweenLeverAndRollerAttrib.value

            leverWidth = '0.4'
            leverWidthAttrib = des.attributes.itemByName('LeverEscapement', 'leverWidth')
            if leverWidthAttrib:
                leverWidthAttrib = leverWidthAttrib.value

            rollerAngleRaitoToLeverAngle = '3'
            rollerAngleRaitoToLeverAngleAttrib = des.attributes.itemByName('LeverEscapement', 'rollerAngleRaitoToLeverAngle')
            if rollerAngleRaitoToLeverAngleAttrib:
                rollerAngleRaitoToLeverAngleAttrib = rollerAngleRaitoToLeverAngleAttrib.value

            balanceRollerDiamRaitoToSatefyRollerDiam = '2'
            balanceRollerDiamRaitoToSatefyRollerDiamAttrib = des.attributes.itemByName('LeverEscapement', 'balanceRollerDiamRaitoToSatefyRollerDiam')

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            global _description, _numTeeth, _lockingDiam, _holeDiam, _thickness, _majorDiam, _pivotDistBetweenWheelAndPallets, _pivotDistBetweenLeverAndRoller, _leverWidth, _rollerAngleRaitoToLeverAngle, _balanceRollerDiamRaitoToSatefyRollerDiam, _errMessage

            # Define the command dialog.
            _description = inputs.addTextBoxCommandInput('description', '', '<br><b>The Escape wheel and the Pallets:</b>', 2, True)
            _description.isFullWidth = True

            _numTeeth = inputs.addTextBoxCommandInput('numTeeth', 'Number of Teeth', numTeeth, 1, True)

            _lockingDiam = inputs.addValueInput('lockingDiam', 'locking Diameter', _units, adsk.core.ValueInput.createByReal(float(lockingDiam)))

            _holeDiam = inputs.addValueInput('holeDiam', 'Hole Diameter', _units, adsk.core.ValueInput.createByReal(float(holeDiam)))

            _thickness = inputs.addValueInput('thickness', 'Wheel Thickness', _units, adsk.core.ValueInput.createByReal(float(thickness)))

            _majorDiam = inputs.addTextBoxCommandInput('majorDiam', 'Major Diameter', majorDiam, 1, True)

            _pivotDistBetweenWheelAndPallets = inputs.addTextBoxCommandInput('pivotDistBetweenWheelAndPallets', 'Distance between a wheel pivot and a pallets(lever) pivot', pivotDistBetweenWheelAndPallets, 1, True)

            _description = inputs.addTextBoxCommandInput('description', '', '<br><b>The Lever and the Roller:</b>', 2, True)
            _description.isFullWidth = True

            _pivotDistBetweenLeverAndRoller = inputs.addValueInput('pivotDistBetweenLeverAndRoller', 'Distance between a pallets(lever) pivot and a roller pivot', _units, adsk.core.ValueInput.createByReal(float(pivotDistBetweenLeverAndRoller)))

            _leverWidth = inputs.addValueInput('leverWidth', 'Width of the lever', _units, adsk.core.ValueInput.createByReal(float(leverWidth)))

            _rollerAngleRaitoToLeverAngle = inputs.addValueInput('rollerAngleRaitoToLeverAngle', 'Raito of the roller angle to the lever angle', '', adsk.core.ValueInput.createByReal(float(rollerAngleRaitoToLeverAngle)))

            _balanceRollerDiamRaitoToSatefyRollerDiam = inputs.addValueInput('balanceRollerDiamRaitoToSatefyRollerDiam', 'Raito of the balance roller diameter to the safety roller diameter', '', adsk.core.ValueInput.createByReal(float(balanceRollerDiamRaitoToSatefyRollerDiam)))

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
            attribs.add('LeverEscapement', 'numTeeth', _numTeeth.text)
            attribs.add('LeverEscapement', 'lockingDiam', str(_lockingDiam.value))
            attribs.add('LeverEscapement', 'holeDiam', str(_holeDiam.value))
            attribs.add('LeverEscapement', 'thickness', str(_thickness.value))
            attribs.add('LeverEscapement', 'pivotDistBetweenLeverAndRoller', str(_pivotDistBetweenLeverAndRoller.value))
            attribs.add('LeverEscapement', 'leverWidth', str(_leverWidth.value))
            attribs.add('LeverEscapement', 'rollerAngleRaitoToLeverAngle', str(_rollerAngleRaitoToLeverAngle.value))
            attribs.add('LeverEscapement', 'rollerAngleRaitoToLeverAngle', str(_balanceRollerDiamRaitoToSatefyRollerDiam.value))

            numTeeth = int(_numTeeth.text)
            lockingDiam = _lockingDiam.value
            holeDiam = _holeDiam.value
            thickness = _thickness.value
            pivotDistBetweenLeverAndRoller = _pivotDistBetweenLeverAndRoller.value
            leverWidth = _leverWidth.value
            rollerAngleRaitoToLeverAngle = _rollerAngleRaitoToLeverAngle.value
            balanceRollerDiamRaitoToSatefyRollerDiam = _balanceRollerDiamRaitoToSatefyRollerDiam.value

            # create the pallet and escape wheel.
            # drawWheelAndPallet(des, numTeeth, lockingDiam, holeDiam, thickness)
            wheelAndPallets = WheelAndPallets(des, numTeeth, lockingDiam, holeDiam, thickness)
            wheelAndPallets.draw()

            pivotDistBetweenWheelAndPallets = wheelAndPallets.getPivotDistance()
            leverAndRoller = LeverAndRoller(des, pivotDistBetweenLeverAndRoller, leverWidth, rollerAngleRaitoToLeverAngle, balanceRollerDiamRaitoToSatefyRollerDiam, pivotDistBetweenWheelAndPallets)
            leverAndRoller.draw()

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

            # Update the major diameter value.
            if changedInput.id == 'lockingDiam':
                try:
                    des = adsk.fusion.Design.cast(_app.activeProduct)
                    wheelAndPallets = WheelAndPallets(des, _numTeeth.text, _lockingDiam.value, _holeDiam.value, _thickness.value)
                    _majorDiam.text = str(round(wheelAndPallets.getMajorDiameterOfWheel()*10, 3))+" mm"
                    _pivotDistBetweenWheelAndPallets.text = str(round(wheelAndPallets.getPivotDistance()*10, 3)) + "mm"
                    if _pivotDistBetweenLeverAndRoller.value < wheelAndPallets.getPivotDistance():
                        _pivotDistBetweenLeverAndRoller.value = wheelAndPallets.getPivotDistance()
                except:
                    _majorDiam.text = " mm"
                    _pivotDistBetweenWheelAndPallets.text = " mm"
                    _pivotDistBetweenLeverAndRoller.value = 0.0

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

class Points:
    def __init__(self):
        pass

    def getIntersectionPoint(self, point1, point2, point3, point4):
        vector1to2 = point1.vectorTo(point2)
        vector3to4 = point3.vectorTo(point4)
        vector3to1 = point3.vectorTo(point1)
        crossProduct = vector3to4.crossProduct(vector1to2)

        if crossProduct.length > 0:
            scalar = vector3to1.crossProduct(vector3to4).length / vector3to4.crossProduct(vector1to2).length
            vector1toInts = vector1to2.copy()
            vector1toInts.scaleBy(scalar)
            intersectionPoint = point1.copy()
            intersectionPoint.translateBy(vector1toInts)
            return intersectionPoint
        else:
            None

class WheelAndPallets():
    def __init__(self, design, numTeeth, lockingDiam, holeDiam, thickness):
        self.__design = design
        self.__numTeeth = numTeeth
        self.__lockingDiam = lockingDiam
        self.__holeDiam = holeDiam
        self.__thickness = thickness

        self.__points = Points()
        self.__getPointsForDrawing()

    def draw(self):
        self.createSketches()
        self.drawConstructions()
        self.drawWheel()
        self.drawPallets()

    def createSketches(self):
        # Get occurences in the root component.
        self.__occs = self.__design.rootComponent.occurrences

        # Add new components to the occurences.
        self.__wheelOcc = self.__occs.addNewComponent(adsk.core.Matrix3D.create())
        self.__palletOcc = self.__occs.addNewComponent(adsk.core.Matrix3D.create())

        # Get objects of new compornents.
        self.__wheelComp = adsk.fusion.Component.cast(self.__wheelOcc.component)
        self.__palletComp = adsk.fusion.Component.cast(self.__palletOcc.component)

        self.__wheelComp.name = "escape wheel"
        self.__palletComp.name = "pallets"

        # Create new sketches in each component.
        self.__baseSketch = self.__wheelComp.sketches.add(self.__wheelComp.xYConstructionPlane)
        self.__wheelSketch = self.__wheelComp.sketches.add(self.__wheelComp.xYConstructionPlane)
        self.__palletSketch =  self.__palletComp.sketches.add(self.__palletComp.xYConstructionPlane)

        self.__baseSketch.name = "constructions"
        self.__wheelSketch.name = "escape wheel"
        self.__palletSketch.name = "pallets"

        # Define a normal vector for rotation.
        self.__normal = self.__baseSketch.referencePlane.geometry.normal
        self.__normal.transformBy(self.__baseSketch.transform)

    def getPivotDistance(self):
        return (self.__lockingDiam/2.0)/math.cos(math.radians(30.0))

    def getMajorDiameterOfWheel(self):
        return self.__points.A.vectorTo(self.__points.J).length*2

    def __getPointsForDrawing(self):
        # Define a matrix and a normal vector for rotation.
        transform = adsk.core.Matrix3D.create()
        normal = adsk.core.Vector3D.create(0, 0, 1)

        # Get a Wheel pivot.
        self.__points.A = adsk.core.Point3D.create(0, 0, 0)

        # Get a Pallet pivot.
        self.__points.O = self.__points.A.copy()
        self.__points.O.translateBy(adsk.core.Vector3D.create(0, self.getPivotDistance(), 0))

        # Get a point D.
        transform.setToRotation(math.radians(-60), normal, self.__points.O)
        self.__points.D = self.__points.A.copy()
        self.__points.D.transformBy(transform)

        # Get a point E.
        transform.setToRotation(math.radians(60), normal, self.__points.O)
        self.__points.E = self.__points.A.copy()
        self.__points.E.transformBy(transform)

        # Get a point B.
        transform.setToRotation(math.radians(31), normal, self.__points.A)
        self.__points.B = self.__points.O.copy()
        self.__points.B.transformBy(transform)

        # Get a point C.
        transform.setToRotation(math.radians(-29), normal, self.__points.A)
        self.__points.C = self.__points.O.copy()
        self.__points.C.transformBy(transform)

        # Get a point T.
        transform.setToRotation(math.radians(-7), normal, self.__points.A)
        self.__points.T = self.__points.C.copy()
        self.__points.T.transformBy(transform)

        # Get a point Y.
        transform.setToRotation(math.radians(-4), normal, self.__points.A)
        self.__points.Y = self.__points.T.copy()
        self.__points.Y.transformBy(transform)

        # Get a temporary point F.
        transform.setToRotation(math.radians(8), normal, self.__points.O)
        self.__points.__F = self.__points.E.copy()
        self.__points.__F.transformBy(transform)

        # Get a point K.
        transform.setToRotation(math.radians(2), normal, self.__points.O)
        self.__points.K = self.__points.__F.copy()
        self.__points.K.transformBy(transform)

        # Get a point L.
        transform.setToRotation(math.radians(-29), normal, self.__points.A.copy())
        self.__points.L = self.__points.A.copy()
        self.__points.L.translateBy(adsk.core.Vector3D.create(0, self.__lockingDiam/2, 0))
        self.__points.L.transformBy(transform)

        # Get a point G.
        angleEOL = self.__points.O.vectorTo(self.__points.E).dotProduct(self.__points.O.vectorTo(self.__points.L))
        angleEOL = angleEOL/(self.__points.O.vectorTo(self.__points.E).length*self.__points.O.vectorTo(self.__points.L).length)
        angleEOL = math.degrees(math.acos(angleEOL))
        transform.setToRotation(math.radians(10+angleEOL), normal, self.__points.O)
        self.__points.G = self.__points.L.copy()
        self.__points.G.transformBy(transform)

        # Get a point F.
        scalar = self.__points.O.vectorTo(self.__points.G).length/math.cos(math.radians(2.0))
        vector = self.__points.O.vectorTo(self.__points.__F)
        vector.normalize()
        vector.scaleBy(scalar)
        self.__points.F = self.__points.O.copy()
        self.__points.F.translateBy(vector)

        # Get a point a.
        transform.setToRotation(math.radians(-40), normal, self.__points.A)
        self.__points.a = self.__points.A.copy()
        self.__points.a.translateBy(adsk.core.Vector3D.create(0, self.__lockingDiam/2, 0))
        self.__points.a.transformBy(transform)

        # Get a point J.
        self.__points.J = self.__points.getIntersectionPoint(self.__points.A, self.__points.T, self.__points.F, self.__points.a)

        # Get a point M.
        transform.setToRotation(math.radians(-7), normal, self.__points.A)
        self.__points.M = self.__points.B.copy()
        self.__points.M.transformBy(transform)

        # Get a temporary point N.
        transform.setToRotation(math.radians(4), normal, self.__points.A)
        self.__points.__N = self.__points.B.copy()
        self.__points.__N.transformBy(transform)

        # Get a point N.
        scalar = self.getMajorDiameterOfWheel()/2
        vector = self.__points.A.vectorTo(self.__points.__N)
        vector.normalize()
        vector.scaleBy(scalar)
        self.__points.N = self.__points.A.copy()
        self.__points.N.translateBy(vector)

        # Get a point V.
        self.__points.V = self.__points.getIntersectionPoint(self.__points.O, self.__points.D, self.__points.A, self.__points.M)

        # Get a point P.
        transform.setToRotation(math.radians(10), normal, self.__points.O)
        self.__points.P = self.__points.V.copy()
        self.__points.P.transformBy(transform)

        # Get a point R.
        self.__points.R = self.__points.getIntersectionPoint(self.__points.O, self.__points.D, self.__points.A, self.__points.B)

        # Get a point W.
        transform.setToRotation(math.radians(90), normal, self.__points.R)
        vector = self.__points.R.vectorTo(self.__points.O)
        vector.normalize()
        vector.scaleBy(0.5)
        vector.transformBy(transform)
        self.__points.W = self.__points.R.copy()
        self.__points.W.translateBy(vector)

        # Get a temporary point R.
        transform.setToRotation(math.radians(-90), normal, self.__points.R)
        vector = self.__points.R.vectorTo(self.__points.O)
        vector.transformBy(transform)
        self.__points.__R = self.__points.R.copy()
        self.__points.__R.translateBy(vector)

        transform.setToRotation(math.radians(-13.5), normal, self.__points.R)
        self.__points.__R.transformBy(transform)

        # Get a temporary point W.
        self.__points.__W = self.__points.W.copy()
        self.__points.__W.transformBy(transform)

        # Get a temporary point Q.
        transform.setToRotation(math.radians(2), normal, self.__points.O)
        self.__points.__Q = self.__points.D.copy()
        self.__points.__Q.transformBy(transform)

        # Get a point Q.
        self.__points.Q = self.__points.getIntersectionPoint(self.__points.__W, self.__points.__R, self.__points.__Q, self.__points.O)

    def drawWheel(self):
        # Define a matrix for rotation.
        transform = adsk.core.Matrix3D.create()

        # Draw the hole for wheel pivot.
        wheelPivotHole  = self.__wheelSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__holeDiam/2)
        # normal = adsk.core.Vector3D.create(0, 0, 1)

        # Draw the face of wheel teeth.
        transform.setToRotation(math.radians(-24), self.__normal, self.__points.R)
        self.__points.X = self.__points.A.copy()
        self.__points.X.transformBy(transform)
        wheelTeethInclineFace = self.__wheelSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.N, self.__points.R)
        tempWheelTeethLockingFace = self.__wheelSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, self.__points.X)
        # tempWheelTeethLockingFace.isConstruction = True

        teethRootRadius = self.getMajorDiameterOfWheel()/3
        teethRootCircle = self.__wheelSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, teethRootRadius)
        teethRootCircle.isConstruction = True

        self.__points.Z = tempWheelTeethLockingFace.geometry.intersectWithCurve(teethRootCircle.geometry).item(0)
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

        # Draw the hole for pallet pivot.
        palletPivotHole = self.__palletSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.O, self.__holeDiam/2)

        # Draw the face of enter pallet.
        enterPalletInclineFace = self.__palletSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, self.__points.P)

        transform.setToRotation(math.radians(-13.5), self.__normal, self.__points.R)
        vectorEnterPalletLockingFace = self.__points.R.vectorTo(self.__points.W)
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
        vectorExitPalletLockingFace = self.__points.F.vectorTo(self.__points.G)
        vectorExitPalletLockingFace.transformBy(transform)
        vectorExitPalletLockingFace.normalize()
        exitPalletLockingFace = self.__palletSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, adsk.core.Point3D.create(self.__points.F.x + vectorExitPalletLockingFace.x,
                                                                                                                                      self.__points.F.y + vectorExitPalletLockingFace.y,
                                                                                                                                      self.__points.F.z + vectorExitPalletLockingFace.z))
        exitPalletAnotherFace = self.__palletSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, adsk.core.Point3D.create(self.__points.J.x + vectorExitPalletLockingFace.x,
                                                                                                                                      self.__points.J.y + vectorExitPalletLockingFace.y,
                                                                                                                                      self.__points.J.z + vectorExitPalletLockingFace.z))

    def drawConstructions(self):
        # Draw a line AO as center line.
        lineAO = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.O)
        lineAO.isConstruction = True

        # Draw a locking circle.
        lockingCircle = self.__baseSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__lockingDiam/2)
        lockingCircle.isConstruction = True

        # Draw a line OD.
        lineOD = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.D)
        lineOD.isConstruction = True

        # Draw a line OE.
        lineOE = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.E)
        lineOE.isConstruction = True

        # Draw a line AC.
        lineAC = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.C)
        lineAC.isConstruction = True

        # Draw a line AT.
        lineAT = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.T)
        lineAT.isConstruction = True

        # Draw a line AY.
        lineAY = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.Y)
        lineAY.isConstruction = True

        # Draw a line OK.
        lineOK = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.K)
        lineOK.isConstruction = True

        # Draw an arc HL.
        arcHL = self.__baseSketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.O, self.__points.L, math.radians(30))
        arcHL.isConstruction = True

        # Draw a line FG.
        lineOF = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.F)
        lineOF.isConstruction = True

        lineFG = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.G)
        lineFG.isConstruction = True

        # Draw a line Fa, for incline of the pallet.
        lineFa = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.a)
        lineFa.isConstruction = True

        # Draw a major circle.
        majorRadius = self.getMajorDiameterOfWheel()/2
        majorCircle = self.__baseSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, majorRadius)
        majorCircle.isConstruction = True

        # Draw a line AB.
        lineAB = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.B)
        lineAB.isConstruction = True

        # Draw a line AM.
        lineAM = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.M)
        lineAM.isConstruction = True

        # Draw a line AN.
        lineAN = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.N)
        lineAN.isConstruction = True

        # Draw an arc VP.
        arcVP = self.__baseSketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.O, self.__points.V, math.radians(30))
        arcVP.isConstruction = True

        lineOP = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.P)
        lineOP.isConstruction = True

        # Draw a line RW.
        lineRW = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, self.__points.W)
        lineRW.isConstruction = True

        # Draw a line OQ.
        lineOQ = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.Q)
        lineOQ.isConstruction = True

class LeverAndRoller(Points):
    def __init__(self, design, pivotDistBetweenLeverAndRoller, leverWidth, rollerAngleRaitoToLeverAngle, balanceRollerDiamRaitoToSatefyRollerDiam, pivotDistBetweenWheelAndPallets):
        self.__design = design
        self.__pivotDistBetweenLeverAndRoller = pivotDistBetweenLeverAndRoller
        self.__leverWidth = leverWidth
        self.__rollerAngleRaitoToLeverAngle = rollerAngleRaitoToLeverAngle
        self.__balanceRollerDiamRaitoToSatefyRollerDiam = balanceRollerDiamRaitoToSatefyRollerDiam
        self.__pivotDistBetweenWheelAndPallets = pivotDistBetweenWheelAndPallets

        self.__points = Points()
        self.__getPointsForDrawing()

    def draw(self):
        self.createSketches()
        self.drawConstructions()
        # self.drawRoller()
        # self.drawLever()

    def createSketches(self):
        # Get occurences in the root component.
        self.__occs = self.__design.rootComponent.occurrences

        # Add new components to the occurences.
        self.__leverOcc = self.__occs.addNewComponent(adsk.core.Matrix3D.create())
        self.__rollerOcc = self.__occs.addNewComponent(adsk.core.Matrix3D.create())

        # Get objects of new compornents.
        self.__leverComp = adsk.fusion.Component.cast(self.__leverOcc.component)
        self.__rollerComp = adsk.fusion.Component.cast(self.__rollerOcc.component)

        self.__leverComp.name = "lever"
        self.__rollerComp.name = "roller"

        # Create new sketches in each component.
        self.__baseSketch = self.__leverComp.sketches.add(self.__leverComp.xYConstructionPlane)
        self.__leverSketch =  self.__leverComp.sketches.add(self.__leverComp.xYConstructionPlane)
        self.__rollerSketch = self.__rollerComp.sketches.add(self.__rollerComp.xYConstructionPlane)

        self.__baseSketch.name = "constructions"
        self.__leverSketch.name = "lever"
        self.__rollerSketch.name = "roller"

        # Define a normal vector for rotation.
        self.__normal = self.__baseSketch.referencePlane.geometry.normal
        self.__normal.transformBy(self.__baseSketch.transform)

    def __getPointsForDrawing(self):
        # Define a matrix and a normal vector for rotation.
        transform = adsk.core.Matrix3D.create()
        normal = adsk.core.Vector3D.create(0, 0, 1)

        self.__points.O = adsk.core.Point3D.create(0, 0, 0)
        self.__points.O.translateBy(adsk.core.Vector3D.create(0, self.__pivotDistBetweenWheelAndPallets, 0))

        self.__points.A = self.__points.O.copy()
        self.__points.A.translateBy(adsk.core.Vector3D.create(0, self.__pivotDistBetweenLeverAndRoller, 0))

        transform.setToRotation(math.radians(5), normal, self.__points.O)
        self.__points.B = self.__points.A.copy()
        self.__points.B.transformBy(transform)

        transform.setToRotation(math.radians(-5*self.__rollerAngleRaitoToLeverAngle), normal, self.__points.A)
        self.__points.C = self.__points.O.copy()
        self.__points.C.transformBy(transform)

        self.__points.D = self.__points.getIntersectionPoint(self.__points.O, self.__points.B, self.__points.A, self.__points.C)

    def drawConstructions(self):
        lineAO = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.O)
        lineAO.isConstruction = True

        lineOB = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.B)
        lineOB.isConstruction = True

        lineAC = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.C)
        lineAC.isConstruction = True

        balanceRollerRadius = self.__points.A.vectorTo(self.__points.D).length
        balanceRollerCircle = self.__baseSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, balanceRollerRadius)
        balanceRollerCircle.isConstruction = True

        safetyRollerRadius = balanceRollerRadius/self.__balanceRollerDiamRaitoToSatefyRollerDiam
        safetyRollerCircle = self.__baseSketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, safetyRollerRadius)
        safetyRollerCircle.isConstruction = True

        # lineAD = self.__baseSketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.D)
        # lineAD.isConstruction = True

    def drawRoller():
        pass

    def drawLever():
        pass