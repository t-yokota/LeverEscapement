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
_holeDiam = adsk.core.ValueCommandInput.cast(None)
_numTeeth = adsk.core.TextBoxCommandInput.cast(None)
_lockingDiam = adsk.core.ValueCommandInput.cast(None)
_thickness = adsk.core.ValueCommandInput.cast(None)
_majorDiam = adsk.core.TextBoxCommandInput.cast(None)
_pivotDistBetweenWheelAndPallets = adsk.core.TextBoxCommandInput.cast(None)
_pivotDistBetweenLeverAndRoller = adsk.core.ValueCommandInput.cast(None)
_leverWidth = adsk.core.ValueCommandInput.cast(None)
_rollerAngleRaitoToLeverAngle = adsk.core.ValueCommandInput.cast(None)
_leverAngle = adsk.core.TextBoxCommandInput.cast(None)
_rollerAngle = adsk.core.TextBoxCommandInput.cast(None)
_impulsePinAngle = adsk.core.ValueCommandInput.cast(None)
_impulsePinDiam = adsk.core.TextBoxCommandInput.cast(None)
_balanceRollerDiamRaitoToSatefyRollerDiam = adsk.core.ValueCommandInput.cast(None)
_balanceRollerDiam = adsk.core.TextBoxCommandInput.cast(None)
_satefyRollerDiam = adsk.core.TextBoxCommandInput.cast(None)
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
            holeDiam = '0.15' # 0.15[cm] = 1.5[mm]
            holeDiamAttrib = des.attributes.itemByName('LeverEscapement', 'holeDiam')
            if holeDiamAttrib:
                holeDiam = holeDiamAttrib.value

            numTeeth = '15'

            lockingDiam = '4' # 4[cm] = 40.0[mm]
            lockingDiamAttrib = des.attributes.itemByName('LeverEscapement', 'lockingDiam')
            if lockingDiamAttrib:
                lockingDiam = lockingDiamAttrib.value

            thickness = '1'
            thicknessAttrib = des.attributes.itemByName('LeverEscapement', 'thickness')
            if thicknessAttrib:
                thickness = thicknessAttrib.value

            wheelAndPallets = WheelAndPallets(des, int(numTeeth), float(lockingDiam), float(holeDiam), float(thickness))
            majorDiam = str(round(wheelAndPallets.getMajorDiameterOfWheel()*10, 3))

            pivotDistBetweenWheelAndPallets = str(round(wheelAndPallets.getPivotDistance()*10, 3))

            pivotDistBetweenLeverAndRoller = str(wheelAndPallets.getPivotDistance())
            pivotDistBetweenLeverAndRollerAttrib = des.attributes.itemByName('LeverEscapement', 'pivotDistBetweenLeverAndRoller')
            if pivotDistBetweenLeverAndRollerAttrib:
                pivotDistBetweenLeverAndRoller = pivotDistBetweenLeverAndRollerAttrib.value

            leverWidth = '0.4'
            leverWidthAttrib = des.attributes.itemByName('LeverEscapement', 'leverWidth')
            if leverWidthAttrib:
                leverWidth = leverWidthAttrib.value

            rollerAngleRaitoToLeverAngle = '3'
            rollerAngleRaitoToLeverAngleAttrib = des.attributes.itemByName('LeverEscapement', 'rollerAngleRaitoToLeverAngle')
            if rollerAngleRaitoToLeverAngleAttrib:
                rollerAngleRaitoToLeverAngle = rollerAngleRaitoToLeverAngleAttrib.value

            leverAngle = '10.0'

            rollerAngle = str(float(leverAngle)*float(rollerAngleRaitoToLeverAngle))

            impulsePinAngle = '12.0'
            impulsePinAngleAttrib = des.attributes.itemByName('LeverEscapement', 'impulsePinAngle')
            if impulsePinAngleAttrib:
                impulsePinAngle = impulsePinAngleAttrib.value

            balanceRollerDiamRaitoToSatefyRollerDiam = '2.0'
            balanceRollerDiamRaitoToSatefyRollerDiamAttrib = des.attributes.itemByName('LeverEscapement', 'balanceRollerDiamRaitoToSatefyRollerDiam')
            if balanceRollerDiamRaitoToSatefyRollerDiamAttrib:
                balanceRollerDiamRaitoToSatefyRollerDiam = balanceRollerDiamRaitoToSatefyRollerDiamAttrib.value

            leverAndRoller = LeverAndRoller(des,
                                            float(pivotDistBetweenWheelAndPallets),
                                            float(pivotDistBetweenLeverAndRoller),
                                            float(leverWidth),
                                            float(rollerAngleRaitoToLeverAngle),
                                            float(leverAngle),
                                            math.radians(float(impulsePinAngle)),
                                            float(balanceRollerDiamRaitoToSatefyRollerDiam),
                                            float(holeDiam))

            balanceRollerDiam = str(round(leverAndRoller.getBalanceRollerDiameter()*10, 3))

            satefyRollerDiam = str(round(leverAndRoller.getBalanceRollerDiameter()*10/float(balanceRollerDiamRaitoToSatefyRollerDiam), 3))

            impulsePinDiam = str(round(leverAndRoller.getImpulsePinDiameter()*10, 3))

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            global _description
            global _numTeeth, _lockingDiam, _holeDiam, _thickness, _majorDiam
            global _pivotDistBetweenWheelAndPallets, _pivotDistBetweenLeverAndRoller, _leverWidth
            global _rollerAngleRaitoToLeverAngle, _leverAngle, _rollerAngle
            global _impulsePinAngle, _impulsePinDiam
            global _balanceRollerDiamRaitoToSatefyRollerDiam, _balanceRollerDiam, _satefyRollerDiam
            global _errMessage

            # Define the command dialog.
            _description = inputs.addTextBoxCommandInput('description', '', '<br><b>Common settings:</b>', 2, True)
            _description.isFullWidth = True

            _holeDiam = inputs.addValueInput('holeDiam', 'Diameter of Pivot Hole', _units, adsk.core.ValueInput.createByReal(float(holeDiam)))

            _description = inputs.addTextBoxCommandInput('description', '', '<br><b>The Escape Wheel and the Pallets:</b>', 2, True)
            _description.isFullWidth = True

            _numTeeth = inputs.addTextBoxCommandInput('numTeeth', 'Number of Teeth', numTeeth, 1, True)

            _lockingDiam = inputs.addValueInput('lockingDiam', 'Locking Diameter', _units, adsk.core.ValueInput.createByReal(float(lockingDiam)))

            _majorDiam = inputs.addTextBoxCommandInput('majorDiam', 'Major Diameter [mm]', majorDiam, 1, True)

            _thickness = inputs.addValueInput('thickness', 'Wheel Thickness', _units, adsk.core.ValueInput.createByReal(float(thickness)))

            _pivotDistBetweenWheelAndPallets = inputs.addTextBoxCommandInput('pivotDistBetweenWheelAndPallets', 'Pivot Distance (Wheel to Pallets) [mm]', pivotDistBetweenWheelAndPallets, 1, True)

            _description = inputs.addTextBoxCommandInput('description', '', '<br><b>The Lever and the Roller:</b>', 2, True)
            _description.isFullWidth = True

            _pivotDistBetweenLeverAndRoller = inputs.addValueInput('pivotDistBetweenLeverAndRoller', 'Pivot Distance (Pallets to Roller)', _units, adsk.core.ValueInput.createByReal(float(pivotDistBetweenLeverAndRoller)))

            _leverWidth = inputs.addValueInput('leverWidth', 'Lever Width', _units, adsk.core.ValueInput.createByReal(float(leverWidth)))

            _rollerAngleRaitoToLeverAngle = inputs.addValueInput('rollerAngleRaitoToLeverAngle', 'Angle Raito (Roller Angle / Lever Angle)', '', adsk.core.ValueInput.createByReal(float(rollerAngleRaitoToLeverAngle)))

            _leverAngle = inputs.addTextBoxCommandInput('leverAngle', 'Lever Angle [deg]', leverAngle, 1, True)

            _rollerAngle = inputs.addTextBoxCommandInput('rollerAngle', 'Roller Angle [deg]', rollerAngle, 1, True)

            _impulsePinAngle = inputs.addValueInput('impulsePinAngle', 'Impulse Pin Angle', 'deg', adsk.core.ValueInput.createByReal(math.radians(float(impulsePinAngle))))

            _impulsePinDiam = inputs.addTextBoxCommandInput('impulsePinDiam', 'Impulse Pin Diameter [mm]', impulsePinDiam, 1, True)

            _balanceRollerDiamRaitoToSatefyRollerDiam = inputs.addValueInput('balanceRollerDiamRaitoToSatefyRollerDiam', 'Diameter Raito (Balance Roller / Safety Roller)', '', adsk.core.ValueInput.createByReal(float(balanceRollerDiamRaitoToSatefyRollerDiam)))

            _balanceRollerDiam = inputs.addTextBoxCommandInput('balanceRollerDiam', 'Balance Roller Diameter [mm]', balanceRollerDiam, 1, True)

            _satefyRollerDiam = inputs.addTextBoxCommandInput('satefyRollerDiam', 'Safety Roller Diameter [mm]', satefyRollerDiam, 1, True)

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
            # attribs.add('LeverEscapement', 'numTeeth', _numTeeth.text)
            attribs.add('LeverEscapement', 'lockingDiam', str(_lockingDiam.value))
            attribs.add('LeverEscapement', 'holeDiam', str(_holeDiam.value))
            attribs.add('LeverEscapement', 'thickness', str(_thickness.value))
            attribs.add('LeverEscapement', 'pivotDistBetweenLeverAndRoller', str(_pivotDistBetweenLeverAndRoller.value))
            attribs.add('LeverEscapement', 'leverWidth', str(_leverWidth.value))
            attribs.add('LeverEscapement', 'rollerAngleRaitoToLeverAngle', str(_rollerAngleRaitoToLeverAngle.value))
            # attribs.add('LeverEscapement', 'leverAngle', _leverAngle.text)
            attribs.add('LeverEscapement', 'impulsePinAngle', str(math.degrees(_impulsePinAngle.value)))
            attribs.add('LeverEscapement', 'balanceRollerDiamRaitoToSatefyRollerDiam', str(_balanceRollerDiamRaitoToSatefyRollerDiam.value))

            numTeeth = int(_numTeeth.text)
            lockingDiam = _lockingDiam.value
            holeDiam = _holeDiam.value
            thickness = _thickness.value
            pivotDistBetweenLeverAndRoller = _pivotDistBetweenLeverAndRoller.value
            leverWidth = _leverWidth.value
            rollerAngleRaitoToLeverAngle = _rollerAngleRaitoToLeverAngle.value
            leverAngle = float(_leverAngle.text)
            impulsePinAngle = _impulsePinAngle.value
            balanceRollerDiamRaitoToSatefyRollerDiam = _balanceRollerDiamRaitoToSatefyRollerDiam.value

            # create the pallet and escape wheel.
            wheelAndPallets = WheelAndPallets(des, numTeeth, lockingDiam, holeDiam, thickness)
            wheelAndPallets.draw()

            pivotDistBetweenWheelAndPallets = wheelAndPallets.getPivotDistance()
            leverAndRoller = LeverAndRoller(des,
                                            pivotDistBetweenWheelAndPallets,
                                            pivotDistBetweenLeverAndRoller,
                                            leverWidth,
                                            rollerAngleRaitoToLeverAngle,
                                            leverAngle,
                                            impulsePinAngle,
                                            balanceRollerDiamRaitoToSatefyRollerDiam,
                                            holeDiam)
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
            des = adsk.fusion.Design.cast(_app.activeProduct)
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            try:
                wheelAndPallets = WheelAndPallets(des, _numTeeth.text, _lockingDiam.value, _holeDiam.value, _thickness.value)
                pivotDistBetweenWheelAndPallets = wheelAndPallets.getPivotDistance()

                leverAndRoller = LeverAndRoller(des,
                                                pivotDistBetweenWheelAndPallets,
                                                _pivotDistBetweenLeverAndRoller.value,
                                                _leverWidth.value,
                                                _rollerAngleRaitoToLeverAngle.value,
                                                float(_leverAngle.text),
                                                _impulsePinAngle.value,
                                                _balanceRollerDiamRaitoToSatefyRollerDiam.value,
                                                _holeDiam.value)
            except:
                pass

            # Update the major diameter value.
            if changedInput.id == 'lockingDiam':
                try:
                    _majorDiam.text = str(round(wheelAndPallets.getMajorDiameterOfWheel()*10, 3))
                    _pivotDistBetweenWheelAndPallets.text = str(round(wheelAndPallets.getPivotDistance()*10, 3))
                    if _pivotDistBetweenLeverAndRoller.value < wheelAndPallets.getPivotDistance():
                        _pivotDistBetweenLeverAndRoller.value = wheelAndPallets.getPivotDistance()
                except:
                    pass

            if changedInput.id == 'rollerAngleRaitoToLeverAngle':
                try:
                    _rollerAngle.text = str(float(_leverAngle.text)*_rollerAngleRaitoToLeverAngle.value)
                except:
                    pass

            if changedInput.id == 'pivotDistBetweenLeverAndRoller' or changedInput.id == 'rollerAngleRaitoToLeverAngle' or changedInput.id == 'impulsePinAngle':
                try:
                    _impulsePinDiam.text = str(round(leverAndRoller.getImpulsePinDiameter()*10, 3))
                except:
                    pass

            if changedInput.id == 'balanceRollerDiamRaitoToSatefyRollerDiam':
                try:
                    _balanceRollerDiam.text = str(round(leverAndRoller.getBalanceRollerDiameter()*10, 3))
                    _satefyRollerDiam.text = str(round(leverAndRoller.getBalanceRollerDiameter()*10/float(_balanceRollerDiamRaitoToSatefyRollerDiam.value), 3))
                except:
                    pass

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

    def getPerpendicularProjectedPoint(self, sourcePoint, lineStart, lineEnd):
        vectorStoP = lineStart.vectorTo(sourcePoint)
        vectorStoE = lineStart.vectorTo(lineEnd)
        dotProduct = vectorStoE.dotProduct(vectorStoP)

        scalar = dotProduct/vectorStoE.length
        vector = vectorStoE.copy()
        vector.normalize()
        vector.scaleBy(scalar)
        projectedPoint = lineStart.copy()
        projectedPoint.translateBy(vector)
        return projectedPoint

    def getLineSymmetryPoint(self, sourcePoint, lineStart, lineEnd):
        projectedPoint = self.getPerpendicularProjectedPoint(sourcePoint, lineStart, lineEnd)
        vector = sourcePoint.vectorTo(projectedPoint)
        symmetryPoint = projectedPoint.copy()
        symmetryPoint.translateBy(vector)
        return symmetryPoint

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
        vectorOE = self.__points.O.vectorTo(self.__points.E)
        vectorOL = self.__points.O.vectorTo(self.__points.L)
        angleEOL = vectorOE.dotProduct(vectorOL)/(vectorOE.length*vectorOL.length)
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
    def __init__(self,
                 design,
                 pivotDistBetweenWheelAndPallets,
                 pivotDistBetweenLeverAndRoller,
                 leverWidth,
                 rollerAngleRaitoToLeverAngle,
                 leverAngle,
                 impulsePinAngle,
                 balanceRollerDiamRaitoToSatefyRollerDiam,
                 holeDiam):
        self.__design = design
        self.__pivotDistBetweenWheelAndPallets = pivotDistBetweenWheelAndPallets
        self.__pivotDistBetweenLeverAndRoller = pivotDistBetweenLeverAndRoller
        self.__leverWidth = leverWidth
        self.__rollerAngleRaitoToLeverAngle = rollerAngleRaitoToLeverAngle
        self.__leverAngle = leverAngle
        self.__rollerAngle = self.__leverAngle*self.__rollerAngleRaitoToLeverAngle
        self.__impulsePinAngle = math.degrees(impulsePinAngle)
        self.__balanceRollerDiamRaitoToSatefyRollerDiam = balanceRollerDiamRaitoToSatefyRollerDiam
        self.__holeDiam = holeDiam

        self.__safetyRollerCrescentAngle = 54 # 54[deg]
        self.__forkCrotchOffset = 0.05 # 0.5[mm]

        self.__points = Points()
        self.__getPointsForDrawing()

    def draw(self):
        self.createSketches()
        self.drawLeverConstructions()
        self.drawLever()
        self.drawRollerConstructions()
        self.drawRoller()

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
        self.__leverBaseSketch = self.__leverComp.sketches.add(self.__leverComp.xYConstructionPlane)
        self.__rollerBaseSketch = self.__rollerComp.sketches.add(self.__rollerComp.xYConstructionPlane)
        self.__leverSketch =  self.__leverComp.sketches.add(self.__leverComp.xYConstructionPlane)
        self.__rollerSketch = self.__rollerComp.sketches.add(self.__rollerComp.xYConstructionPlane)

        self.__leverBaseSketch.name = "constructions"
        self.__rollerBaseSketch.name = "constructions"
        self.__leverSketch.name = "lever"
        self.__rollerSketch.name = "roller"

        self.__leverBaseSketch.isVisible = False
        self.__rollerBaseSketch.isVisible = False

        # Define a normal vector for rotation.
        self.__leverNormal = self.__leverBaseSketch.referencePlane.geometry.normal
        self.__rollerNormal = self.__rollerBaseSketch.referencePlane.geometry.normal
        self.__leverNormal.transformBy(self.__leverBaseSketch.transform)
        self.__rollerNormal.transformBy(self.__rollerBaseSketch.transform)

    def getBalanceRollerDiameter(self):
        return self.__points.A.vectorTo(self.__points.D).length*2

    def getSafetyRollerDiameter(self):
        return self.getBalanceRollerDiameter()/self.__balanceRollerDiamRaitoToSatefyRollerDiam

    def getImpulsePinDiameter(self):
        return self.__points.E.vectorTo(self.__points.G).length*2

    def getForkWidth(self):
        return self.__points.I.vectorTo(self.__points.L).length

    def getForkCrotchWidth(self):
        return self.getImpulsePinDiameter()+self.__forkCrotchOffset

    def __getPointsForDrawing(self):
        transform = adsk.core.Matrix3D.create()
        normal = adsk.core.Vector3D.create(0, 0, 1)

        self.__points.O = adsk.core.Point3D.create(0, 0, 0)
        self.__points.O.translateBy(adsk.core.Vector3D.create(0, self.__pivotDistBetweenWheelAndPallets, 0))

        self.__points.A = self.__points.O.copy()
        self.__points.A.translateBy(adsk.core.Vector3D.create(0, self.__pivotDistBetweenLeverAndRoller, 0))

        transform.setToRotation(math.radians(self.__leverAngle/2), normal, self.__points.O)
        self.__points.B = self.__points.A.copy()
        self.__points.B.transformBy(transform)

        transform.setToRotation(math.radians(-self.__rollerAngle/2), normal, self.__points.A)
        self.__points.C = self.__points.O.copy()
        self.__points.C.transformBy(transform)

        self.__points.D = self.__points.getIntersectionPoint(self.__points.O, self.__points.B, self.__points.A, self.__points.C)

        transform.setToRotation(math.radians(-self.__rollerAngle/2), normal, self.__points.A)
        self.__points.E = self.__points.A.copy()
        self.__points.E.translateBy(adsk.core.Vector3D.create(0, -self.getBalanceRollerDiameter()/2, 0))
        self.__points.E.transformBy(transform)

        transform.setToRotation(math.radians(-self.__impulsePinAngle/2), normal, self.__points.A)
        self.__points.F = self.__points.E.copy()
        self.__points.F.transformBy(transform)

        self.__points.G = self.__points.getPerpendicularProjectedPoint(self.__points.E, self.__points.A, self.__points.F)

        transform.setToRotation(math.radians(90), normal, self.__points.E)
        vector = self.__points.E.vectorTo(self.__points.B)
        vector.transformBy(transform)
        vector.normalize()
        vector.scaleBy(self.getImpulsePinDiameter()/2+self.__forkCrotchOffset/2)
        self.__points.H = self.__points.E.copy()
        self.__points.H.translateBy(vector)

        vectorAE = self.__points.A.vectorTo(self.__points.E)
        vectorAH = self.__points.A.vectorTo(self.__points.H)
        angleEAH = math.degrees(math.acos(vectorAE.dotProduct(vectorAH)/(vectorAE.length*vectorAH.length)))
        transform.setToRotation(math.radians(-self.__safetyRollerCrescentAngle/2+angleEAH), normal, self.__points.A)
        self.__points.I = self.__points.H.copy()
        self.__points.I.transformBy(transform)

        transform.setToRotation(math.radians(self.__leverAngle/2), normal, self.__points.E)
        vector = adsk.core.Vector3D.create(0, -self.getImpulsePinDiameter()/2, 0)
        vector.transformBy(transform)
        self.__points.J = self.__points.H.copy()
        self.__points.J.translateBy(vector)

        vector = self.__points.E.vectorTo(self.__points.B)
        self.__points.K = self.__points.H.copy()
        self.__points.K.translateBy(vector)

        self.__points.L = self.__points.getLineSymmetryPoint(self.__points.I, self.__points.O, self.__points.B)
        self.__points.M = self.__points.getLineSymmetryPoint(self.__points.J, self.__points.O, self.__points.B)
        self.__points.N = self.__points.getLineSymmetryPoint(self.__points.K, self.__points.O, self.__points.B)

        vector = self.__points.O.vectorTo(self.__points.E)
        scalar = vector.length-self.getImpulsePinDiameter()/2-self.__leverWidth/2
        vector.normalize()
        vector.scaleBy(scalar)
        self.__points.P = self.__points.O.copy()
        self.__points.P.translateBy(vector)

        transform.setToRotation(math.radians(self.__leverAngle/2), normal, self.__points.O)
        vector = adsk.core.Vector3D.create(-self.__leverWidth/2, 0, 0)
        vector.transformBy(transform)
        self.__points.Q = self.__points.O.copy()
        self.__points.Q.translateBy(vector)

        vector = self.__points.O.vectorTo(self.__points.P)
        self.__points.R = self.__points.Q.copy()
        self.__points.R.translateBy(vector)

        scalar = self.getForkCrotchWidth()/2+self.__leverWidth/2
        vector = self.__points.P.vectorTo(self.__points.R)
        vector.normalize()
        vector.scaleBy(scalar)
        self.__points.S = self.__points.P.copy()
        self.__points.S.translateBy(vector)

        self.__points.T = self.__points.getLineSymmetryPoint(self.__points.Q.copy(), self.__points.O, self.__points.B)
        self.__points.U = self.__points.getLineSymmetryPoint(self.__points.R.copy(), self.__points.O, self.__points.B)
        self.__points.V = self.__points.getLineSymmetryPoint(self.__points.S.copy(), self.__points.O, self.__points.B)

        transform.setToRotation(math.radians(self.__impulsePinAngle/2), normal, self.__points.A)
        self.__points.W = self.__points.E.copy()
        self.__points.W.transformBy(transform)

        transform.setToRotation(math.radians(-self.__safetyRollerCrescentAngle/2-self.__rollerAngle/2), normal, self.__points.A)
        vector = adsk.core.Vector3D.create(0, -self.getSafetyRollerDiameter()/2, 0)
        vector.transformBy(transform)
        self.__points.X = self.__points.A.copy()
        self.__points.X.translateBy(vector)

        self.__points.Y = self.__points.getLineSymmetryPoint(self.__points.X, self.__points.A, self.__points.E)

        vector = self.__points.E.vectorTo(self.__points.A)
        vector.normalize()
        vector.scaleBy(self.getImpulsePinDiameter()/2)
        self.__points.Z = self.__points.E.copy()
        self.__points.Z.translateBy(vector)

        self.__points.ZA = self.__points.getPerpendicularProjectedPoint(self.__points.Z, self.__points.A, self.__points.F)

        self.__points.ZB = self.__points.getLineSymmetryPoint(self.__points.ZA, self.__points.A, self.__points.E)

        transform.setToRotation(math.radians(-self.__rollerAngle/2), normal, self.__points.A)
        vector = adsk.core.Vector3D.create(-self.getSafetyRollerDiameter()/2, 0, 0)
        vector.transformBy(transform)
        self.__points.ZC = self.__points.A.copy()
        self.__points.ZC.translateBy(vector)

        self.__points.ZD = self.__points.getLineSymmetryPoint(self.__points.ZC, self.__points.A, self.__points.E)

    def drawLeverConstructions(self):
        sketch = self.__leverBaseSketch

        leverRootcircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.O, self.__leverWidth/2)
        leverRootcircle.isConstruction = True

        lineAO = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.O)
        lineAO.isConstruction = True

        lineOB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.B)
        lineOB.isConstruction = True

        lineAC = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.C)
        lineAC.isConstruction = True

        balanceRollerRadius = self.getBalanceRollerDiameter()/2
        balanceRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, balanceRollerRadius)
        balanceRollerCircle.isConstruction = True

        safetyRollerRadius = self.getSafetyRollerDiameter()/2
        safetyRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, safetyRollerRadius)
        safetyRollerCircle.isConstruction = True

        lineAF = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.F)
        lineAF.isConstruction = True

        sketch.sketchPoints.add(self.__points.G)

        circleE = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.E, self.getImpulsePinDiameter()/2)
        circleE.isConstruction = True

        lineEH = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.E, self.__points.H)
        lineEH.isConstruction = True

        lineAH = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.H)
        lineAH.isConstruction = True

        lineAI = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.I)
        lineAI.isConstruction = True

        lineJK = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, self.__points.K)
        lineJK.isConstruction = True

        lineIL = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.I, self.__points.L)
        lineIL.isConstruction = True

        lineJM = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, self.__points.M)
        lineJM.isConstruction = True

        lineMN = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.M, self.__points.N)
        lineMN.isConstruction = True

        lineQR = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, self.__points.R)
        lineQR.isConstruction = True

        linePS = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.P, self.__points.S)
        linePS.isConstruction = True

        lineAW = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.W)
        lineAW.isConstruction = True

    def drawRollerConstructions(self):
        sketch = self.__rollerBaseSketch

        lineAO = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.O)
        lineAO.isConstruction = True

        lineOB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.B)
        lineOB.isConstruction = True

        lineAC = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.C)
        lineAC.isConstruction = True

        balanceRollerRadius = self.getBalanceRollerDiameter()/2
        balanceRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, balanceRollerRadius)
        balanceRollerCircle.isConstruction = True

        safetyRollerRadius = self.getSafetyRollerDiameter()/2
        safetyRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, safetyRollerRadius)
        safetyRollerCircle.isConstruction = True

        lineAF = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.F)
        lineAF.isConstruction = True

        sketch.sketchPoints.add(self.__points.G)

        circleE = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.E, self.getImpulsePinDiameter()/2)
        circleE.isConstruction = True

        lineAW = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.W)
        lineAW.isConstruction = True

        lineAX = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.X)
        lineAX.isConstruction = True

        lineAY = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.Y)
        lineAY.isConstruction = True

        lineZZA = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Z, self.__points.ZA)
        lineZZA.isConstruction = True

        lineZAZB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.ZA, self.__points.ZB)
        lineZAZB.isConstruction = True

        lineZCZD = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.ZC, self.__points.ZD)
        lineZCZD.isConstruction = True

    def drawLever(self):
        sketch = self.__leverSketch

        transform = adsk.core.Matrix3D.create()
        normal = self.__leverNormal
        points = Points()

        # fork crotch
        balanceRollerRadius = self.getBalanceRollerDiameter()/2
        balanceRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, balanceRollerRadius)
        lineJK = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, self.__points.K)
        points.k = lineJK.geometry.intersectWithCurve(balanceRollerCircle.geometry).item(0)
        points.n = points.getLineSymmetryPoint(points.k, self.__points.O, self.__points.B)

        sketch.sketchCurves.sketchLines.addByTwoPoints(points.k, self.__points.J)
        sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, self.__points.M)
        sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.M, points.n)

        balanceRollerCircle.deleteMe()
        lineJK.deleteMe()

        # lever(fork) handle
        transform.setToRotation(math.radians(90), normal, self.__points.R)
        vector = self.__points.R.vectorTo(self.__points.S)
        vector.transformBy(transform)
        point = self.__points.R.copy()
        point.translateBy(vector)
        line1 = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, self.__points.R)
        line2 = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, self.__points.S)
        leverHandleFaceLeft = sketch.sketchCurves.sketchArcs.addFillet(line1, self.__points.R, line2, self.__points.R, self.getForkCrotchWidth()/2)

        transform.setToRotation(math.radians(-90), normal, self.__points.U)
        vector = self.__points.U.vectorTo(self.__points.V)
        vector.transformBy(transform)
        point = self.__points.U.copy()
        point.translateBy(vector)
        line1 = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.T, self.__points.U)
        line2 = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.U, self.__points.V)
        leverHandleFaceRight = sketch.sketchCurves.sketchArcs.addFillet(line1, self.__points.U, line2, self.__points.U, self.getForkCrotchWidth()/2)

        # fork branch
        transform.setToRotation(math.radians(10), normal, points.k)
        vector = points.k.vectorTo(self.__points.I)
        vector.scaleBy(0.5)
        vector.transformBy(transform)
        point = points.k.copy()
        point.translateBy(vector)
        controlPoints = [points.k, point, self.__points.I]
        forkBranchGuardFaceLeft = sketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

        transform.setToRotation(math.radians(-10), normal, points.n)
        vector = points.n.vectorTo(self.__points.L)
        vector.scaleBy(0.5)
        vector.transformBy(transform)
        point = points.n.copy()
        point.translateBy(vector)
        controlPoints = [points.n, point, self.__points.L]
        forkBranchGuardFaceRight = sketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

        transform.setToRotation(math.radians(10), normal, self.__points.S)
        vector1 = self.__points.J.vectorTo(points.k)
        vector1.transformBy(transform)
        point1 = self.__points.S.copy()
        point1.translateBy(vector1)
        angle = 10 if point1.vectorTo(points.getLineSymmetryPoint(point1, self.__points.O, self.__points.B)).length >= self.getForkWidth() else 20
        transform.setToRotation(math.radians(angle), normal, self.__points.S)
        vector2 = self.__points.J.vectorTo(points.k)
        vector2.transformBy(transform)
        vector2.scaleBy(2.0)
        point2 = self.__points.S.copy()
        point2.translateBy(vector2)
        controlPoints = [self.__points.S, point1, point2, self.__points.I]
        forkBranchOuterFaceLeft = sketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

        transform.setToRotation(math.radians(-10), normal, self.__points.V)
        vector1 = self.__points.M.vectorTo(points.n)
        vector1.transformBy(transform)
        point1 = self.__points.V.copy()
        point1.translateBy(vector1)
        transform.setToRotation(math.radians(-angle), normal, self.__points.V)
        vector2 = self.__points.M.vectorTo(points.n)
        vector2.transformBy(transform)
        vector2.scaleBy(2.0)
        point2 = self.__points.V.copy()
        point2.translateBy(vector2)
        controlPoints = [self.__points.V, point1, point2, self.__points.L]
        forkBranchOuterFaceRight = sketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

        _, _, point1 = forkBranchGuardFaceLeft.evaluator.getEndPoints()
        _, _, point2 = forkBranchOuterFaceLeft.evaluator.getEndPoints()
        sketch.sketchCurves.sketchArcs.addFillet(forkBranchGuardFaceLeft, point1, forkBranchOuterFaceLeft, point2, 0.01)

        _, _, point1 = forkBranchGuardFaceRight.evaluator.getEndPoints()
        _, _, point2 = forkBranchOuterFaceRight.evaluator.getEndPoints()
        sketch.sketchCurves.sketchArcs.addFillet(forkBranchGuardFaceRight, point1, forkBranchOuterFaceRight, point2, 0.01)

        # guard pin
        safetyRollerRadius = self.getSafetyRollerDiameter()/2
        safetyRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, safetyRollerRadius)
        lineOB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.B)
        points.b = lineOB.geometry.intersectWithCurve(safetyRollerCircle.geometry).item(0)

        transform.setToRotation(math.radians(-90), normal, points.b)
        points.a = self.__points.A.copy()
        points.a.transformBy(transform)
        lineba = sketch.sketchCurves.sketchLines.addByTwoPoints(points.b, points.a)
        lineMN = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.M, self.__points.N)
        points.b2 = lineba.geometry.intersectWithCurve(lineMN.geometry).item(0)
        points.b3 = points.getLineSymmetryPoint(points.b2, self.__points.O, self.__points.B)

        sketch.sketchCurves.sketchLines.addByTwoPoints(points.b, points.b2)
        sketch.sketchCurves.sketchLines.addByTwoPoints(points.b, points.b3)
        sketch.sketchCurves.sketchLines.addByTwoPoints(points.b2, points.n)
        sketch.sketchCurves.sketchLines.addByTwoPoints(points.b3, points.k)

        # lever root
        leverRootArc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.O, self.__points.Q, math.radians(180))
        leverPivotHole = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.O, self.__holeDiam/2)

        safetyRollerCircle.deleteMe()
        lineba.deleteMe()
        lineOB.deleteMe()
        lineMN.deleteMe()

    def drawRoller(self):
        sketch = self.__rollerSketch

        transform = adsk.core.Matrix3D.create()
        normal = self.__rollerNormal
        points = Points()

        # safety roller crescent
        safetyRollerRadius = self.getSafetyRollerDiameter()/2
        safetyRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, safetyRollerRadius)
        lineOB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.B)
        points.b = lineOB.geometry.intersectWithCurve(safetyRollerCircle.geometry).item(0)

        safetyRollerCircle.deleteMe()
        lineOB.deleteMe()

        point = self.__points.X.copy()
        point = points.getPerpendicularProjectedPoint(point, self.__points.A, self.__points.E)
        scalar = self.__points.E.vectorTo(points.b).length-(self.getBalanceRollerDiameter()/2-self.getSafetyRollerDiameter()/2) # in-crescent guard pin length
        vector = point.vectorTo(self.__points.A)
        vector.normalize()
        vector.scaleBy(scalar)
        point.translateBy(vector)
        sketch.sketchPoints.add(point)
        safetyRollerCresent = sketch.sketchCurves.sketchArcs.addByThreePoints(self.__points.X, point, self.__points.Y)

        # safety roller arc
        safetyRollerArc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.A, self.__points.X, math.radians(-360+self.__safetyRollerCrescentAngle))

        # impulse pin
        impulsePinArc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.A, self.__points.F, math.radians(self.__impulsePinAngle))
        impulsePinFaceLeft = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.ZA)
        impulsePinFaceRight = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.W, self.__points.ZB)

        # balance roller
        transform.setToRotation(math.radians(-self.__rollerAngle/2), normal, self.__points.A)
        vector = adsk.core.Vector3D.create(0, -0.01, 0)
        vector.transformBy(transform)
        point = self.__points.ZC.copy()
        point.translateBy(vector)
        balanceRollerFaceLeft = sketch.sketchCurves.sketchArcs.addByThreePoints(self.__points.ZC, point, self.__points.ZA)

        point = self.__points.getLineSymmetryPoint(point, self.__points.A, self.__points.E)
        balanceRollerFaceRight = sketch.sketchCurves.sketchArcs.addByThreePoints(self.__points.ZD, point, self.__points.ZB)

        rollerPivotHole = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__holeDiam/2)