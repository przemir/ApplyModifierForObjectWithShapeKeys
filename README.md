# ApplyModifierForObjectWithShapeKeys
Blender script

Apply modifier and remove from the stack for object with shape keys (Pushing 'Apply' button in 'Object modifiers' tab result in an error 'Modifier cannot be applied to a mesh with shape keys').

Usage

Press 'F3' and choose 'Apply modifier for object with shape keys' action.

![screen](screen.png 'Addon location')

Installation

It is a plugin. Select "File -> User Preferences" and choose "Addon" tab. Click "Install from file..." and choose downloaded file.

For Blender 2.9 make sure "Edit -> Preferences -> Interface -> Developer Extras" is checked.

How script works

Object is duplicated to match number of shapekeys. From every object shapekeys are removed leaving only one shapekey. After that last the shapekey of each object has to be removed. Now each object apply modifier. After that object are joined to first one as shapes.
Note that this solution may not work for modifiers which change different vertices number for different shapes (for example 'Boolean' modifier).
