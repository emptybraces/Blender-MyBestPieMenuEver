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
class MPM_OT_SetterBase():
    propName: bpy.props.StringProperty()
    def execute(self, context):
        target = getattr(context, self.propName, None)
        if target != None:
            setattr(target, self.propName, self.value)
        return {'FINISHED'}
    @staticmethod
    def operator(layout, clsid, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        layout.context_pointer_set(name=propName, data=targetObj)
        if depress is None:
            cur_value = getattr(targetObj, propName, False) if value is None else value
            depress = cur_value if isinstance(cur_value, bool) else False
        if isActive != None:
            layout = layout.row(align=True)
            layout.enabled = isActive and targetObj != None
        op = layout.operator(clsid, text=text, icon=icon, depress=depress)
        op.propName = propName
        op.value = not getattr(targetObj, propName, False) if clsid == MPM_OT_SetBoolToggle.bl_idname else value
class MPM_OT_SetPointer(bpy.types.Operator):
    bl_idname = "op.mpm_set_pointer"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    propName: bpy.props.StringProperty()
    propObj: bpy.props.StringProperty()
    propValue: bpy.props.StringProperty()
    def execute(self, context):
        target = getattr(context, self.propObj, None)
        value = getattr(context, self.propValue, None)
        # print(context, self.propObj, self.propValue, target, value)
        setattr(target, self.propName, value)
        return {'FINISHED'}
    @staticmethod
    def operator(layout, text, targetObj, propName, value, isActive=True, depress=False, ctxt=''):
        keyObj = text
        keyValue = keyObj + "_value"
        # context_pointer_setはopeartorの前で設定しないと有効にならない
        layout.context_pointer_set(name=keyObj, data=targetObj)
        layout.context_pointer_set(name=keyValue, data=value)
        op = layout.operator(MPM_OT_SetPointer.bl_idname, text=text, depress=depress)
        op.propName = propName
        op.propObj = keyObj
        op.propValue = keyValue
        # print(layout, op.propObj, op.propValue, targetObj, value)
        layout.enabled = isActive and targetObj != None
class MPM_OT_SetBool(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "op.mpm_set_bool"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    value: bpy.props.BoolProperty()
    @staticmethod
    def operator(layout, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetBool.bl_idname, text, targetObj, propName, value, icon, depress, isActive)
class MPM_OT_SetBoolToggle(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "op.mpm_set_invert"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    value: bpy.props.BoolProperty()
    @staticmethod
    def operator(layout, text, targetObj, propName, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetBoolToggle.bl_idname, text, targetObj, propName, None, icon, depress, isActive)

class MPM_OT_SetSingle(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "op.mpm_set_signel"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    value: bpy.props.FloatProperty()
    @staticmethod
    def operator(layout, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetSingle.bl_idname, text, targetObj, propName, value, icon, depress, isActive)
class MPM_OT_SetString(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "op.mpm_set_string"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    value: bpy.props.StringProperty()
    @staticmethod
    def operator(layout, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetString.bl_idname, text, targetObj, propName, value, icon, depress, isActive)
class MPM_OT_Empty(bpy.types.Operator):
    bl_idname = "op.mpm_empty"
    bl_label = "empty"
    def execute(self, context):
        return {'FINISHED'}
class MPM_OT_CallPanel(bpy.types.Operator):
    bl_idname = "op.mpm_call_panel"
    bl_label = "call panel"
    name: bpy.props.StringProperty()
    keep_open: bpy.props.BoolProperty(default=True)
    def execute(self, context):
        bpy.ops.wm.call_panel(name=self.name, keep_open=self.keep_open)
        return {'FINISHED'}
# --------------------------------------------------------------------------------
def show_enum_values(obj, prop_name):
    print([item.identifier for item in obj.bl_rna.properties[prop_name].enum_items])
def enum_values(obj, prop_name):
    return [item.identifier for item in obj.bl_rna.properties[prop_name].enum_items]
def layout_prop(layout, target, prop, text=None, isActive=None, expand=False, toggle=-1, icon_only=False):
    if target != None:
        if isActive != None:
            layout = layout.row()
            layout.active = isActive
        layout.prop(target, prop, text=text, expand=expand, toggle=toggle, emboss=True, icon_only=icon_only)
    else:
        layout.label(text='None')
def layout_operator(layout, opid, text=None, isActive=None, depress=False, icon='NONE'):
    if isActive != None:
        layout = layout.row()
        layout.active = isActive
    return layout.operator(opid, text=text, depress=depress, icon=icon)
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
            b.rotation_quaternion = (1, 0, 0, 0)
def reset_pose_bone_scale(armature):
    if armature.type == 'ARMATURE':
        for b in armature.pose.bones:
            b.scale = Vector((1, 1, 1))
def reset_pose_bone(armature):
    armature = get_armature(armature)
    reset_pose_bone_location(armature)
    reset_pose_bone_rotation(armature)
    reset_pose_bone_scale(armature)
def get_armature(obj):
    if obj.type == "MESH":
        for m in obj.modifiers:
            if m.type == "ARMATURE" and m.object != None:
                return m.object
    elif obj.type == "ARMATURE":
        return obj
    else:
        return None
def register_classes(classes):
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(e)
def unregister_classes(classes):
    for cls in classes:
        print("unregistered: ", cls)
        bpy.utils.unregister_class(cls)
def is_armature_in_selected():
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            return True
        if 0 < len([m for m in obj.modifiers if m.type == 'ARMATURE' and m.object != None]):
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
    MPM_OT_SetBool,
    MPM_OT_SetBoolToggle,
    MPM_OT_SetSingle,
    MPM_OT_SetPointer,
    MPM_OT_SetString,
    MPM_OT_Empty,
    MPM_OT_CallPanel,
)
def register():
    register_classes(classes)
def unregister():
    unregister_classes(classes)
