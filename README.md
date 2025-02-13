# ApplyModifierForObjectWithShapeKeys
*Blender script*

Apply modifiers and remove them from the stack for objects with shape keys. 
(Pushing 'Apply' in the 'Object modifiers' tab results in the error 'Modifier cannot be applied to a mesh with shape keys').

## Usage

Press 'F3' and choose 'Apply modifier for object with shape keys'.

![screen](screen.png 'Addon location')

## Usage in script

In case you want to use addon's method in script/exporter here is sample usage:

```
import bpy
import time

import ApplyModifierForObjectWithShapeKeys

modifiers = ['Subdivision']

ApplyModifierForObjectWithShapeKeys.applyModifierForObjectWithShapeKeys(bpy.context, modifiers, True)
```
Modifiers are identified by name.

Last parameter is 'Don't include armature deformation' and by default is set to true.

Note that method assumes object is selected.

## Installation

Select "File -> User Preferences" and choose "Addon" tab. Click "Install from file..." and choose the downloaded file (only "ApplyModifierForObjectWithShapeKeys.py", not the folder).

## How the script works

The object is duplicated to match the number of shapekeys. For each object, all but one shape key is removed, with each object having a different shape key. Then, each object applies the selected modifier. After that, all objects are merged into one as shape keys.
Note that this solution may not work for modifiers which change the amount of vertices for different shapes (for example, 'Boolean' modifier, or 'Mirror' with merge option).

Algorithm changed!
Now instead of copying all objects to list, they are handled one by one. There will be maximum 3 copies of objects (including original object) at time.
It should be less memory consuming for heavier models with many shape keys that way.


