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
    "author":       "Przemysław Bągard", # Updated by Iszotic
    "blender":      (2,9,2),
    "version":      (0,1,0),
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
def applyModifierForObjectWithShapeKeys(context, modifierName):
    
    list_properties = []
    properties = ["interpolation", "mute", "name", "relative_key", "slider_max", "slider_min", "value", "vertex_group"]
    list = []
    list_shapes = []

    if context.object.data.shape_keys:
        list_shapes = [o for o in context.object.data.shape_keys.key_blocks]
    
    if(list_shapes == []):
        bpy.ops.object.modifier_apply(modifier=modifierName)
        return context.view_layer.objects.active
    
    list.append(context.view_layer.objects.active)
    for i in range(1, len(list_shapes)):
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "orient_type":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "texture_space":False, "release_confirm":False})
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
        bpy.ops.object.shape_key_remove()
        # time to apply modifiers
        bpy.ops.object.modifier_apply(modifier=modifierName) #method no longer has keywoard argument "apply_as"
    
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = list[0]
    context.view_layer.objects.active.select_set(True)
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
    return context.view_layer.objects.active

class ApplyModifierForObjectWithShapeKeysOperator(bpy.types.Operator):
    bl_idname = "object.apply_modifier_for_object_with_shape_keys"
    bl_label = "Apply modifier for object with shape keys"
 
    def item_list(self, context):
        #return [(modifier.name, modifier.name, modifier.name) for modifier in bpy.context.scene.objects.active.modifiers]
        return [(modifier.name, modifier.name, modifier.name) for modifier in bpy.context.view_layer.objects.active.modifiers]
        
    my_enum = EnumProperty(name="Modifier name",
        items = item_list)
 
    def execute(self, context):
    
        ob = context.view_layer.objects.active
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = ob
        ob.select_set(True)
        applyModifierForObjectWithShapeKeys(context, self.my_enum)
        
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
register_class(ApplyModifierForObjectWithShapeKeysOperator)

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
    register_class(DialogPanel)
 
#def unregister():
#    bpy.utils.unregister_module(__name__)
register()
