# ApplyModifierForObjectWithShapeKeys
*Blender script*

Apply modifiers and remove them from the stack for objects with shape keys. 
(Pushing 'Apply' in the 'Object modifiers' tab results in the error 'Modifier cannot be applied to a mesh with shape keys').

## Usage

Press 'F3' and choose 'Apply modifier for object with shape keys'.

![screen](screen.png 'Addon location')

## Installation

Select "File -> User Preferences" and choose "Addon" tab. Click "Install from file..." and choose the downloaded file (only "ApplyModifierForObjectWithShapeKeys.py", not the folder).

For Blender 2.9 make sure "Edit -> Preferences -> Interface -> Developer Extras" is checked. Blender 2.91.2 onward does not require this step.

## How the script works

The object is duplicated to match the number of shapekeys. For each object, all but one shape key is removed, with each object having a different shape key. Then, each object applies the selected modifier. After that, all objects are merged into one as shape keys.
Note that this solution may not work for modifiers which change the amount of vertices for different shapes (for example, 'Boolean' modifier, or 'Mirror' with merge option).

## Recent changes

Updated to 2.93
