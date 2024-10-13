#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math
# from distutils.util import strtobool

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''
_description = adsk.core.TextBoxCommandInput.cast(None)

_plane = adsk.core.DropDownCommandInput.cast(None)
_holeDiam = adsk.core.ValueCommandInput.cast(None)
_extendBool = adsk.core.BoolValueCommandInput.cast(None)

_numTeeth = adsk.core.TextBoxCommandInput.cast(None)
_lockingDiam = adsk.core.ValueCommandInput.cast(None)
_majorDiam = adsk.core.TextBoxCommandInput.cast(None)
_arborDistWheelToPallet = adsk.core.TextBoxCommandInput.cast(None)
_lighteningBool = adsk.core.BoolValueCommandInput.cast(None)
_wallThickness = adsk.core.ValueCommandInput.cast(None)

_arborDistLeverToRoller = adsk.core.ValueCommandInput.cast(None)
_leverWidth = adsk.core.ValueCommandInput.cast(None)
_swingAngleRaitoRollerToLever = adsk.core.ValueCommandInput.cast(None)
_leverSwingAngle = adsk.core.TextBoxCommandInput.cast(None)
_rollerSwingAngle = adsk.core.TextBoxCommandInput.cast(None)
_impulsePinAngle = adsk.core.ValueCommandInput.cast(None)
_impulsePinDiam = adsk.core.TextBoxCommandInput.cast(None)
_diamRaitoImpulsePinOrbitToSafetyRoller = adsk.core.ValueCommandInput.cast(None)
_impulsePinOrbitDiam = adsk.core.TextBoxCommandInput.cast(None)
_satefyRollerDiam = adsk.core.TextBoxCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_handlers = []


def str_to_bool(val):
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"Invalid truth value: {val}")


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        cmdDef = _ui.commandDefinitions.itemById('adskLeverEscapementPythonScript')
        if not cmdDef:
            # Create a command definition.
            cmdDef = _ui.commandDefinitions.addButtonDefinition(
                'adskLeverEscapementPythonScript',
                'Lever Escapement',
                'Create components of an escape wheel, a pallet fork, and a safety roller.', 'resources/LeverEscapement'
            )

        # Connect to the command created event.
        onCommandCreated = commandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command.
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class commandCreatedHandler(adsk.core.CommandCreatedEventHandler):
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
            plane = 'X-Y plane'
            planeAttrib = des.attributes.itemByName('LeverEscapement', 'plane')
            if planeAttrib:
                plane = planeAttrib.value

            holeDiam = '0.19' # 0.19[cm] = 1.9[mm]
            holeDiamAttrib = des.attributes.itemByName('LeverEscapement', 'holeDiam')
            if holeDiamAttrib:
                holeDiam = holeDiamAttrib.value

            extendBool = True
            extendBoolAttrib = des.attributes.itemByName('LeverEscapement', 'extendBool')
            if extendBoolAttrib:
                extendBool = True if str_to_bool(extendBoolAttrib.value) == 1 else False

            numTeeth = '15'

            lockingDiam = '4' # 4[cm] = 40.0[mm]
            lockingDiamAttrib = des.attributes.itemByName('LeverEscapement', 'lockingDiam')
            if lockingDiamAttrib:
                lockingDiam = lockingDiamAttrib.value

            lighteningBool = True
            lighteningBoolAttrib = des.attributes.itemByName('LeverEscapement', 'lighteningBool')
            if lighteningBoolAttrib:
                lighteningBool = True if str_to_bool(lighteningBoolAttrib.value) == 1 else False

            wallThickness = '0.2'
            wallThicknessAttrib = des.attributes.itemByName('LeverEscapement', 'wallThickness')
            if wallThicknessAttrib:
                wallThickness = wallThicknessAttrib.value

            leverWidth = '0.4'
            leverWidthAttrib = des.attributes.itemByName('LeverEscapement', 'leverWidth')
            if leverWidthAttrib:
                leverWidth = leverWidthAttrib.value

            swingAngleRaitoRollerToLever = '3'
            swingAngleRaitoRollerToLeverAttrib = des.attributes.itemByName('LeverEscapement', 'swingAngleRaitoRollerToLever')
            if swingAngleRaitoRollerToLeverAttrib:
                swingAngleRaitoRollerToLever = swingAngleRaitoRollerToLeverAttrib.value

            leverSwingAngle = '10.0'

            rollerSwingAngle = str(float(leverSwingAngle)*float(swingAngleRaitoRollerToLever))

            impulsePinAngle = '12.0'
            impulsePinAngleAttrib = des.attributes.itemByName('LeverEscapement', 'impulsePinAngle')
            if impulsePinAngleAttrib:
                impulsePinAngle = impulsePinAngleAttrib.value

            diamRaitoImpulsePinOrbitToSafetyRoller = '2.0'
            diamRaitoImpulsePinOrbitToSafetyRollerAttrib = des.attributes.itemByName('LeverEscapement', 'diamRaitoImpulsePinOrbitToSafetyRoller')
            if diamRaitoImpulsePinOrbitToSafetyRollerAttrib:
                diamRaitoImpulsePinOrbitToSafetyRoller = diamRaitoImpulsePinOrbitToSafetyRollerAttrib.value

            # Define the default values based on caluculated points.
            commonParams = {
                'design': des,
                'plane' : plane,
                'holeDiam' : float(holeDiam),
                'leverWidth': float(leverWidth),
                'leverSwingAngle': float(leverSwingAngle),
                'extendBool' : extendBool,
            }

            wheelAndPallet = WheelAndPallet(int(numTeeth), float(lockingDiam), lighteningBool, float(wallThickness), **commonParams)

            arborDistWheelToPallet = str(round(wheelAndPallet.getArborDistance()*10, 3))

            arborDistLeverToRoller = str(wheelAndPallet.getArborDistance())
            arborDistLeverToRollerAttrib = des.attributes.itemByName('LeverEscapement', 'arborDistLeverToRoller')
            if arborDistLeverToRollerAttrib:
                arborDistLeverToRoller = arborDistLeverToRollerAttrib.value

            leverAndRoller = LeverAndRoller(float(arborDistWheelToPallet),
                                            float(arborDistLeverToRoller),
                                            float(swingAngleRaitoRollerToLever),
                                            math.radians(float(impulsePinAngle)),
                                            float(diamRaitoImpulsePinOrbitToSafetyRoller),
                                            **commonParams)

            majorDiam = str(round(wheelAndPallet.getWheelMajorDiameter()*10, 3))

            impulsePinOrbitDiam = str(round(leverAndRoller.getImpulsePinOrbitDiameter()*10, 3))

            satefyRollerDiam = str(round(leverAndRoller.getImpulsePinOrbitDiameter()*10/float(diamRaitoImpulsePinOrbitToSafetyRoller), 3))

            impulsePinDiam = str(round(leverAndRoller.getImpulsePinDiameter()*10, 3))

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            global _description
            global _plane, _holeDiam, _extendBool
            global _numTeeth, _lockingDiam, _majorDiam, _lighteningBool, _wallThickness
            global _arborDistWheelToPallet, _arborDistLeverToRoller, _leverWidth
            global _swingAngleRaitoRollerToLever, _leverSwingAngle, _rollerSwingAngle
            global _impulsePinAngle, _impulsePinDiam
            global _diamRaitoImpulsePinOrbitToSafetyRoller, _impulsePinOrbitDiam, _satefyRollerDiam
            global _errMessage

            # Define the command dialog.
            ## For Common settings
            _description = inputs.addTextBoxCommandInput('description', '', '<br><b>Common settings:</b>', 2, True)
            _description.isFullWidth = True

            _plane = inputs.addDropDownCommandInput('plane', 'Sketch plane', adsk.core.DropDownStyles.TextListDropDownStyle)
            if plane == 'X-Y plane':
                _plane.listItems.add('X-Y plane', True)
                _plane.listItems.add('X-Z plane', False)
                _plane.listItems.add('Y-Z plane', False)
            elif plane == 'X-Z plane':
                _plane.listItems.add('X-Y plane', False)
                _plane.listItems.add('X-Z plane', True)
                _plane.listItems.add('Y-Z plane', False)
            elif plane == 'Y-Z plane':
                _plane.listItems.add('X-Y plane', False)
                _plane.listItems.add('X-Z plane', False)
                _plane.listItems.add('Y-Z plane', True)

            _holeDiam = inputs.addValueInput('holeDiam', 'Diameter of the hole for arbor', _units, adsk.core.ValueInput.createByReal(float(holeDiam)))

            _extendBool = inputs.addBoolValueInput('extendBool', 'Extend the lever swing angle for 3D printing', True, '', extendBool)

            ## For Wheel and Pallet
            _description = inputs.addTextBoxCommandInput('description', '', '<br><b>The Escape wheel and the Pallet:</b>', 2, True)
            _description.isFullWidth = True

            _numTeeth = inputs.addTextBoxCommandInput('numTeeth', 'Number of the Escape wheel teeth', numTeeth, 1, True)

            _lockingDiam = inputs.addValueInput('lockingDiam', 'Locking diameter', _units, adsk.core.ValueInput.createByReal(float(lockingDiam)))

            _majorDiam = inputs.addTextBoxCommandInput('majorDiam', 'Major diameter [mm]', majorDiam, 1, True)

            _arborDistWheelToPallet = inputs.addTextBoxCommandInput('arborDistWheelToPallet', 'Arbor distance (Escape wheel to Pallet) [mm]', arborDistWheelToPallet, 1, True)

            _lighteningBool = inputs.addBoolValueInput('lighteningBool', 'Lightening the wheel', True, '', lighteningBool)

            _wallThickness = inputs.addValueInput('wallThickness', 'Thickness of the wall', _units, adsk.core.ValueInput.createByReal(float(wallThickness)))
            _wallThickness.isEnabled = True if lighteningBool == True else False

            ## For Lever and Roller
            _description = inputs.addTextBoxCommandInput('description', '', '<br><b>The Lever and the Safety roller:</b>', 2, True)
            _description.isFullWidth = True

            _arborDistLeverToRoller = inputs.addValueInput('arborDistLeverToRoller', 'Arbor distance (Lever to Safety roller)', _units, adsk.core.ValueInput.createByReal(float(arborDistLeverToRoller)))

            _leverWidth = inputs.addValueInput('leverWidth', 'Lever width', _units, adsk.core.ValueInput.createByReal(float(leverWidth)))

            _swingAngleRaitoRollerToLever = inputs.addValueInput('swingAngleRaitoRollerToLever', 'Swing angle raito (Safety roller to Lever)', '', adsk.core.ValueInput.createByReal(float(swingAngleRaitoRollerToLever)))

            _rollerSwingAngle = inputs.addTextBoxCommandInput('rollerSwingAngle', 'Swing angle of Safety roller [deg]', rollerSwingAngle, 1, True)

            _leverSwingAngle = inputs.addTextBoxCommandInput('leverSwingAngle', 'Swing angle of Lever [deg]', leverSwingAngle, 1, True)

            _impulsePinAngle = inputs.addValueInput('impulsePinAngle', 'Impulse pin angle', 'deg', adsk.core.ValueInput.createByReal(math.radians(float(impulsePinAngle))))

            _impulsePinDiam = inputs.addTextBoxCommandInput('impulsePinDiam', 'Impulse pin diameter [mm]', impulsePinDiam, 1, True)

            _diamRaitoImpulsePinOrbitToSafetyRoller = inputs.addValueInput('diamRaitoImpulsePinOrbitToSafetyRoller', 'Diameter raito (Impulse pin orbit to Safety roller)', '', adsk.core.ValueInput.createByReal(float(diamRaitoImpulsePinOrbitToSafetyRoller)))

            _impulsePinOrbitDiam = inputs.addTextBoxCommandInput('impulsePinOrbitDiam', 'Diameter of Impulse pin orbit [mm]', impulsePinOrbitDiam, 1, True)

            _satefyRollerDiam = inputs.addTextBoxCommandInput('satefyRollerDiam', 'Diameter of Safety roller [mm]', satefyRollerDiam, 1, True)

            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

            # Connect to the command related events.
            # onExecute = commandExecuteHandler()
            # cmd.execute.add(onExecute)
            # _handlers.append(onExecute)

            onExecutePreview = commandExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            _handlers.append(onExecutePreview)

            onInputChanged = commandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            # onValidateInputs = commandValidateInputsHandler()
            # cmd.validateInputs.add(onValidateInputs)
            # _handlers.append(onValidateInputs)
            ## TBA

            onDestroy = commandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class commandDestroyHandler(adsk.core.CommandEventHandler):
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


# Event handler for the execute event.
class commandExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            attribs.add('LeverEscapement', 'plane', _plane.selectedItem.name)
            attribs.add('LeverEscapement', 'holeDiam', str(_holeDiam.value))
            attribs.add('LeverEscapement', 'extendBool', str(_extendBool.value))
            # attribs.add('LeverEscapement', 'numTeeth', _numTeeth.text)
            attribs.add('LeverEscapement', 'lockingDiam', str(_lockingDiam.value))
            attribs.add('LeverEscapement', 'lighteningBool', str(_lighteningBool.value))
            attribs.add('LeverEscapement', 'wallThickness', str(_wallThickness.value))
            attribs.add('LeverEscapement', 'arborDistLeverToRoller', str(_arborDistLeverToRoller.value))
            attribs.add('LeverEscapement', 'leverWidth', str(_leverWidth.value))
            attribs.add('LeverEscapement', 'swingAngleRaitoRollerToLever', str(_swingAngleRaitoRollerToLever.value))
            # attribs.add('LeverEscapement', 'leverSwingAngle', _leverSwingAngle.text)
            attribs.add('LeverEscapement', 'impulsePinAngle', str(math.degrees(_impulsePinAngle.value)))
            attribs.add('LeverEscapement', 'diamRaitoImpulsePinOrbitToSafetyRoller', str(_diamRaitoImpulsePinOrbitToSafetyRoller.value))

            plane = _plane.selectedItem.name
            holeDiam = _holeDiam.value
            extendBool = _extendBool.value
            numTeeth = int(_numTeeth.text)
            lockingDiam = _lockingDiam.value
            lighteningBool = _lighteningBool.value
            wallThickness = _wallThickness.value
            arborDistLeverToRoller = _arborDistLeverToRoller.value
            leverWidth = _leverWidth.value
            swingAngleRaitoRollerToLever = _swingAngleRaitoRollerToLever.value
            leverSwingAngle = float(_leverSwingAngle.text)
            impulsePinAngle = _impulsePinAngle.value
            diamRaitoImpulsePinOrbitToSafetyRoller = _diamRaitoImpulsePinOrbitToSafetyRoller.value

            commonParams = {
                'design': des,
                'plane': plane,
                'holeDiam': holeDiam,
                'leverWidth': leverWidth,
                'leverSwingAngle': leverSwingAngle,
                'extendBool': extendBool,
            }

            wheelAndPallet = WheelAndPallet(numTeeth, lockingDiam, lighteningBool, wallThickness, **commonParams)
            wheelAndPallet.draw()

            arborDistWheelToPallet = wheelAndPallet.getArborDistance()
            leverAndRoller = LeverAndRoller(arborDistWheelToPallet,
                                            arborDistLeverToRoller,
                                            swingAngleRaitoRollerToLever,
                                            impulsePinAngle,
                                            diamRaitoImpulsePinOrbitToSafetyRoller,
                                            **commonParams)
            leverAndRoller.draw()

            args.isValidResult = True

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the inputChanged event.
class commandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            des = adsk.fusion.Design.cast(_app.activeProduct)
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            try:
                commonParams = {
                    'design': des,
                    'plane': _plane.selectedItem.name,
                    'holeDiam' : _holeDiam.value,
                    'leverWidth': _leverWidth.value,
                    'leverSwingAngle': float(_leverSwingAngle.text),
                    'extendBool' : _extendBool.value,
                }

                if changedInput.id == 'lighteningBool':
                    if _lighteningBool.value:
                        _wallThickness.isEnabled = True
                    else:
                        _wallThickness.isEnabled = False

                if changedInput.id == 'lockingDiam':
                    wheelAndPallet = WheelAndPallet(int(_numTeeth.text), _lockingDiam.value, _lighteningBool.value, _wallThickness.value, **commonParams)
                    arborDistWheelToPallet = wheelAndPallet.getArborDistance()

                    _majorDiam.text = str(round(wheelAndPallet.getWheelMajorDiameter()*10, 3))
                    _arborDistWheelToPallet.text = str(round(arborDistWheelToPallet*10, 3))
                    _arborDistLeverToRoller.value = arborDistWheelToPallet
                else:
                    arborDistWheelToPallet = float(_arborDistWheelToPallet.text)

                leverAndRoller = LeverAndRoller(arborDistWheelToPallet,
                                                _arborDistLeverToRoller.value,
                                                _swingAngleRaitoRollerToLever.value,
                                                _impulsePinAngle.value,
                                                _diamRaitoImpulsePinOrbitToSafetyRoller.value,
                                                **commonParams)

                _rollerSwingAngle.text = str(float(_leverSwingAngle.text)*_swingAngleRaitoRollerToLever.value)
                _impulsePinDiam.text = str(round(leverAndRoller.getImpulsePinDiameter()*10, 3))
                _impulsePinOrbitDiam.text = str(round(leverAndRoller.getImpulsePinOrbitDiameter()*10, 3))
                _satefyRollerDiam.text = str(round(leverAndRoller.getImpulsePinOrbitDiameter()*10/_diamRaitoImpulsePinOrbitToSafetyRoller.value, 3))

            except:
                pass

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# # Event handler for the validateInputs event.
# class commandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
#     def __init__(self):
#         super().__init__()
#     def notify(self, args):
#         try:
#             ## TBA


class Points:
    def __init__(self):
        pass


class Utilites:
    def __init__(self):
        pass

    def __getComponentByName(self, component, name):
        if component.name == name:
            return component

        for child in component.occurrences:
            found = self.__getComponentByName(child.component, name)
            if found:
                return found

        return None

    def getComponentByName(self, design, name):
        component = design.rootComponent
        return self.__getComponentByName(component, name)

    def createComponent(self, design):
        occs = design.rootComponent.occurrences
        occ = occs.addNewComponent(adsk.core.Matrix3D.create())
        comp = adsk.fusion.Component.cast(occ.component)
        return comp

    def createComponentToParent(self, parentComp):
        occs = parentComp.occurrences
        occ = occs.addNewComponent(adsk.core.Matrix3D.create())
        comp = adsk.fusion.Component.cast(occ.component)
        return comp

    def createSketch(self, component, planeParam):
        if planeParam == 'X-Y plane':
            sketchPlane = component.xYConstructionPlane
        elif planeParam == 'X-Z plane':
            sketchPlane = component.xZConstructionPlane
        elif planeParam == 'Y-Z plane':
            sketchPlane = component.yZConstructionPlane

        sketch = component.sketches.add(sketchPlane)
        return sketch

    def getPlaneNormal(self, planeParam):
        if planeParam == 'X-Y plane':
            normal = adsk.core.Vector3D.create(0, 0, 1)
        elif planeParam == 'X-Z plane':
            normal = adsk.core.Vector3D.create(0, -1, 0)
        elif planeParam == 'Y-Z plane':
            normal = adsk.core.Vector3D.create(-1, 0, 0)

        return normal

    def getWorldNormal(self, sketch, normal):
        normal.transformBy(sketch.transform)
        return normal

    def addVectors(self, vector1, vector2):
        x = vector1.x + vector2.x
        y = vector1.y + vector2.y
        z = vector1.z + vector2.z
        vector = adsk.core.Vector3D.create(x, y, z)
        return vector

    def getMiddlePoint(self, startPoint, endPoint):
        vectorStoE = startPoint.vectorTo(endPoint)
        vectorStoE.scaleBy(0,5)

        midPoint = startPoint.copy()
        midPoint.translateBy(vectorStoE)
        return midPoint

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

        scalar = dotProduct / vectorStoE.length
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

    def getThreePointsAngle(self, startPoint, vertexPoint, endPoint):
        vectorVtoS = vertexPoint.vectorTo(startPoint)
        vectorVtoE = vertexPoint.vectorTo(endPoint)

        angle = vectorVtoS.dotProduct(vectorVtoE) / (vectorVtoS.length*vectorVtoE.length)
        angle = math.degrees(math.acos(angle))
        return angle


class CommonDrawingPrameters:
    def __init__(self, design, plane, holeDiam, leverWidth, leverSwingAngle, extendBool):
        self.__design = design
        self.__plane = plane
        self.__leverWidth = leverWidth
        self.__leverSwingAngle = leverSwingAngle
        self.__holeDiam = holeDiam
        self.__extendBool = extendBool
        self.__bankingPinOffset = 1.0 # [deg]
        self.__bankingPinOffsetForExtension = 2.0 #[deg]

    def getDesign(self):
        return self.__design

    def getPlane(self):
        return self.__plane

    def getArborHoleDiam(self):
        return self.__holeDiam

    def getLeverWidth(self):
        return self.__leverWidth

    def getLeverSwingAngle(self):
        return self.__leverSwingAngle

    def getExtendBool(self):
        return self.__extendBool

    def getBankingPinOffset(self):
        return self.__bankingPinOffset

    def getBankingPinOffsetForExtension(self):
        return self.__bankingPinOffsetForExtension


class WheelAndPallet(CommonDrawingPrameters):
    def __init__(self,
                 numTeeth,
                 lockingDiam,
                 lighteningBool,
                 wallThickness,
                 **commonParameters):

        super().__init__(**commonParameters)
        self.__numTeeth = numTeeth
        self.__lockingDiam = lockingDiam
        self.__lighteningBool = lighteningBool
        self.__wallThicknessForLightening = wallThickness

        self.__rootDiamOfTeeth = self.__lockingDiam*2/3
        self.__angleForPalletArmStartPoint = 10 # [deg]

        self.__outerDiamForLightening = self.__rootDiamOfTeeth - self.__wallThicknessForLightening*2
        self.__innerDiamForLightening = self.getArborHoleDiam() + self.__wallThicknessForLightening*2

        self.__points = Points()
        self.__utils = Utilites()
        self.__getPointsForDrawing()

    def draw(self):
        self.createWheelComponent()
        self.createPalletComponent()
        self.createWheelSketch()
        self.createPalletSketch()
        self.drawWheelConstructions()
        self.drawWheel()
        self.drawPalletConstructions()
        self.drawPallet()

    def createWheelComponent(self):
        self.__wheelComp = self.__utils.createComponent(self.getDesign())
        if self.__lighteningBool:
            self.__wheelComp.name = 'EscapeWheel' + '_lockingDiam' + str(round(self.__lockingDiam*10,2)) + '_wallThickness' + str(round(self.__wallThicknessForLightening*10,2))
        else:
            self.__wheelComp.name = 'EscapeWheel' + '_lockingDiam' + str(round(self.__lockingDiam*10,2))

    def createPalletComponent(self):
        self.__palletForkComp = self.__utils.getComponentByName(self.getDesign(), 'PalletFork') or self.__utils.createComponent(self.getDesign())
        self.__palletForkComp.name = 'PalletFork'

        self.__palletComp = self.__utils.createComponentToParent(self.__palletForkComp)
        if self.getExtendBool():
            self.__palletComp.name = 'Pallet' + '_extendedSwingAngle' + str(round(self.getBankingPinOffsetForExtension(),2))
        else:
            self.__palletComp.name = 'Pallet'

    def createWheelSketch(self):
        self.__wheelConstructionSketch = self.__utils.createSketch(self.__wheelComp, self.getPlane())
        self.__wheelSketch = self.__utils.createSketch(self.__wheelComp, self.getPlane())
        self.__wheelConstructionSketch.name = 'Constructions'
        self.__wheelSketch.name = 'Escape wheel'
        self.__wheelConstructionSketch.isVisible = False

    def createPalletSketch(self):
        self.__palletConstructionSketch = self.__utils.createSketch(self.__palletComp, self.getPlane())
        self.__palletSketch = self.__utils.createSketch(self.__palletComp, self.getPlane())
        self.__palletConstructionSketch.name = 'Constructions'
        self.__palletSketch.name = 'Pallet'
        self.__palletConstructionSketch.isVisible = False

    def getArborDistance(self):
        return (self.__lockingDiam/2.0)/math.cos(math.radians(30.0))

    def getWheelMajorDiameter(self):
        return self.__points.A.vectorTo(self.__points.J).length*2

    def __getPointsForDrawing(self):
        transform = adsk.core.Matrix3D.create()
        normal = adsk.core.Vector3D.create(0, 0, 1)

        # Get points according to the figure (in Page.223, No.468) and descriptions in the book 'WATCHMAKING'.
        self.__points.A = adsk.core.Point3D.create(0, 0, 0) # Wheel arbor

        vector = adsk.core.Vector3D.create(0, self.getArborDistance(), 0)
        self.__points.O = self.__points.A.copy()
        self.__points.O.translateBy(vector) # Pallet arbor

        transform.setToRotation(math.radians(-60), normal, self.__points.O)
        self.__points.D = self.__points.A.copy()
        self.__points.D.transformBy(transform)

        transform.setToRotation(math.radians(60), normal, self.__points.O)
        self.__points.E = self.__points.A.copy()
        self.__points.E.transformBy(transform)

        transform.setToRotation(math.radians(31), normal, self.__points.A)
        self.__points.B = self.__points.O.copy()
        self.__points.B.transformBy(transform)

        transform.setToRotation(math.radians(-29), normal, self.__points.A)
        self.__points.C = self.__points.O.copy()
        self.__points.C.transformBy(transform)

        transform.setToRotation(math.radians(-7), normal, self.__points.A)
        self.__points.T = self.__points.C.copy()
        self.__points.T.transformBy(transform)

        transform.setToRotation(math.radians(-4), normal, self.__points.A)
        self.__points.Y = self.__points.T.copy()
        self.__points.Y.transformBy(transform)

        transform.setToRotation(math.radians(8), normal, self.__points.O)
        self.__points.__F = self.__points.E.copy()
        self.__points.__F.transformBy(transform) # temporary F

        transform.setToRotation(math.radians(2), normal, self.__points.O)
        self.__points.K = self.__points.__F.copy()
        self.__points.K.transformBy(transform)

        transform.setToRotation(math.radians(-29), normal, self.__points.A.copy())
        vector = adsk.core.Vector3D.create(0, self.__lockingDiam/2, 0)
        vector.transformBy(transform)
        self.__points.L = self.__points.A.copy()
        self.__points.L.translateBy(vector)

        angle = self.__utils.getThreePointsAngle(self.__points.E, self.__points.O, self.__points.L)
        transform.setToRotation(math.radians(10+angle), normal, self.__points.O)
        self.__points.__G = self.__points.L.copy()
        self.__points.__G.transformBy(transform) # temporary G

        scalar = self.__points.O.vectorTo(self.__points.__G).length/math.cos(math.radians(2.0))
        vector = self.__points.O.vectorTo(self.__points.__F)
        vector.normalize()
        vector.scaleBy(scalar)
        self.__points.F = self.__points.O.copy()
        self.__points.F.translateBy(vector)

        vector = self.__points.F.vectorTo(self.__points.__G)
        scalar = self.__points.L.vectorTo(self.__points.C).length*1.5
        vector.normalize()
        vector.scaleBy(scalar)
        self.__points.G = self.__points.F.copy()
        self.__points.G.translateBy(vector)

        vector = self.__points.A.vectorTo(self.__points.Y)
        vector.normalize()
        vector.scaleBy(self.__lockingDiam/2)
        self.__points.a = self.__points.A.copy()
        self.__points.a.translateBy(vector)

        self.__points.J = self.__utils.getIntersectionPoint(self.__points.A, self.__points.T, self.__points.F, self.__points.a)

        transform.setToRotation(math.radians(-7), normal, self.__points.A)
        self.__points.M = self.__points.B.copy()
        self.__points.M.transformBy(transform)

        transform.setToRotation(math.radians(4), normal, self.__points.A)
        self.__points.__N = self.__points.B.copy()
        self.__points.__N.transformBy(transform) # temporary N

        vector = self.__points.A.vectorTo(self.__points.__N)
        vector.normalize()
        vector.scaleBy(self.getWheelMajorDiameter()/2)
        self.__points.N = self.__points.A.copy()
        self.__points.N.translateBy(vector)

        self.__points.V = self.__utils.getIntersectionPoint(self.__points.O, self.__points.D, self.__points.A, self.__points.M)

        transform.setToRotation(math.radians(10), normal, self.__points.O)
        self.__points.P = self.__points.V.copy()
        self.__points.P.transformBy(transform)

        self.__points.__P = self.__points.D.copy()
        self.__points.__P.transformBy(transform) # for construction drawing

        self.__points.R = self.__utils.getIntersectionPoint(self.__points.O, self.__points.D, self.__points.A, self.__points.B)

        transform.setToRotation(math.radians(90), normal, self.__points.R)
        scalar = self.__points.R.vectorTo(self.__points.B).length*1.5
        vector = self.__points.R.vectorTo(self.__points.O)
        vector.normalize()
        vector.scaleBy(scalar)
        vector.transformBy(transform)
        self.__points.W = self.__points.R.copy()
        self.__points.W.translateBy(vector)

        transform.setToRotation(math.radians(-13.5), normal, self.__points.R)
        self.__points.__W = self.__utils.getLineSymmetryPoint(self.__points.W, self.__points.O, self.__points.D)
        self.__points.__W.transformBy(transform)

        transform.setToRotation(math.radians(2), normal, self.__points.O)
        self.__points.__Q = self.__points.D.copy()
        self.__points.__Q.transformBy(transform) # temporary Q

        self.__points.Q = self.__utils.getIntersectionPoint(self.__points.R, self.__points.__W, self.__points.__Q, self.__points.O)

        transform.setToRotation(math.radians(-24), normal, self.__points.R)
        self.__points.X = self.__points.A.copy()
        self.__points.X.transformBy(transform)

        # Get points for drawing detaild pallet (these are out of the description in 'WATCHMAKING')
        transform.setToRotation(math.radians(-13.5), normal, self.__points.R)
        scalar = self.__points.R.vectorTo(self.__points.O).length
        vector = self.__points.R.vectorTo(self.__points.W)
        vector.normalize()
        vector.scaleBy(scalar)
        vector.transformBy(transform)
        self.__points.ZB = self.__points.Q.copy()
        self.__points.ZB.translateBy(vector)

        self.__points.ZA = self.__points.P.copy()
        self.__points.ZA.translateBy(vector)

        transform.setToRotation(math.radians(-15), normal, self.__points.F)
        scalar = self.__points.F.vectorTo(self.__points.O).length
        vector = self.__points.F.vectorTo(self.__points.__G)
        vector.normalize()
        vector.scaleBy(scalar)
        vector.transformBy(transform)
        self.__points.ZC = self.__points.F.copy()
        self.__points.ZC.translateBy(vector)

        self.__points.ZD = self.__points.J.copy()
        self.__points.ZD.translateBy(vector)

        transform.setToRotation(math.radians(self.getLeverSwingAngle()/2-self.__angleForPalletArmStartPoint), normal, self.__points.O)
        vector = adsk.core.Vector3D.create(0, -self.getLeverWidth()/2, 0)
        vector.transformBy(transform)
        self.__points.ZE = self.__points.O.copy()
        self.__points.ZE.translateBy(vector)

        transform.setToRotation(math.radians(self.getLeverSwingAngle()/2+self.__angleForPalletArmStartPoint), normal, self.__points.O)
        vector = adsk.core.Vector3D.create(0, -self.getLeverWidth()/2, 0)
        vector.transformBy(transform)
        self.__points.ZF = self.__points.O.copy()
        self.__points.ZF.translateBy(vector)

        # Get points for drawing pallet's extenstion (Due to insufficient accuracy in 3D printing, We extend the pallet stones to ensure that the lock can operate).
        if self.getExtendBool():
            # For entry pallet
            transform.setToRotation(math.radians(self.getBankingPinOffsetForExtension()), normal, self.__points.O)
            self.__points.__extP = self.__points.__P.copy()
            self.__points.__extP.transformBy(transform)

            angle = self.__utils.getThreePointsAngle(self.__points.__P, self.__points.P, self.__points.ZA)
            transform.setToRotation(math.radians(180-angle), normal, self.__points.P)
            self.__points.expP = self.__points.__P.copy()
            self.__points.expP.transformBy(transform)

            self.__points.extP = self.__utils.getIntersectionPoint(self.__points.O, self.__points.__extP, self.__points.P, self.__points.expP)

            vector = self.__points.P.vectorTo(self.__points.extP)
            self.__points.extQ = self.__points.Q.copy()
            self.__points.extQ.translateBy(vector)

            # For exit pallet
            transform.setToRotation(math.radians(-self.getBankingPinOffsetForExtension()), normal, self.__points.O)
            self.__points.__extF = self.__points.__F.copy()
            self.__points.__extF.transformBy(transform)

            transform.setToRotation(math.radians(180), normal, self.__points.F)
            self.__points.__ZC = self.__points.ZC.copy()
            self.__points.__ZC.transformBy(transform)

            self.__points.extF = self.__utils.getIntersectionPoint(self.__points.O, self.__points.__extF, self.__points.ZC, self.__points.__ZC)

            vector = self.__points.F.vectorTo(self.__points.extF)
            self.__points.extJ = self.__points.J.copy()
            self.__points.extJ.translateBy(vector)

    def drawWheelConstructions(self):
        sketch = self.__wheelConstructionSketch

        lineAO = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.O)
        lineAO.isConstruction = True

        lockingCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__lockingDiam/2)
        lockingCircle.isConstruction = True

        lineOD = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.D)
        lineOD.isConstruction = True

        lineOE = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.E)
        lineOE.isConstruction = True

        lineAC = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.C)
        lineAC.isConstruction = True

        lineAT = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.T)
        lineAT.isConstruction = True

        lineAY = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.Y)
        lineAY.isConstruction = True

        lineOK = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.K)
        lineOK.isConstruction = True

        arcHL = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.O, self.__points.L, math.radians(30))
        arcHL.isConstruction = True

        lineOL = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.L)
        lineOL.isConstruction = True

        # lineOF = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.F)
        # lineOF.isConstruction = True
        pointF = sketch.sketchPoints.add(self.__points.F)

        __lineOF = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.__F)
        __lineOF.isConstruction = True

        lineFG = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.G)
        lineFG.isConstruction = True

        lineFa = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.a)
        lineFa.isConstruction = True

        pointJ = sketch.sketchPoints.add(self.__points.J)

        wheelMajorCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getWheelMajorDiameter()/2)
        wheelMajorCircle.isConstruction = True

        lineAB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.B)
        lineAB.isConstruction = True

        lineAM = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.M)
        lineAM.isConstruction = True

        lineAN = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.N)
        lineAN.isConstruction = True

        arcVP = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.O, self.__points.V, math.radians(30))
        arcVP.isConstruction = True

        # lineOP = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.P)
        # lineOP.isConstruction = True
        pointP = sketch.sketchPoints.add(self.__points.P)

        __lineOP = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.__P)
        __lineOP.isConstruction = True

        lineRW = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, self.__points.W)
        lineRW.isConstruction = True

        # lineOQ = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.Q)
        # lineOQ.isConstruction = True
        pointQ = sketch.sketchPoints.add(self.__points.Q)

        __lineOQ = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.__Q)
        __lineOQ.isConstruction = True

        linePQ = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.P, self.__points.Q)
        linePQ.isConstruction = True

        lineQR = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, self.__points.R)
        lineQR.isConstruction = True

        lineRX = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, self.__points.X)
        lineRX.isConstruction = True

        teethRootCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__rootDiamOfTeeth/2)
        teethRootCircle.isConstruction = True

    def drawPalletConstructions(self):
        sketch = self.__palletConstructionSketch

        palletArborCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.O, self.getArborHoleDiam()/2)
        palletArborCircle.isConstruction = True

        leverWidthCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.O, self.getLeverWidth()/2)
        leverWidthCircle.isConstruction = True

        linePQ = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.P, self.__points.Q)
        linePQ.isConstruction = True

        linePZA = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.P, self.__points.ZA)
        linePZA.isConstruction = True

        lineQZB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, self.__points.ZB)
        lineQZB.isConstruction = True

        lineFJ = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.J)
        lineFJ.isConstruction = True

        lineFZC = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.ZC)
        lineFZC.isConstruction = True

        lineJZD = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, self.__points.ZD)
        lineJZD.isConstruction = True

        lineOZE = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.ZE)
        lineOZE.isConstruction = True

        lineOZF = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.ZF)
        lineOZF.isConstruction = True

        # pointZG = sketch.sketchPoints.add(self.__points.ZF)
        # pointZH = sketch.sketchPoints.add(self.__points.ZH)

    def drawWheel(self):
        sketch = self.__wheelSketch
        normal = self.__utils.getPlaneNormal(self.getPlane())
        normal = self.__utils.getWorldNormal(sketch, normal)

        transform = adsk.core.Matrix3D.create()
        points = Points()

        # Wheel arbor
        wheelArborHole  = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getArborHoleDiam()/2)

        # Incline face of wheel teeth
        wheelTeethInclineFace = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.N, self.__points.R)

        # Locking face of wheel teeth
        teethRootCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__rootDiamOfTeeth/2)
        lineRX = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, self.__points.X)

        points.x = lineRX.geometry.intersectWithCurve(teethRootCircle.geometry).item(0)
        wheelTeethLockingFace = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, points.x)

        teethRootCircle.deleteMe()
        lineRX.deleteMe()

        # Copy incline/locking faces and draw another face of wheel theeth by them.
        inputEntities = adsk.core.ObjectCollection.create()
        inputEntities.add(wheelTeethInclineFace)
        inputEntities.add(wheelTeethLockingFace)

        for i in range(1, 16):
            transform.setToRotation(math.radians(360/self.__numTeeth), normal, self.__points.A)
            copiedEntities = sketch.copy(inputEntities, transform)
            copiedSketchLine = [entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)]

            originInclineFace = inputEntities.item(0)
            copiedInclineFace = copiedSketchLine[0]
            copiedLockingFace = copiedSketchLine[1]

            controlPoints = [originInclineFace.geometry.startPoint, originInclineFace.geometry.endPoint, copiedLockingFace.geometry.endPoint]
            wheelTeethAnotherFace = sketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

            _, startPoint, _ = wheelTeethAnotherFace.evaluator.getEndPoints()
            sketch.sketchCurves.sketchArcs.addFillet(wheelTeethAnotherFace, startPoint, originInclineFace, originInclineFace.geometry.startPoint, 0.005)

            if i == 15:
                # Delete dupulicated lines.
                copiedInclineFace.deleteMe()
                copiedLockingFace.deleteMe()
            else:
                inputEntities = adsk.core.ObjectCollection.create()
                inputEntities.add(copiedInclineFace)
                inputEntities.add(copiedLockingFace)

        # Drawing for lightening
        if self.__lighteningBool:
            innerLighteningCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__innerDiamForLightening/2)
            outerLighteningCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__outerDiamForLightening/2)

            points.__a = adsk.core.Point3D.create(-self.__wallThicknessForLightening/2, 0, 0)
            points.__b = adsk.core.Point3D.create(-self.__wallThicknessForLightening/2, self.__outerDiamForLightening/2, 0)
            points.__c = adsk.core.Point3D.create( self.__wallThicknessForLightening/2, 0, 0)
            points.__d = adsk.core.Point3D.create( self.__wallThicknessForLightening/2, self.__outerDiamForLightening/2, 0)

            __line_ab = sketch.sketchCurves.sketchLines.addByTwoPoints(points.__a, points.__b)
            __line_cd = sketch.sketchCurves.sketchLines.addByTwoPoints(points.__c, points.__d)

            points.a = __line_ab.geometry.intersectWithCurve(innerLighteningCircle.geometry).item(0)
            points.b = __line_ab.geometry.intersectWithCurve(outerLighteningCircle.geometry).item(0)
            points.c = __line_cd.geometry.intersectWithCurve(innerLighteningCircle.geometry).item(0)
            points.d = __line_cd.geometry.intersectWithCurve(outerLighteningCircle.geometry).item(0)

            innerLighteningCircle.deleteMe()
            outerLighteningCircle.deleteMe()
            __line_ab.deleteMe()
            __line_cd.deleteMe()

            line_ab = sketch.sketchCurves.sketchLines.addByTwoPoints(points.a, points.b)
            line_cd = sketch.sketchCurves.sketchLines.addByTwoPoints(points.c, points.d)

            inputEntities = adsk.core.ObjectCollection.create()
            inputEntities.add(line_ab)
            inputEntities.add(line_cd)

            for i in range(1, 4):
                transform.setToRotation(math.radians(120), normal, self.__points.A)
                copiedEntities = sketch.copy(inputEntities, transform)
                copiedSketchLine = [entity for entity in copiedEntities if isinstance(entity, adsk.fusion.SketchLine)]

                originLineForArc = inputEntities.item(0)
                copiedLineForArc = copiedSketchLine[1]

                angle = self.__utils.getThreePointsAngle(originLineForArc.geometry.startPoint, self.__points.A, copiedLineForArc.geometry.startPoint)
                innerLighteningArc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.A, originLineForArc.geometry.startPoint, math.radians(angle))

                angle = self.__utils.getThreePointsAngle(originLineForArc.geometry.endPoint, self.__points.A, copiedLineForArc.geometry.endPoint)
                otuerLighteningArc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.A, originLineForArc.geometry.endPoint, math.radians(angle))

                if i == 3:
                    copiedSketchLine[0].deleteMe()
                    copiedSketchLine[1].deleteMe()
                else:
                    inputEntities = adsk.core.ObjectCollection.create()
                    inputEntities.add(copiedSketchLine[0])
                    inputEntities.add(copiedSketchLine[1])

        # Construction for wheel locking diameter
        wheelLockingCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.__lockingDiam/2)
        wheelLockingCircle.isConstruction = True

    def drawPallet(self):
        sketch = self.__palletSketch
        normal = self.__utils.getPlaneNormal(self.getPlane())
        normal = self.__utils.getWorldNormal(sketch, normal)

        transform = adsk.core.Matrix3D.create()
        points = Points()

        # Pallet arbor
        palletArborHole = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.O, self.getArborHoleDiam()/2)

        # Pallet arm outlines
        ## Innter arc to entry pallet
        wheelMajorCircleLeft = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getWheelMajorDiameter()/2)
        linePZA = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.P, self.__points.ZA)
        points.za = linePZA.geometry.intersectWithCurve(wheelMajorCircleLeft.geometry).item(0)

        transform.setToRotation(math.radians(90), normal, self.__points.A)
        vector = self.__points.ZE.vectorTo(self.__points.O)
        vector.normalize()
        vector.scaleBy(0.01)
        vector.transformBy(transform)
        point = self.__points.ZE.copy()
        point.translateBy(vector)
        innerArcToEntryPallet = sketch.sketchCurves.sketchArcs.addByThreePoints(self.__points.ZE, point, points.za)

        wheelMajorCircleLeft.deleteMe()
        linePZA.deleteMe()

        ## Outer arc to entry pallet
        # vector = self.__points.ZE.vectorTo(self.__points.O)
        transform.setToRotation(math.radians(self.getLeverSwingAngle()/2), normal, self.__points.O)
        vector = adsk.core.Vector3D.create(0, self.getLeverWidth()/2, 0)
        vector.transformBy(transform)
        points.ze = self.__points.O.copy()
        points.ze.translateBy(vector)

        point = innerArcToEntryPallet.geometry.center
        # radius = innerArcToEntryPallet.geometry.radius + self.getLeverWidth()
        radius = point.vectorTo(points.ze).length
        outerCircleToEntryPallet = sketch.sketchCurves.sketchCircles.addByCenterRadius(point, radius)

        lineQZB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, self.__points.ZB)
        points.zb = lineQZB.geometry.intersectWithCurve(outerCircleToEntryPallet.geometry).item(0)

        point = innerArcToEntryPallet.geometry.center
        angle = self.__utils.getThreePointsAngle(points.ze, point, points.zb)
        outerArcToEntryPallet = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(point, points.ze, math.radians(angle))

        outerCircleToEntryPallet.deleteMe()
        lineQZB.deleteMe()

        ## Innter arc to exit pallet
        transform.setToRotation(math.radians(self.getLeverSwingAngle()), normal, self.__points.O)
        points.a = self.__points.A.copy()
        points.a.transformBy(transform)
        wheelMajorCircleForExitLocking = sketch.sketchCurves.sketchCircles.addByCenterRadius(points.a, self.getWheelMajorDiameter()/2)

        lineFZC = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.ZC)
        points.zc = lineFZC.geometry.intersectWithCurve(wheelMajorCircleForExitLocking.geometry).item(0)

        transform.setToRotation(math.radians(-90), normal, self.__points.A)
        vector = self.__points.ZF.vectorTo(self.__points.O)
        vector.normalize()
        vector.scaleBy(0.01)
        vector.transformBy(transform)
        point = self.__points.ZF.copy()
        point.translateBy(vector)
        innerArcToExitPallet = sketch.sketchCurves.sketchArcs.addByThreePoints(self.__points.ZF, point, points.zc)

        wheelMajorCircleForExitLocking.deleteMe()

        ## Extension
        if self.getExtendBool():
            innerArcToExitPallet.isConstruction = True
            lineOzc = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, points.zc)
            lineOzc.isConstruction = True

            transform.setToRotation(math.radians(self.getLeverSwingAngle() + self.getBankingPinOffsetForExtension()), normal, self.__points.O)
            points.a = self.__points.A.copy()
            points.a.transformBy(transform)
            wheelMajorCircleForExitLocking = sketch.sketchCurves.sketchCircles.addByCenterRadius(points.a, self.getWheelMajorDiameter()/2)

            points.zc = lineFZC.geometry.intersectWithCurve(wheelMajorCircleForExitLocking.geometry).item(0)
            innerArcToExitPallet = sketch.sketchCurves.sketchArcs.addByThreePoints(self.__points.ZF, point, points.zc)

            lineOzc = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, points.zc)
            lineOzc.isConstruction = True

            wheelMajorCircleForExitLocking.deleteMe()

        lineFZC.deleteMe()

        ## Outer arc to exit pallet
        # vector = self.__points.ZF.vectorTo(self.__points.O)
        transform.setToRotation(math.radians(self.getLeverSwingAngle()/2), normal, self.__points.O)
        vector = adsk.core.Vector3D.create(0, self.getLeverWidth()/2, 0)
        vector.transformBy(transform)
        points.zf = self.__points.O.copy()
        points.zf.translateBy(vector)

        point = innerArcToExitPallet.geometry.center
        # radius = innerArcToExitPallet.geometry.radius + self.getLeverWidth()
        radius = point.vectorTo(points.zf).length
        outerCircleToExitPallet = sketch.sketchCurves.sketchCircles.addByCenterRadius(point, radius)

        lineJZD = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, self.__points.ZD)
        points.zd = lineJZD.geometry.intersectWithCurve(outerCircleToExitPallet.geometry).item(0)

        point = innerArcToExitPallet.geometry.center
        angle = self.__utils.getThreePointsAngle(points.zf, point, points.zd)
        outerArcToExitPallet = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(point, points.zf, -math.radians(angle))

        outerCircleToExitPallet.deleteMe()
        lineJZD.deleteMe()

        # Entry pallet
        ## Incline face
        entryPalletInclineFace = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, self.__points.P)

        ## Locking face
        entryPalletLockingFace = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, points.zb)

        ## Another face
        entryPalletAnotherFace = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.P, points.za)

        ## Extension
        if self.getExtendBool():
            entryPalletInclineFace.isConstruction = True
            sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, self.__points.extQ)
            sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.extQ, self.__points.extP)
            sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.extP, self.__points.P)

            lineOP = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.P)
            lineOP.isConstruction = True

            lineExtOP = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.extP)
            lineExtOP.isConstruction = True

        # Exit pallet
        ## Incline face
        exitPalletInclineFace = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.J)

        ## Locking face
        exitPalletLockingFace = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, points.zc)

        ## Another face
        exitPalletAnotherFace = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, points.zd)

        ## Extension
        if self.getExtendBool():
            exitPalletInclineFace.isConstruction = True
            sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.extF)
            sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.extF, self.__points.extJ)
            sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.extJ, self.__points.J)

            lineOF = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.F)
            lineOF.isConstruction = True

            lineExtOF = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.extF)
            lineExtOF.isConstruction = True

        # Ohters
        angle = self.__utils.getThreePointsAngle(self.__points.ZE, self.__points.O, self.__points.ZF)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.O, self.__points.ZE, math.radians(angle))


class LeverAndRoller(CommonDrawingPrameters):
    def __init__(self,
                 arborDistWheelToPallet,
                 arborDistLeverToRoller,
                 swingAngleRaitoRollerToLever,
                 impulsePinAngle,
                 diamRaitoImpulsePinOrbitToSafetyRoller,
                 **commonParameters):

        super().__init__(**commonParameters)
        self.__arborDistWheelToPallet = arborDistWheelToPallet
        self.__arborDistLeverToRoller = arborDistLeverToRoller
        self.__swingAngleRaitoRollerToLever = swingAngleRaitoRollerToLever
        self.__rollerSwingAngle = self.getLeverSwingAngle()*self.__swingAngleRaitoRollerToLever
        self.__impulsePinAngle = math.degrees(impulsePinAngle)
        self.__diamRaitoImpulsePinOrbitToSafetyRoller = diamRaitoImpulsePinOrbitToSafetyRoller

        self.__safetyRollerCrescentAngle = 54 # 54[deg]
        self.__forkSlotOffset = 0.01 # 0.1[mm]

        self.__points = Points()
        self.__utils = Utilites()
        self.__getPointsForDrawing()

    def draw(self):
        self.createLeverComponent()
        self.createRollerComponent()
        self.createLeverSketch()
        self.createRollerSketch()
        self.drawLeverConstructions()
        self.drawLever()
        self.drawRollerConstructions()
        self.drawRoller()

    def createLeverComponent(self):
        self.__palletForkComp = self.__utils.getComponentByName(self.getDesign(), 'PalletFork')

        self.__leverComp = self.__utils.createComponentToParent(self.__palletForkComp)
        self.__leverComp.name = 'Lever' + '_arborDist' + str(round(self.__arborDistLeverToRoller*10,2)) +'_width' + str(round(self.getLeverWidth()*10,2)) + '_swingAngleRaito' + str(self.__swingAngleRaitoRollerToLever)

    def createRollerComponent(self):
        self.__rollerComp = self.__utils.createComponent(self.getDesign())
        self.__rollerComp.name = 'SafetyRoller'+ '_pinAngle' + str(round(self.__impulsePinAngle,2)) + '_diamRaito' + str(self.__diamRaitoImpulsePinOrbitToSafetyRoller)

    def createLeverSketch(self):
        self.__leverConstructionSketch = self.__utils.createSketch(self.__leverComp, self.getPlane())
        self.__leverSketch = self.__utils.createSketch(self.__leverComp, self.getPlane())
        self.__leverConstructionSketch.name = 'Constructions'
        self.__leverSketch.name = 'Lever'
        self.__leverConstructionSketch.isVisible = False
        self.__leverNormal = self.__utils.getPlaneNormal(self.getPlane())
        self.__leverNormal.transformBy(self.__leverSketch.transform)

    def createRollerSketch(self):
        self.__rollerConstructionSketch = self.__utils.createSketch(self.__rollerComp, self.getPlane())
        self.__rollerSketch = self.__utils.createSketch(self.__rollerComp, self.getPlane())
        self.__rollerConstructionSketch.name = 'Constructions'
        self.__rollerSketch.name = 'Safety Roller'
        self.__rollerConstructionSketch.isVisible = False
        self.__rollerNormal = self.__utils.getPlaneNormal(self.getPlane())
        self.__rollerNormal.transformBy(self.__rollerSketch.transform)

    def getImpulsePinOrbitDiameter(self):
        return self.__points.A.vectorTo(self.__points.D).length*2

    def getSafetyRollerDiameter(self):
        return self.getImpulsePinOrbitDiameter()/self.__diamRaitoImpulsePinOrbitToSafetyRoller

    def getImpulsePinDiameter(self):
        return self.__points.E.vectorTo(self.__points.G).length*2

    def getForkPointWidth(self):
        return self.__points.I.vectorTo(self.__points.L).length

    def getForkSlotWidth(self):
        return self.getImpulsePinDiameter()+self.__forkSlotOffset

    def __getPointsForDrawing(self):
        transform = adsk.core.Matrix3D.create()
        normal = adsk.core.Vector3D.create(0, 0, 1)

        self.__points.O = adsk.core.Point3D.create(0, 0, 0)
        self.__points.O.translateBy(adsk.core.Vector3D.create(0, self.__arborDistWheelToPallet, 0))

        self.__points.A = self.__points.O.copy()
        self.__points.A.translateBy(adsk.core.Vector3D.create(0, self.__arborDistLeverToRoller, 0))

        transform.setToRotation(math.radians(self.getLeverSwingAngle()/2), normal, self.__points.O)
        self.__points.B = self.__points.A.copy()
        self.__points.B.transformBy(transform)

        transform.setToRotation(math.radians(-self.__rollerSwingAngle/2), normal, self.__points.A)
        self.__points.C = self.__points.O.copy()
        self.__points.C.transformBy(transform)

        self.__points.D = self.__utils.getIntersectionPoint(self.__points.O, self.__points.B, self.__points.A, self.__points.C)

        transform.setToRotation(math.radians(-self.__rollerSwingAngle/2), normal, self.__points.A)
        self.__points.E = self.__points.A.copy()
        self.__points.E.translateBy(adsk.core.Vector3D.create(0, -self.getImpulsePinOrbitDiameter()/2, 0))
        self.__points.E.transformBy(transform)

        transform.setToRotation(math.radians(-self.__impulsePinAngle/2), normal, self.__points.A)
        self.__points.F = self.__points.E.copy()
        self.__points.F.transformBy(transform)

        self.__points.G = self.__utils.getPerpendicularProjectedPoint(self.__points.E, self.__points.A, self.__points.F)

        transform.setToRotation(math.radians(90), normal, self.__points.E)
        vector = self.__points.E.vectorTo(self.__points.B)
        vector.transformBy(transform)
        vector.normalize()
        vector.scaleBy(self.getImpulsePinDiameter()/2+self.__forkSlotOffset/2)
        self.__points.H = self.__points.E.copy()
        self.__points.H.translateBy(vector)

        vectorAE = self.__points.A.vectorTo(self.__points.E)
        vectorAH = self.__points.A.vectorTo(self.__points.H)
        angleEAH = math.degrees(math.acos(vectorAE.dotProduct(vectorAH)/(vectorAE.length*vectorAH.length)))
        transform.setToRotation(math.radians(-self.__safetyRollerCrescentAngle/2+angleEAH), normal, self.__points.A)
        self.__points.I = self.__points.H.copy()
        self.__points.I.transformBy(transform)

        transform.setToRotation(math.radians(self.getLeverSwingAngle()/2), normal, self.__points.E)
        vector = adsk.core.Vector3D.create(0, -self.getImpulsePinDiameter()/2, 0)
        vector.transformBy(transform)
        self.__points.J = self.__points.H.copy()
        self.__points.J.translateBy(vector)

        vector = self.__points.E.vectorTo(self.__points.B)
        self.__points.K = self.__points.H.copy()
        self.__points.K.translateBy(vector)

        self.__points.L = self.__utils.getLineSymmetryPoint(self.__points.I, self.__points.O, self.__points.B)
        self.__points.M = self.__utils.getLineSymmetryPoint(self.__points.J, self.__points.O, self.__points.B)
        self.__points.N = self.__utils.getLineSymmetryPoint(self.__points.K, self.__points.O, self.__points.B)

        vector = self.__points.O.vectorTo(self.__points.E)
        scalar = vector.length-self.getImpulsePinDiameter()/2-self.getLeverWidth()/2
        vector.normalize()
        vector.scaleBy(scalar)
        self.__points.P = self.__points.O.copy()
        self.__points.P.translateBy(vector)

        transform.setToRotation(math.radians(self.getLeverSwingAngle()/2), normal, self.__points.O)
        vector = adsk.core.Vector3D.create(-self.getLeverWidth()/2, 0, 0)
        vector.transformBy(transform)
        self.__points.Q = self.__points.O.copy()
        self.__points.Q.translateBy(vector)

        vector = self.__points.O.vectorTo(self.__points.P)
        self.__points.R = self.__points.Q.copy()
        self.__points.R.translateBy(vector)

        scalar = self.getForkSlotWidth()/2+self.getLeverWidth()/2
        vector = self.__points.P.vectorTo(self.__points.R)
        vector.normalize()
        vector.scaleBy(scalar)
        self.__points.S = self.__points.P.copy()
        self.__points.S.translateBy(vector)

        self.__points.T = self.__utils.getLineSymmetryPoint(self.__points.Q.copy(), self.__points.O, self.__points.B)
        self.__points.U = self.__utils.getLineSymmetryPoint(self.__points.R.copy(), self.__points.O, self.__points.B)
        self.__points.V = self.__utils.getLineSymmetryPoint(self.__points.S.copy(), self.__points.O, self.__points.B)

        transform.setToRotation(math.radians(self.__impulsePinAngle/2), normal, self.__points.A)
        self.__points.W = self.__points.E.copy()
        self.__points.W.transformBy(transform)

        transform.setToRotation(math.radians(-self.__safetyRollerCrescentAngle/2-self.__rollerSwingAngle/2), normal, self.__points.A)
        vector = adsk.core.Vector3D.create(0, -self.getSafetyRollerDiameter()/2, 0)
        vector.transformBy(transform)
        self.__points.X = self.__points.A.copy()
        self.__points.X.translateBy(vector)

        self.__points.Y = self.__utils.getLineSymmetryPoint(self.__points.X, self.__points.A, self.__points.E)

        vector = self.__points.E.vectorTo(self.__points.A)
        vector.normalize()
        vector.scaleBy(self.getImpulsePinDiameter()/2)
        self.__points.Z = self.__points.E.copy()
        self.__points.Z.translateBy(vector)

        self.__points.ZA = self.__utils.getPerpendicularProjectedPoint(self.__points.Z, self.__points.A, self.__points.F)

        self.__points.ZB = self.__utils.getLineSymmetryPoint(self.__points.ZA, self.__points.A, self.__points.E)

        transform.setToRotation(math.radians(-self.__rollerSwingAngle/2), normal, self.__points.A)
        vector = adsk.core.Vector3D.create(-self.getSafetyRollerDiameter()/2, 0, 0)
        vector.transformBy(transform)
        self.__points.ZC = self.__points.A.copy()
        self.__points.ZC.translateBy(vector)

        self.__points.ZD = self.__utils.getLineSymmetryPoint(self.__points.ZC, self.__points.A, self.__points.E)

    def drawLeverConstructions(self):
        sketch = self.__leverConstructionSketch

        leverRootcircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.O, self.getLeverWidth()/2)
        leverRootcircle.isConstruction = True

        lineAO = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.O)
        lineAO.isConstruction = True

        lineOB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.B)
        lineOB.isConstruction = True

        lineAC = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.C)
        lineAC.isConstruction = True

        impulsePinOrbitCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getImpulsePinOrbitDiameter()/2)
        impulsePinOrbitCircle.isConstruction = True

        safetyRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getSafetyRollerDiameter()/2)
        safetyRollerCircle.isConstruction = True

        lineAF = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.F)
        lineAF.isConstruction = True

        pointG = sketch.sketchPoints.add(self.__points.G)

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
        sketch = self.__rollerConstructionSketch

        lineAO = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.O)
        lineAO.isConstruction = True

        lineOB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.B)
        lineOB.isConstruction = True

        lineAC = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.C)
        lineAC.isConstruction = True

        impulsePinOrbitCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getImpulsePinOrbitDiameter()/2)
        impulsePinOrbitCircle.isConstruction = True

        safetyRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getSafetyRollerDiameter()/2)
        safetyRollerCircle.isConstruction = True

        lineAF = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.A, self.__points.F)
        lineAF.isConstruction = True

        pointG = sketch.sketchPoints.add(self.__points.G)

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
        normal = self.__utils.getPlaneNormal(self.getPlane())
        normal = self.__utils.getWorldNormal(sketch, normal)

        transform = adsk.core.Matrix3D.create()
        points = Points()

        # Fork slot
        impulsePinOrbitCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getImpulsePinOrbitDiameter()/2)
        lineJK = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, self.__points.K)
        points.k = lineJK.geometry.intersectWithCurve(impulsePinOrbitCircle.geometry).item(0)
        points.n = self.__utils.getLineSymmetryPoint(points.k, self.__points.O, self.__points.B)

        sketch.sketchCurves.sketchLines.addByTwoPoints(points.k, self.__points.J)
        sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.J, self.__points.M)
        sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.M, points.n)

        impulsePinOrbitCircle.deleteMe()
        lineJK.deleteMe()

        # Lever (Fork handle)
        transform.setToRotation(math.radians(90), normal, self.__points.R)
        vector = self.__points.R.vectorTo(self.__points.S)
        vector.transformBy(transform)
        point = self.__points.R.copy()
        point.translateBy(vector)
        line1 = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.Q, self.__points.R)
        line2 = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.R, self.__points.S)
        leverFaceLeft = sketch.sketchCurves.sketchArcs.addFillet(line1, self.__points.R, line2, self.__points.R, self.getForkSlotWidth()/2)

        transform.setToRotation(math.radians(-90), normal, self.__points.U)
        vector = self.__points.U.vectorTo(self.__points.V)
        vector.transformBy(transform)
        point = self.__points.U.copy()
        point.translateBy(vector)
        line1 = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.T, self.__points.U)
        line2 = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.U, self.__points.V)
        leverFaceRight = sketch.sketchCurves.sketchArcs.addFillet(line1, self.__points.U, line2, self.__points.U, self.getForkSlotWidth()/2)

        # Fork horn (tine)
        transform.setToRotation(math.radians(10), normal, points.k)
        vector = points.k.vectorTo(self.__points.I)
        vector.scaleBy(0.5)
        vector.transformBy(transform)
        point = points.k.copy()
        point.translateBy(vector)
        controlPoints = [points.k, point, self.__points.I]
        forkHornGuardFaceLeft = sketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

        transform.setToRotation(math.radians(-10), normal, points.n)
        vector = points.n.vectorTo(self.__points.L)
        vector.scaleBy(0.5)
        vector.transformBy(transform)
        point = points.n.copy()
        point.translateBy(vector)
        controlPoints = [points.n, point, self.__points.L]
        forkHornGuardFaceRight = sketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

        transform.setToRotation(math.radians(10), normal, self.__points.S)
        vector1 = self.__points.J.vectorTo(points.k)
        vector1.transformBy(transform)
        point1 = self.__points.S.copy()
        point1.translateBy(vector1)
        angle = 10 if point1.vectorTo (self.__utils.getLineSymmetryPoint(point1, self.__points.O, self.__points.B)).length >= self.getForkPointWidth() else 20
        transform.setToRotation(math.radians(angle), normal, self.__points.S)
        vector2 = self.__points.J.vectorTo(points.k)
        vector2.transformBy(transform)
        vector2.scaleBy(2.0)
        point2 = self.__points.S.copy()
        point2.translateBy(vector2)
        controlPoints = [self.__points.S, point1, point2, self.__points.I]
        forkHornOuterFaceLeft = sketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

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
        forkHornOuterFaceRight = sketch.sketchCurves.sketchControlPointSplines.add(controlPoints, 3)

        _, _, guardFaceEndPoint = forkHornGuardFaceLeft.evaluator.getEndPoints()
        _, _, outerFaceEndPoint = forkHornOuterFaceLeft.evaluator.getEndPoints()
        sketch.sketchCurves.sketchArcs.addFillet(forkHornGuardFaceLeft, guardFaceEndPoint, forkHornOuterFaceLeft, outerFaceEndPoint, 0.01)

        _, _, guardFaceEndPoint = forkHornGuardFaceRight.evaluator.getEndPoints()
        _, _, outerFaceEndPoint = forkHornOuterFaceRight.evaluator.getEndPoints()
        sketch.sketchCurves.sketchArcs.addFillet(forkHornGuardFaceRight, guardFaceEndPoint, forkHornOuterFaceRight, outerFaceEndPoint, 0.01)

        # Guard pin
        safetyRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getSafetyRollerDiameter()/2)
        lineOB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.B)
        points.b = lineOB.geometry.intersectWithCurve(safetyRollerCircle.geometry).item(0)

        transform.setToRotation(math.radians(-90), normal, points.b)
        points.a = self.__points.A.copy()
        points.a.transformBy(transform)
        lineba = sketch.sketchCurves.sketchLines.addByTwoPoints(points.b, points.a)
        lineMN = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.M, self.__points.N)
        points.b2 = lineba.geometry.intersectWithCurve(lineMN.geometry).item(0)
        points.b3 = self.__utils.getLineSymmetryPoint(points.b2, self.__points.O, self.__points.B)

        sketch.sketchCurves.sketchLines.addByTwoPoints(points.b, points.b2)
        sketch.sketchCurves.sketchLines.addByTwoPoints(points.b, points.b3)
        sketch.sketchCurves.sketchLines.addByTwoPoints(points.b2, points.n)
        sketch.sketchCurves.sketchLines.addByTwoPoints(points.b3, points.k)

        # Lever root
        leverRootArc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.O, self.__points.Q, math.radians(180))
        leverArborHole = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.O, self.getArborHoleDiam()/2)

        safetyRollerCircle.deleteMe()
        lineba.deleteMe()
        lineOB.deleteMe()
        lineMN.deleteMe()

        # Constructions for banking pin
        transform.setToRotation(math.radians(self.getBankingPinOffset()), normal, self.__points.O)
        point1 = self.__points.Q.copy()
        point1.transformBy(transform)
        point2 = self.__points.R.copy()
        point2.transformBy(transform)
        lineForEnterSideBankingPin = sketch.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
        lineForEnterSideBankingPin.isConstruction = True

        if self.getExtendBool():
            transform.setToRotation(math.radians(self.getBankingPinOffset()+self.getBankingPinOffsetForExtension()), normal, self.__points.O)
            point1 = self.__points.Q.copy()
            point1.transformBy(transform)
            point2 = self.__points.R.copy()
            point2.transformBy(transform)
            lineForEnterSideBankingPin = sketch.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
            lineForEnterSideBankingPin.isConstruction = True

        transform.setToRotation(math.radians(-self.getBankingPinOffset()-self.getLeverSwingAngle()), normal, self.__points.O)
        point1 = self.__points.T.copy()
        point1.transformBy(transform)
        point2 = self.__points.U.copy()
        point2.transformBy(transform)
        lineForExitSideBankingPin = sketch.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
        lineForExitSideBankingPin.isConstruction = True

        if self.getExtendBool():
            transform.setToRotation(math.radians(-self.getBankingPinOffset()-self.getBankingPinOffsetForExtension()-self.getLeverSwingAngle()), normal, self.__points.O)
            point1 = self.__points.T.copy()
            point1.transformBy(transform)
            point2 = self.__points.U.copy()
            point2.transformBy(transform)
            lineForExitSideBankingPin = sketch.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
            lineForExitSideBankingPin.isConstruction = True

        # Constructions for arbor distance, lever swing angle
        lineForArborDistances = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.A)
        lineForArborDistances.isConstruction = True

        lineForLeverSwingAngle = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.D)
        lineForLeverSwingAngle.isConstruction = True

    def drawRoller(self):
        sketch = self.__rollerSketch
        normal = self.__utils.getPlaneNormal(self.getPlane())
        normal = self.__utils.getWorldNormal(sketch, normal)

        transform = adsk.core.Matrix3D.create()
        points = Points()

        # Roller arbor
        rollerArborHole = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getArborHoleDiam()/2)

        # Safety roller crescent
        safetyRollerCircle = sketch.sketchCurves.sketchCircles.addByCenterRadius(self.__points.A, self.getSafetyRollerDiameter()/2)
        lineOB = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.O, self.__points.B)
        points.b = lineOB.geometry.intersectWithCurve(safetyRollerCircle.geometry).item(0)

        safetyRollerCircle.deleteMe()
        lineOB.deleteMe()

        point = self.__points.X.copy()
        point = self.__utils.getPerpendicularProjectedPoint(point, self.__points.A, self.__points.E)
        scalar = self.__points.E.vectorTo(points.b).length-(self.getImpulsePinOrbitDiameter()/2-self.getSafetyRollerDiameter()/2) # in-crescent guard pin length
        vector = point.vectorTo(self.__points.A)
        vector.normalize()
        vector.scaleBy(scalar)
        point.translateBy(vector)
        sketch.sketchPoints.add(point)
        safetyRollerCresent = sketch.sketchCurves.sketchArcs.addByThreePoints(self.__points.X, point, self.__points.Y)

        # Safety roller arc
        safetyRollerArc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.A, self.__points.X, math.radians(-360+self.__safetyRollerCrescentAngle))

        # Impulse pin
        impulsePinArc = sketch.sketchCurves.sketchArcs.addByCenterStartSweep(self.__points.A, self.__points.F, math.radians(self.__impulsePinAngle))
        impulsePinFaceLeft = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.ZA)
        impulsePinFaceRight = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.W, self.__points.ZB)

        # Face of impulse pin to safety roller
        transform.setToRotation(math.radians(-90), normal, self.__points.A)
        vector = self.__points.ZC.vectorTo(self.__points.A)
        vector.normalize()
        vector.scaleBy(0.01)
        vector.transformBy(transform)
        point = self.__points.ZC.copy()
        point.translateBy(vector)
        impulsePinToRollerFaceLeft = sketch.sketchCurves.sketchArcs.addByThreePoints(self.__points.ZC, point, self.__points.ZA)

        point = self.__utils.getLineSymmetryPoint(point, self.__points.A, self.__points.E)
        impulsePinToRollerFaceRight = sketch.sketchCurves.sketchArcs.addByThreePoints(self.__points.ZD, point, self.__points.ZB)

        # Constructions for impulse pin, safety roller diameter and swing angle
        lineForimpulsePinFaceLeft = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.F, self.__points.A)
        lineForimpulsePinFaceLeft.isConstruction = True
        lineForimpulsePinFaceRight = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.W, self.__points.A)
        lineForimpulsePinFaceRight.isConstruction = True

        lineForSafetyRollerDiamRaito = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.X, self.__points.A)
        lineForSafetyRollerDiamRaito.isConstruction = True

        lineForRollerSwingAngle = sketch.sketchCurves.sketchLines.addByTwoPoints(self.__points.D, self.__points.A)
        lineForRollerSwingAngle.isConstruction = True