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