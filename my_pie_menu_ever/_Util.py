import bpy
from mathutils import Vector, Quaternion
from bpy.types import Panel, Menu, Operator
from rna_prop_ui import PropertyPanel
from bpy.app.translations import (
    pgettext_iface as iface_,
    pgettext_tip as tip_,
    contexts as i18n_contexts,
)
# HT – ヘッダー
# MT – メニュー
# OT – オペレーター
# PT – パネル
# UL – UIリスト
class OT_SetterBase():
    propName: bpy.props.StringProperty()
    def execute(self, context):
        target = getattr(context, self.propName, None)
        setattr(target, self.propName, self.value)
        return {'FINISHED'}
    @staticmethod
    def operator(cls, layout, label, targetObj, propName, value=None, depress=None, isActive=True, ctxt=''):
        layout.context_pointer_set(name=propName, data=targetObj)
        if depress is None:
            cur_value = getattr(targetObj, propName, False) if value is None else value
            depress = cur_value if isinstance(cur_value, bool) else False
        op = layout.operator(cls, text=label, text_ctxt=ctxt, depress=depress)
        op.propName = propName
        print()
        op.value = not getattr(targetObj, propName) if cls == "op.set_invert" else value
        layout.enabled = isActive and targetObj != None
class OT_SetPointer(bpy.types.Operator):
    bl_idname = "op.set_pointer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    propName: bpy.props.StringProperty()
    propObj: bpy.props.StringProperty()
    propValue: bpy.props.StringProperty()
    def execute(self, context):
        target = getattr(context, self.propObj, None)
        value = getattr(context, self.propValue, None)
        setattr(target, self.propName, value)
        return {'FINISHED'}
    @staticmethod
    def operator(layout, label, targetObj, propName, value, isActive = True, ctxt = ''):
        # context_pointer_setはopeartorの前で設定しないと有効にならない
        keyObj = label
        keyValue = keyObj + "_value"
        layout.context_pointer_set(name=keyObj, data=targetObj)
        layout.context_pointer_set(name=keyValue, data=value)
        op = layout.operator(OT_SetPointer.bl_idname, text=label, text_ctxt = ctxt)
        op.propName = propName
        op.propObj = keyObj
        op.propValue = keyValue
        layout.enabled = isActive and targetObj != None
 
class OT_SetBool(OT_SetterBase, bpy.types.Operator):
    bl_idname = "op.set_bool"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    value: bpy.props.BoolProperty()
class OT_SetBoolToggle(OT_SetterBase, bpy.types.Operator):
    bl_idname = "op.set_invert"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    value: bpy.props.BoolProperty()
class OT_SetSingle(OT_SetterBase, bpy.types.Operator):
    bl_idname = "op.set_signel"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    value: bpy.props.FloatProperty()
class OT_SetString(OT_SetterBase, bpy.types.Operator):
    bl_idname = "op.set_signel"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    value: bpy.props.FloatProperty()
class OT_Empty(bpy.types.Operator):
    bl_idname = "op.empty"
    bl_label = "empty"
    def execute(self, context):
        return {'FINISHED'}
# --------------------------------------------------------------------------------
def show_enum_values(obj, prop_name):
    print([item.identifier for item in obj.bl_rna.properties[prop_name].enum_items])
def enum_values(obj, prop_name):
    return [item.identifier for item in obj.bl_rna.properties[prop_name].enum_items]
def layout_prop(layout, target, prop, text=None, expand=False, toggle=-1):
    if target != None:
        layout.prop(target, prop, text=text, expand=expand, toggle=toggle, emboss=True)
    else:
        layout.label(text='None')
def layout_operator(layout, opid, label=None, isActive=None, depress=False):
    if isActive == None:
        return layout.operator(opid, text=label, depress=depress)
    else:
        r = layout.row()
        r.active = isActive
        return r.operator(opid, text=label, depress=depress)
def layout_for_mirror(layout):
    row = layout.row(align=True)
    row.label(icon='MOD_MIRROR')
    sub = row.row(align=True)
    sub.scale_x = 0.9
    return row, sub
def reset_pose_bone_location(armature):
    if armature.type == 'ARMATURE':
        for b in armature.pose.bones:
            b.location = Vector((0, 0, 0))
def reset_pose_bone_rotation(armature):
    if armature.type == 'ARMATURE':
        for b in armature.pose.bones:
            b.rotation_euler = (0, 0, 0)
def reset_pose_bone_scale(armature):
    if armature.type == 'ARMATURE':
        for b in armature.pose.bones:
            b.scale = Vector((1, 1, 1))
def reset_pose_bone(armature):
    reset_pose_bone_location(armature)
    reset_pose_bone_rotation(armature)
    reset_pose_bone_scale(armature)
def register_classes(classes):
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(e)
def unregister_classes(classes):
    for cls in classes:
        bpy.utils.unregister_class(cls)
def is_armature_in_selected():
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            return True
    return False
def show_msgbox(message, title = "", icon = 'INFO'):
    def draw(self, context):
        lines = message.split('\n')
        for line in lines:
            self.layout.label(text=line)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
# --------------------------------------------------------------------------------
classes = (
    OT_SetBool,
    OT_SetBoolToggle,
    OT_SetSingle,
    OT_SetPointer,
    OT_SetString,
    OT_Empty,
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
