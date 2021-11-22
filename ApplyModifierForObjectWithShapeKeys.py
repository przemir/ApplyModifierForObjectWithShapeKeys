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
    "version":      (0,2,1),
    "location":     "Context menu",
    "description":  "Apply modifier and remove from the stack for object with shape keys (Pushing 'Apply' button in 'Object modifiers' tab result in an error 'Modifier cannot be applied to a mesh with shape keys').",
    "category":     "Object Tools > Multi Shape Keys"
}

import bpy, math
import time
from bpy.utils import register_class
from bpy.props import *

# Algorithm (old):
# - Duplicate active object as many times as the number of shape keys
# - For each copy remove all shape keys except one
# - Removing last shape does not change geometry data of object
# - Apply modifier for each copy
# - Join objects as shapes and restore shape keys names
# - Delete all duplicated object except one
# - Delete old object
# Original object should be preserved (to keep object name and other data associated with object/mesh). 

# Algorithm (new):
# Don't make list of copies, handle it one shape at time.
# In this algorithm there shouldn't be more than 3 copy of object at time, so it should be more memory-friendly.
#
# - Copy object which will hold shape keys
# - For original object (which will be also result object), remove all shape keys, then apply modifiers. Add "base" shape key
# - For each shape key except base copy temporary object from copy. Then for temporaryObject:
#     - remove all shape keys except one (done by removing all shape keys, then transfering the right one from copyObject)
#     - apply modifiers
#     - merge with originalObject
#     - delete temporaryObject
# - Delete copyObject.

def applyModifierForObjectWithShapeKeys(context, selectedModifiers, disable_armatures):
    
    list_properties = []
    properties = ["interpolation", "mute", "name", "relative_key", "slider_max", "slider_min", "value", "vertex_group"]
    shapesCount = 0
    vertCount = -1
    startTime = time.time()

    disabled_armature_modifiers = []
    if disable_armatures:
        for modifier in context.object.modifiers:
            if modifier.name not in selectedModifiers and modifier.type == 'ARMATURE' and modifier.show_viewport == True:
                disabled_armature_modifiers.append(modifier)
                modifier.show_viewport = False
    
    if context.object.data.shape_keys:
        shapesCount = len(context.object.data.shape_keys.key_blocks)
    
    if(shapesCount == 0):
        for modifierName in selectedModifiers:
            bpy.ops.object.modifier_apply(modifier=modifierName)
        return (True, None)
    
    # We want to preserve original object, so all shapes will be joined to it.
    originalObject = context.view_layer.objects.active
    bpy.ops.object.select_all(action='DESELECT')
    originalObject.select_set(True)
    
    # Copy object which will holds all shape keys.
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
    copyObject = context.view_layer.objects.active
    copyObject.select_set(False)
    
    # Return selection to originalObject.
    context.view_layer.objects.active = originalObject
    originalObject.select_set(True)
    
    # Save key shape properties
    for i in range(0, shapesCount):
        key_b = originalObject.data.shape_keys.key_blocks[i]
        print (originalObject.data.shape_keys.key_blocks[i].name, key_b.name)
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

    # Handle base shape in "originalObject"
    print("applyModifierForObjectWithShapeKeys: Applying base shape key")
    bpy.ops.object.shape_key_remove(all=True)
    for modifierName in selectedModifiers:
        bpy.ops.object.modifier_apply(modifier=modifierName)
    vertCount = len(originalObject.data.vertices)
    bpy.ops.object.shape_key_add(from_mix=False)
    originalObject.select_set(False)
    
    # Handle other shape-keys: copy object, get right shape-key, apply modifiers and merge with originalObject.
    # We handle one object at time here.
    for i in range(1, shapesCount):
        currTime = time.time()
        elapsedTime = currTime - startTime

        print("applyModifierForObjectWithShapeKeys: Applying shape key %d/%d ('%s', %0.2f seconds since start)" % (i+1, shapesCount, list_properties[i]["name"], elapsedTime))
        context.view_layer.objects.active = copyObject
        copyObject.select_set(True)
        
        # Copy temp object.
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        tmpObject = context.view_layer.objects.active
        bpy.ops.object.shape_key_remove(all=True)
        copyObject.select_set(True)
        copyObject.active_shape_key_index = i
        
        # Get right shape-key.
        bpy.ops.object.shape_key_transfer()
        context.object.active_shape_key_index = 0
        bpy.ops.object.shape_key_remove()
        bpy.ops.object.shape_key_remove(all=True)
        
        # Time to apply modifiers.
        for modifierName in selectedModifiers:
            bpy.ops.object.modifier_apply(modifier=modifierName)
        
        # Verify number of vertices.
        if vertCount != len(tmpObject.data.vertices):
            errorInfo = ("Shape keys ended up with different number of vertices!\n"
                         "All shape keys needs to have the same number of vertices after modifier is applied.\n"
                         "Otherwise joining such shape keys will fail!")
            return (False, errorInfo)
    
        # Join with originalObject
        copyObject.select_set(False)
        context.view_layer.objects.active = originalObject
        originalObject.select_set(True)
        bpy.ops.object.join_shapes()
        originalObject.select_set(False)
        context.view_layer.objects.active = tmpObject
        
        # Remove tmpObject
        bpy.ops.object.delete(use_global=False)
    
    # Restore shape key properties like name, mute etc.
    context.view_layer.objects.active = originalObject
    for i in range(0, shapesCount):
        key_b = context.view_layer.objects.active.data.shape_keys.key_blocks[i]
        key_b.name = list_properties[i]["name"]
        key_b.interpolation = list_properties[i]["interpolation"]
        key_b.mute = list_properties[i]["mute"]
        key_b.slider_max = list_properties[i]["slider_max"]
        key_b.slider_min = list_properties[i]["slider_min"]
        key_b.value = list_properties[i]["value"]
        key_b.vertex_group = list_properties[i]["vertex_group"]
        rel_key = list_properties[i]["relative_key"]
    
        for j in range(0, shapesCount):
            key_brel = context.view_layer.objects.active.data.shape_keys.key_blocks[j]
            if rel_key == key_brel.name:
                key_b.relative_key = key_brel
                break
    
    # Remove copyObject.
    originalObject.select_set(False)
    context.view_layer.objects.active = copyObject
    copyObject.select_set(True)
    bpy.ops.object.delete(use_global=False)
    
    # Select originalObject.
    context.view_layer.objects.active = originalObject
    context.view_layer.objects.active.select_set(True)
    
    if disable_armatures:
        for modifier in disabled_armature_modifiers:
            modifier.show_viewport = True
    
    return (True, None)

class PropertyCollectionModifierItem(bpy.types.PropertyGroup):
    checked: BoolProperty(name="", default=False)
bpy.utils.register_class(PropertyCollectionModifierItem)

class ApplyModifierForObjectWithShapeKeysOperator(bpy.types.Operator):
    bl_idname = "object.apply_modifier_for_object_with_shape_keys"
    bl_label = "Apply modifier for object with shape keys"
 
    def item_list(self, context):
        return [(modifier.name, modifier.name, modifier.name) for modifier in bpy.context.object.modifiers]
 
    ##my_enum = EnumProperty(name="Modifier name", items = item_list)
    #my_enum: EnumProperty(
    #name="Modifier name",
    #items=item_list,
    #)
    
    #my_enum: BoolVectorProperty(
    #name="Modifier name",
    #size=len(
    #items=item_list,
    #)
    
    my_collection: CollectionProperty(type=PropertyCollectionModifierItem)
    
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
        
        selectedModifiers = [o.name for o in self.my_collection if o.checked]
        
        if not selectedModifiers:
            self.report({'ERROR'}, 'No modifier selected!')
            return {'FINISHED'}
        
        success, errorInfo = applyModifierForObjectWithShapeKeys(context, selectedModifiers, self.disable_armatures)
        
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
        #self.layout.prop(self, "my_enum")
        box = self.layout.box()
        for prop in self.my_collection:
            box.prop(prop, "checked", text=prop["name"])
        #box.prop(self, "my_collection")
        self.layout.prop(self, "disable_armatures")
 
    def invoke(self, context, event):
        self.my_collection.clear()
        for i in range(len(bpy.context.object.modifiers)):
            item = self.my_collection.add()
            item.name = bpy.context.object.modifiers[i].name
            item.checked = False
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
