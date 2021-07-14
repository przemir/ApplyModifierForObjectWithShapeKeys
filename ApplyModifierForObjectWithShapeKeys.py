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
    "author":       "Przemysław Bągard, additonal contributions by Iszotic, updated to 2.93 by Fro Zen",
    "blender":      (2,93,0),
    "version":      (0,1,2),
    "location":     "Context menu",
    "description":  "Apply modifier and remove from the stack for object with shape keys (Pushing 'Apply' button in 'Object modifiers' tab result in an error 'Modifier cannot be applied to a mesh with shape keys').",
    "category":     "Object Tools > Multi Shape Keys"
}

import bpy, math
from bpy.utils import register_class
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
def applyModifierForObjectWithShapeKeys(context, modifierName, disable_armatures):
    
    list_properties = []
    properties = ["interpolation", "mute", "name", "relative_key", "slider_max", "slider_min", "value", "vertex_group"]
    list = []
    list_shapes = []
    vertCount = -1
    differentVertCount = False
    
    disabled_armature_modifiers = []
    if disable_armatures:
        for modifier in context.object.modifiers:
            if modifier.name != modifierName and modifier.type == 'ARMATURE' and modifier.show_viewport == True:
                disabled_armature_modifiers.append(modifier)
                modifier.show_viewport = False
    
    if context.object.data.shape_keys:
        list_shapes = [o for o in context.object.data.shape_keys.key_blocks]
    
    if(list_shapes == []):
        bpy.ops.object.modifier_apply(modifier=modifierName)
        return (True, None)
    
    list.append(context.view_layer.objects.active)
    for i in range(1, len(list_shapes)):
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        list.append(context.view_layer.objects.active)

    for i, o in enumerate(list):
        context.view_layer.objects.active = o
        key_b = o.data.shape_keys.key_blocks[i]
        print (o.data.shape_keys.key_blocks[i].name, key_b.name)
        properties_object = {p:None for p in properties}
        properties_object["name"] = key_b.name
        properties_object["mute"] = key_b.mute
        properties_object["interpolation"] = key_b.interpolation
        properties_object["relative_key"] = key_b.relative_key.name
        properties_object["slider_max"] = key_b.slider_max
        properties_object["slider_min"] = key_b.slider_min
        properties_object["value"] = key_b.value
        properties_object["vertex_group"] = key_b.vertex_group
        list_properties.append(properties_object)

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
        bpy.ops.object.modifier_apply(modifier=modifierName)
        if vertCount == -1:
            vertCount = len(o.data.vertices)
        if vertCount != len(o.data.vertices):
            differentVertCount = True
    
    if differentVertCount:
        errorInfo = ("Shape keys ended up with different number of vertices!\n"
                     "All shape keys needs to have the same number of vertices after modifier is applied.\n"
                     "Otherwise joining such shape keys will fail!")
        return (False, errorInfo)
            
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = list[0]
    list[0].select_set(True)
    bpy.ops.object.shape_key_add(from_mix=False)
    #workaround for "this type doesn't support IDProperties" handicap error
    key_b0 = context.view_layer.objects.active.data.shape_keys.key_blocks[0]
    key_b0.name = list_properties[0]["name"]
    key_b0.interpolation = list_properties[0]["interpolation"]
    key_b0.mute = list_properties[0]["mute"]
    key_b0.slider_max = list_properties[0]["slider_max"]
    key_b0.slider_min = list_properties[0]["slider_min"]
    key_b0.value = list_properties[0]["value"]
    key_b0.vertex_group = list_properties[0]["vertex_group"]

    for i in range(1, len(list)):
        list[i].select_set(True)
        bpy.ops.object.join_shapes()
        list[i].select_set(False)

        key_b = context.view_layer.objects.active.data.shape_keys.key_blocks[i]
        key_b.name = list_properties[i]["name"]
        key_b.interpolation = list_properties[i]["interpolation"]
        key_b.mute = list_properties[i]["mute"]
        key_b.slider_max = list_properties[i]["slider_max"]
        key_b.slider_min = list_properties[i]["slider_min"]
        key_b.value = list_properties[i]["value"]
        key_b.vertex_group = list_properties[i]["vertex_group"]

    for i in range(0, len(list)):
        key_b = context.view_layer.objects.active.data.shape_keys.key_blocks[i]
        rel_key = list_properties[i]["relative_key"]

        for j in range(0, len(list)):
            key_brel = context.view_layer.objects.active.data.shape_keys.key_blocks[j]
            if rel_key == key_brel.name:
                key_b.relative_key = key_brel
                break

    bpy.ops.object.select_all(action='DESELECT')
    for o in list[1:]:
        o.select_set(True)

    bpy.ops.object.delete(use_global=False)
    context.view_layer.objects.active = list[0]
    context.view_layer.objects.active.select_set(True)
    
    if disable_armatures:
        for modifier in disabled_armature_modifiers:
            modifier.show_viewport = True
    
    return (True, None)

class ApplyModifierForObjectWithShapeKeysOperator(bpy.types.Operator):
    bl_idname = "object.apply_modifier_for_object_with_shape_keys"
    bl_label = "Apply modifier for object with shape keys"
 
    def item_list(self, context):
        return [(modifier.name, modifier.name, modifier.name) for modifier in bpy.context.object.modifiers]
 
    #my_enum = EnumProperty(name="Modifier name", items = item_list)
    my_enum: EnumProperty(
    name="Modifier name",
    items=item_list,
    )
    
    #disable_armatures = BoolProperty(name="Don't include armature deformations", default = True)
    disable_armatures: BoolProperty(
    name="Don't include armature deformations",
    default=True,
    )
 
    def execute(self, context):
        ob = bpy.context.object
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = ob
        ob.select_set(True)
        success, errorInfo = applyModifierForObjectWithShapeKeys(context, self.my_enum, self.disable_armatures)
        
        if not success:
            self.report({'ERROR'}, errorInfo)
        
        return {'FINISHED'}
        
    def draw(self, context):
        if context.object.data.shape_keys and context.object.data.shape_keys.animation_data:
            self.layout.separator()
            self.layout.label(text="Warning:")
            self.layout.label(text="              Object contains animation data")
            self.layout.label(text="              (like drivers, keyframes etc.)")
            self.layout.label(text="              assigned to shape keys.")
            self.layout.label(text="              Those data will be lost!")
            self.layout.separator()
        self.layout.prop(self, "my_enum")
        self.layout.prop(self, "disable_armatures")
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class DialogPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_apply_modifier_for_object_with_shape_keys"
    bl_label = "Multi Shape Keys"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
 
    def draw(self, context):
        self.layout.operator("object.apply_modifier_for_object_with_shape_keys")

classes = [
    DialogPanel,
    ApplyModifierForObjectWithShapeKeysOperator
]

def menu_func(self, context):
    self.layout.operator(ApplyModifierForObjectWithShapeKeysOperator.bl_idname)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object.append(menu_func)
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
 
if __name__ == "__main__":
    register()
