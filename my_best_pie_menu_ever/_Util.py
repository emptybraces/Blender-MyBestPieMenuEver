import bpy
import bmesh
import math
from typing import Callable
from mathutils import Vector, Quaternion, Matrix
from bpy.types import Panel, Menu, Operator
from rna_prop_ui import PropertyPanel
from bpy.app.translations import (
    pgettext_iface as iface_,
    pgettext_tip as tip_,
    contexts as i18n_contexts,
)
VEC3 = (lambda: Vector((0, 0, 0)))
VEC3_X = (lambda: Vector((1, 0, 0)))
VEC3_Y = (lambda: Vector((0, 1, 0)))
VEC3_Z = (lambda: Vector((0, 0, 1)))
callbacks = {}
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
        return {"FINISHED"}

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
    bl_idname = "mpm.set_pointer"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    attrName: bpy.props.StringProperty()
    attrNameTarget: bpy.props.StringProperty()
    attrNameValue: bpy.props.StringProperty()

    def execute(self, context):
        target = getattr(context, self.attrNameTarget, None)
        value = getattr(context, self.attrNameValue, None)
        # print(context, self.attrNameTarget, self.attrNameValue, target, value)
        setattr(target, self.attrName, value)
        return {"FINISHED"}

    @staticmethod
    def operator(layout, text, targetObj, propName, value, isActive=True, depress=False, icon_value=0):
        key_target = replace_leading_underscores(text, '-')
        key_value = key_target + "_value"
        # context_pointer_setはopeartorの前で設定しないと有効にならない
        layout.context_pointer_set(name=key_target, data=targetObj)
        layout.context_pointer_set(name=key_value, data=value)
        op = layout.operator(MPM_OT_SetPointer.bl_idname, text=text, depress=depress, icon_value=icon_value)
        op.attrName = propName
        op.attrNameTarget = key_target
        op.attrNameValue = key_value
        # print(layout, op.propObj, op.attrNameValue, targetObj, value)
        layout.enabled = isActive and targetObj != None


class MPM_OT_SetBool(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "mpm.util_set_bool"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    value: bpy.props.BoolProperty()

    @staticmethod
    def operator(layout, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetBool.bl_idname, text, targetObj, propName, value, icon, depress, isActive)


class MPM_OT_SetBoolToggle(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "mpm.util_set_invert"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    value: bpy.props.BoolProperty()

    @staticmethod
    def operator(layout, text, targetObj, propName, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetBoolToggle.bl_idname, text, targetObj, propName, None, icon, depress, isActive)


class MPM_OT_SetInt(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "mpm.util_set_int"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    value: bpy.props.IntProperty()

    @staticmethod
    def operator(layout, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetInt.bl_idname, text, targetObj, propName, value, icon, depress, isActive)


class MPM_OT_SetSingle(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "mpm.util_set_single"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    value: bpy.props.FloatProperty()

    @staticmethod
    def operator(layout, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetSingle.bl_idname, text, targetObj, propName, value, icon, depress, isActive)


class MPM_OT_SetString(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "mpm.util_set_string"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    value: bpy.props.StringProperty()

    @staticmethod
    def operator(layout, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        if depress is None:
            cur_value = getattr(targetObj, propName, None)
            depress = cur_value == value
            # print(cur_value, value, depress)
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetString.bl_idname, text, targetObj, propName, value, icon, depress, isActive)


class MPM_OT_CallbackOperator(bpy.types.Operator):
    bl_idname = "mpm.util_callback"
    bl_label = ""
    bl_options = {"UNDO"}
    key: bpy.props.StringProperty()
    func_dict: dict[str, Callable[[], None]] = {}

    def execute(self, context):
        f, args = self.func_dict[self.key]
        if args:
            f(*args)  # 引数展開
        else:
            f()
        return {"FINISHED"}

    @staticmethod
    def operator(layout, text, unique_id, func, args, icon="NONE", isActive=None, depress=False):
        if isActive != None:
            # print(unique_id)
            layout = layout.row(align=True)
            layout.enabled = isActive
        op = layout.operator(MPM_OT_CallbackOperator.bl_idname, text=text, icon=icon, depress=depress)
        op.key = unique_id + "." + func.__name__
        MPM_OT_CallbackOperator.func_dict[op.key] = (func, args)
        return op

    @classmethod
    def clear(cls):
        cls.func_dict.clear()


class MPM_OT_CallPanel(bpy.types.Operator):
    bl_idname = "mpm.call_panel"
    bl_label = "call panel"
    name: bpy.props.StringProperty()
    keep_open: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        bpy.ops.wm.call_panel(name=self.name, keep_open=self.keep_open)
        return {"FINISHED"}


# --------------------------------------------------------------------------------

def selected_objects():
    objs = set(bpy.context.selected_objects)
    if bpy.context.active_object:
        objs.add(bpy.context.active_object)
    return objs


def select_active(obj):
    if obj:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj


def select_add(obj):
    obj.select_set(True)


def is_selected_verts(context):
    if context.mode == "EDIT_MESH":
        obj = context.edit_object
        return obj and obj.type == "MESH" and any(e.select for e in bmesh.from_edit_mesh(obj.data).verts)
    else:
        obj = context.active_object
        return obj and obj.type == "MESH" and any(v.select for v in obj.data.vertices)


def has_active_vgroup(context):
    obj = context.object
    return obj and obj.type == "MESH" and obj.vertex_groups.active != None


def has_active_image(context):
    return None != getattr(context.area.spaces.active, "image", None)


def is_selected_edges(obj):
    return obj and obj.type == "MESH" and any(e.select for e in bmesh.from_edit_mesh(obj.data).edges)


def print_enum_values(obj, prop_name):
    print([item.identifier for item in obj.bl_rna.properties[prop_name].enum_items])


def enum_values(obj, prop_name):
    return [item.identifier for item in obj.bl_rna.properties[prop_name].enum_items]


def layout_prop(layout, target, prop, text=None, isActive=None, expand=False, toggle=-1, index=-1, icon="NONE", icon_only=False):
    if target != None:
        if isActive != None:
            layout = layout.row()
            layout.enabled = isActive
        layout.prop(target, prop, text=text, expand=expand, toggle=toggle, index=index, emboss=True, icon=icon, icon_only=icon_only)
    else:
        layout.label(text="None")


def layout_operator(layout, opid, text=None, isActive=None, depress=False, icon="NONE"):
    if isActive != None:
        layout = layout.row()
        layout.enabled = isActive
    return layout.operator(opid, text=text, depress=depress, icon=icon)


def layout_for_mirror(layout):
    row = layout.row(align=True)
    row.label(icon="MOD_MIRROR")
    sub = row.row(align=True)
    sub.scale_x = 0.9
    return row, sub


def reset_pose_bone_location(armature):
    if armature != None and armature.type == "ARMATURE":
        for b in armature.pose.bones:
            b.location = Vector((0, 0, 0))


def reset_pose_bone_rotation(armature):
    if armature != None and armature.type == "ARMATURE":
        for b in armature.pose.bones:
            b.rotation_euler = (0, 0, 0)
            b.rotation_quaternion = (1, 0, 0, 0)


def reset_pose_bone_scale(armature):
    if armature != None and armature.type == "ARMATURE":
        for b in armature.pose.bones:
            b.scale = Vector((1, 1, 1))


def reset_pose_bone(armature):
    armature = get_armature(armature)
    reset_pose_bone_location(armature)
    reset_pose_bone_rotation(armature)
    reset_pose_bone_scale(armature)


def get_armature(obj):
    if obj:
        return obj if obj.type == "ARMATURE" else obj.find_armature()
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
        if obj.type == "ARMATURE":
            return True
        if 0 < len([m for m in obj.modifiers if m.type == "ARMATURE" and m.object != None]):
            return True
    return False


def show_msgbox(message, title="", icon="INFO"):
    def draw(self, context):
        lines = message.split('\n')
        for line in lines:
            self.layout.label(text=line)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def show_report(self, *args):
    self.report({"INFO"}, " ".join(map(str, args)))


def show_report_warn(self, *args):
    self.report({"WARNING"}, " ".join(map(str, args)))


def show_report_error(self, *args):
    self.report({"ERROR"}, " ".join(map(str, args)))


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def lerp(start, end, t):
    return start + t * (end - start)


def lerp_swing(start, end, t):
    swing_factor = 0.5 - 0.5 * math.cos(math.pi * t)
    return start + (end - start) * swing_factor


def lerp_out_cubic(start, end, t):
    return start + (end - start) * (1 - (1 - t) ** 3)


def lerp_inverse(value, frm, to):
    if frm == to:
        return 1
    return (value - frm) / (to - frm)


def lerp_segments_by_distance(points, t):
    num_points = len(points)
    # 各セグメントの距離を計算
    distances = []
    total_distance = 0.0
    for i in range(num_points - 1):
        p1 = points[i]
        p2 = points[i + 1]
        distance = (p2 - p1).length
        distances.append(distance)
        total_distance += distance
    # 距離に基づいて補間位置を決定
    accumulated_distance = 0.0
    for i, distance in enumerate(distances):
        if t * total_distance <= accumulated_distance + distance:
            segment_t = (t * total_distance - accumulated_distance) / distance
            p1 = points[i]
            p2 = points[i + 1]
            return (lerp(p1, p2, segment_t), i, segment_t)
        accumulated_distance += distance
    return points[-1]


def lerp_inverse_segments_by_distance(points, idx):
    num_points = len(points)
    if num_points - 1 == idx:
        return 1
    # 各セグメントの距離を計算
    distances = []
    total_distance = 0.0
    for i in range(num_points - 1):
        p1 = points[i]
        p2 = points[i + 1]
        distance = (p2 - p1).length
        distances.append(distance)
        total_distance += distance
    accumulated_distance = 0.0
    idx_to_distance = 0.0
    for i, distance in enumerate(distances):
        if idx <= i:
            idx_to_distance = lerp(accumulated_distance, accumulated_distance + distance, i-idx)
            break
        accumulated_distance += distance
    return idx_to_distance / total_distance


def replace_leading_underscores(string, replacement_char):
    count = 0
    while count < len(string) and string[count] == '_':
        count += 1
    return replacement_char * count + string[count:]


def view_rotation(view_dir, up_dir):
    view_dir = view_dir.normalized()
    up_dir = up_dir.normalized()
    right = up_dir.cross(view_dir).normalized()
    up = view_dir.cross(right).normalized()
    # ローカル座標系の3x3行列
    rotation_matrix = Matrix((
        right,      # X軸
        up,         # Y軸
        view_dir   # Z軸
    )).transposed()  # Blenderの行列は列優先なので転置
    return rotation_matrix.to_quaternion()


def get_any_view3d_space():
    return next((area.spaces.active for area in bpy.context.screen.areas if area.type == "VIEW_3D"), None)


def callback_try(key, *args):
    cb = callbacks.get(key, lambda *args: None)
    if callable(cb):
        cb(*args)


def callback_remove(key):
    if key in callbacks:
        del callbacks[key]


def find_keymap(keymapName, itemName):
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.get(keymapName)
    kmi = km.keymap_items.get(itemName) if km != None else None
    return (km, kmi)


# --------------------------------------------------------------------------------
classes = (
    MPM_OT_SetBool,
    MPM_OT_SetBoolToggle,
    MPM_OT_SetInt,
    MPM_OT_SetSingle,
    MPM_OT_SetPointer,
    MPM_OT_SetString,
    MPM_OT_CallbackOperator,
    MPM_OT_CallPanel,
)


def register():
    register_classes(classes)


def unregister():
    unregister_classes(classes)
