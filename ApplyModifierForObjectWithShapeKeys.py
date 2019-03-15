# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Przemysław Bągard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ------------------------------------------------------------------------------

# Date: 01 February 2015
# Blender script
# Description: Apply modifier and remove from the stack for object with shape keys
# (Pushing 'Apply' button in 'Object modifiers' tab result in an error 'Modifier cannot be applied to a mesh with shape keys').

bl_info = {
    "name":         "Apply modifier for object with shape keys",
    "author":       "Przemysław Bągard",
    "blender":      (2,6,6),
    "version":      (0,1,0),
    "location":     "Context menu",
    "description":  "Apply modifier and remove from the stack for object with shape keys (Pushing 'Apply' button in 'Object modifiers' tab result in an error 'Modifier cannot be applied to a mesh with shape keys').",
    "category":     "Object Tools > Multi Shape Keys"
}

import bpy, math
from bpy.props import *

# Algorithm:
# - Duplicate active object as many times as the number of shape keys
# - For each copy remove all shape keys except one
# - Removing last shape does not change geometry data of object
# - Apply modifier for each copy
# - Join objects as shapes and restore shape keys names
# - Delete all duplicated object except one
# - Delete old object
# - Restore name of object and object data
def applyModifierForObjectWithShapeKeys(context, modifierName):
    list_names = []
    list = []
    list_shapes = []
    if context.object.data.shape_keys:
        list_shapes = [o for o in context.object.data.shape_keys.key_blocks]
    
    if(list_shapes == []):
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifierName)
        return context.scene.objects.active
    
    list.append(context.scene.objects.active)
    for i in range(1, len(list_shapes)):
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "release_confirm":False})
        list.append(context.scene.objects.active)

    for i, o in enumerate(list):
        context.scene.objects.active = o
        list_names.append(o.data.shape_keys.key_blocks[i].name)
        for j in range(i+1, len(list))[::-1]:
            context.object.active_shape_key_index = j
            bpy.ops.object.shape_key_remove()
        for j in range(0, i):
            context.object.active_shape_key_index = 0
            bpy.ops.object.shape_key_remove()
        # last deleted shape doesn't change object shape
        context.object.active_shape_key_index = 0
        # for some reason, changing to edit mode and return object mode fix problem with mesh change when deleting last shapekey
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.shape_key_remove()
        # time to apply modifiers
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifierName)
    
    bpy.ops.object.select_all(action='DESELECT')
    context.scene.objects.active = list[0]
    list[0].select = True
    bpy.ops.object.shape_key_add(from_mix=False)
    context.scene.objects.active.data.shape_keys.key_blocks[0].name = list_names[0]
    for i in range(1, len(list)):
        list[i].select = True
        bpy.ops.object.join_shapes()
        list[i].select = False
        context.scene.objects.active.data.shape_keys.key_blocks[i].name = list_names[i]
    
    bpy.ops.object.select_all(action='DESELECT')
    for o in list[1:]:
        o.select = True

    bpy.ops.object.delete(use_global=False)
    context.scene.objects.active = list[0]
    context.scene.objects.active.select = True
    return context.scene.objects.active

class ApplyModifierForObjectWithShapeKeysOperator(bpy.types.Operator):
    bl_idname = "object.apply_modifier_for_object_with_shape_keys"
    bl_label = "Apply modifier for object with shape keys"
 
    def item_list(self, context):
        return [(modifier.name, modifier.name, modifier.name) for modifier in bpy.context.scene.objects.active.modifiers]
 
    my_enum = EnumProperty(name="Modifier name",
        items = item_list)
 
    def execute(self, context):
    
        ob = context.scene.objects.active
        bpy.ops.object.select_all(action='DESELECT')
        context.scene.objects.active = ob
        context.scene.objects.active.select = True
        applyModifierForObjectWithShapeKeys(context, self.my_enum)
        
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        
bpy.utils.register_class(ApplyModifierForObjectWithShapeKeysOperator)


class DialogPanel(bpy.types.Panel):
    bl_label = "Multi Shape Keys"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("object.apply_modifier_for_object_with_shape_keys")
 
 
def menu_func(self, context):
    self.layout.operator("object.apply_modifier_for_object_with_shape_keys", 
        text="Apply modifier for object with shape keys")
 
def register():
   bpy.utils.register_module(__name__)
 
def unregister():
    bpy.utils.unregister_module(__name__)
 
if __name__ == "__main__":
    register()
