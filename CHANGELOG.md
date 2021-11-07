2021-11-07
1) Algorithm changed! Now instead of copying all objects to list, they are handled one by one. There will be maximum 3 copies of objects (including original object) at time.

2021-10-31
1) Algorithm changed! Now instead of copying objects with all shape keys then removing those shape keys, objects are copied without shape keys (except first one), then shape keys are transferred from original object to corresponding copies. It should be faster and less memory consuming for heavier models with many shape keys that way.
2) Changed combo to list with checkboxes for modifiers. It is possible now to apply multiple modifiers at once.

2021-03-23
1) Merged pull request. Thanks to Iszotic, addon now preserve some shape key's properties like value, range, mute, vertex group, relative to.
2) Added checkbox 'Don't include armature deformations', enabled by default. This solve the problem with applying bone scale to shape key during process.
3) Addon support Blender 2.9.2

2021-02-11
Error message if number of vertices for shape keys is different. Number of vertices is checked after splitting mesh into many meshes but before merging any of them.

2021-02-05
Added warning in dialog panel when user use operator on object with animation data (like drivers, keyframes) assigned to shape keys. Those data will be lost.

2020-09-15
Addon support Blender 2.9.

2019-03-15
Fixed problem with deleted shapekey's content. 

2015-02-06
Instead of duplicate for base shape, original object is used.

2015-02-04
First commit.