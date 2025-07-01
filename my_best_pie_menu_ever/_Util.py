if "bpy" in locals():
    import importlib
    importlib.reload(_UtilBlf)
    importlib.reload(g)
else:
    from . import _UtilBlf
    from . import g
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
    bl_options = {"UNDO"}
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
    bl_options = {"UNDO"}
    value: bpy.props.BoolProperty()

    @staticmethod
    def operator(layout, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetBool.bl_idname, text, targetObj, propName, value, icon, depress, isActive)


class MPM_OT_SetBoolToggle(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "mpm.util_set_invert"
    bl_label = ""
    bl_options = {"UNDO"}
    value: bpy.props.BoolProperty()

    @staticmethod
    def operator(layout, text, targetObj, propName, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetBoolToggle.bl_idname, text, targetObj, propName, None, icon, depress, isActive)


class MPM_OT_SetInt(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "mpm.util_set_int"
    bl_label = ""
    bl_options = {"UNDO"}
    value: bpy.props.IntProperty()

    @staticmethod
    def operator(layout, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetInt.bl_idname, text, targetObj, propName, value, icon, depress, isActive)


class MPM_OT_SetSingle(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "mpm.util_set_single"
    bl_label = ""
    bl_options = {"UNDO"}
    value: bpy.props.FloatProperty()

    @staticmethod
    def operator(layout, text, targetObj, propName, value=None, icon="NONE", depress=None, isActive=None):
        MPM_OT_SetterBase.operator(layout, MPM_OT_SetSingle.bl_idname, text, targetObj, propName, value, icon, depress, isActive)


class MPM_OT_SetString(MPM_OT_SetterBase, bpy.types.Operator):
    bl_idname = "mpm.util_set_string"
    bl_label = ""
    bl_options = {"UNDO"}
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
    bl_label = "Temporary operator"
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


class MPM_StackableViewportUI:
    mx, my = 0.0, 0.0

    def init_draw_class_instance(self, context, is_multiple, id, drawModalCls):
        self.id = id
        if not (modals := stackable_draw_modals.get(self.id)):
            context.window_manager.modal_handler_add(self)
            if modals is None:
                stackable_draw_modals[self.id] = []
            if not is_multiple:
                stackable_draw_modals[self.id].append(drawModalCls(self.id))
        if is_multiple:
            stackable_draw_modals[self.id].append(drawModalCls(self.id))
        g.force_cancel_piemenu_modal(context)

    def modal(self, context, event):
        context.area.tag_redraw()  # draw2dを毎フレーム呼ぶため。
        cls = self.__class__
        cls.mx = event.mouse_x
        cls.my = event.mouse_y
        modals = stackable_draw_modals.get(self.id)
        if not modals:
            g.space_view_command_display_stack_remove(self.id)
            return self.cancel(context)
        g.space_view_command_display_stack_sety(self.id, (len(modals)-1) * (_UtilBlf.LABEL_SIZE_Y * 2))
        return {}

    def cancel(self, context):
        return {"CANCELLED"}


class MPM_ModalMonitor:

    def __init__(self):
        self.interrupt = False
        self.count = 0.0
        bpy.app.timers.register(self._monitor)
        bpy.app.handlers.load_pre.append(self.on_loadpre)

    def reset_timer(self):
        self.count = 0

    def _monitor(self):
        if self.interrupt:
            return None
        self.count += 0.1
        # print(self.count)
        # if 60 < self.count:
        #     self.cancel()
        #     return None  # 終了
        return 0.1

    def cancel(self):
        self.interrupt = True
        if self.on_loadpre in bpy.app.handlers.load_pre:
            bpy.app.handlers.load_pre.remove(self.on_loadpre)

    def on_loadpre(self, a, b):
        self.cancel()


class MPM_StackableModalMonitor(MPM_ModalMonitor):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.is_current_modal = False
        self.current_focus_type = ""
        self.target_area = bpy.context.area

    def try_cancel(self):
        if not self in stackable_draw_modals.get(self.id, []):
            self.cancel()
            return True

    def prepare_current_state(self):
        if self.is_current_modal and bpy.context.area == self.target_area:
            self.is_current_modal = False
            self.current_focus_type = ""

    def cancel(self):
        super().cancel()
        if self in stackable_draw_modals.get(self.id, []):
            stackable_draw_modals[self.id].remove(self)


stackable_draw_modals: dict[str, list[MPM_ModalMonitor]] = {}

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


def has_selected_verts(context):
    if context.mode == "EDIT_MESH":
        obj = context.edit_object
        return obj and obj.type == "MESH" and any(e.select for e in bmesh.from_edit_mesh(obj.data).verts)
    else:
        obj = context.active_object
        return obj and obj.type == "MESH" and any(v.select for v in obj.data.vertices)


def has_selected_verts_least_two(context):
    verts = None
    count = 0
    if context.mode == "EDIT_MESH":
        obj = context.edit_object
        if not obj or obj.type != "MESH":
            return False
        verts = bmesh.from_edit_mesh(obj.data).verts
    else:
        obj = context.active_object
        if not obj or obj.type != "MESH":
            return False
        verts = obj.data.vertices
    for v in verts:
        if v.select:
            count += 1
            if count >= 2:
                return True
    return False


def has_selected_edges(context):
    if context.mode == "EDIT_MESH":
        obj = context.edit_object
        return obj and obj.type == "MESH" and any(e.select for e in bmesh.from_edit_mesh(obj.data).edges)
    else:
        obj = context.active_object
        return obj and obj.type == "MESH" and any(v.select for v in obj.data.edges)


def has_selected_edges_least_two(context):
    edges = None
    count = 0
    if context.mode == "EDIT_MESH":
        obj = context.edit_object
        if not obj or obj.type != "MESH":
            return False
        edges = bmesh.from_edit_mesh(obj.data).edges
    else:
        obj = context.active_object
        if not obj or obj.type != "MESH":
            return False
        edges = obj.data.edges
    for e in edges:
        if e.select:
            count += 1
            if count >= 2:
                return True
    return False


def has_active_vgroup(context):
    obj = context.object
    return obj and obj.type == "MESH" and obj.vertex_groups.active != None


def has_active_image(context):
    return None != getattr(context.area.spaces.active, "image", None)


def deselect_all(context):
    if context.mode == "EDIT_MESH":
        obj = bpy.context.edit_object
        mesh = bmesh.from_edit_mesh(obj.data)
        for v in mesh.verts:
            v.select_set(False)
        for e in mesh.edges:
            v.select_set(False)
        bmesh.update_edit_mesh(obj.data)
    elif context.mode == "PAINT_WEIGHT":
        bpy.ops.paint.vert_select_all(action="DESELECT")
    else:
        bpy.ops.object.select_all(action="DESELECT")


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


def layout_operator(layout, opid, text=None, isActive=None, depress=False, icon="NONE", scale_x=1.0):
    if isActive != None:
        layout = layout.row()
        layout.scale_x = scale_x
        layout.enabled = isActive
    return layout.operator(opid, text=text, depress=depress, icon=icon)


def layout_for_mirror(layout):
    row = layout.row(align=True)
    row.label(icon="MOD_MIRROR")
    sub = row.row(align=True)
    sub.scale_x = 0.9
    return row, sub


def layout_split_row2(layout, factor1, alignSplit=True, align1=True, align2=True):
    split = layout.row().split(factor=factor1, align=alignSplit)
    c1 = split.row(align=align1)
    rest = split.row(align=align2)
    return c1, rest


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
    for obj in selected_objects():
        if obj.type == "ARMATURE":
            return True
        elif obj.find_armature():
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


def interp_catmull_rom(points, t):
    def __calc(p0, p1, p2, p3, t):
        t2 = t * t
        t3 = t2 * t
        return 0.5 * (
            (2 * p1) +
            (-p0 + p2) * t +
            (2*p0 - 5*p1 + 4*p2 - p3) * t2 +
            (-p0 + 3*p1 - 3*p2 + p3) * t3
        )
    count = len(points)
    if count < 2:
        raise ValueError("少なくとも2点必要です")
    t = max(0.0, min(1.0, t))
    # 区間数（例: 4点 → 3区間）
    num_segments = count - 1

    # t を区間にマッピング
    segment_f = t * num_segments
    segment_index = int(segment_f)
    local_t = segment_f - segment_index

    # インデックス補正（境界で止める）
    i0 = max(segment_index - 1, 0)
    i1 = segment_index
    i2 = min(segment_index + 1, count - 1)
    i3 = min(segment_index + 2, count - 1)
    return __calc(points[i0], points[i1], points[i2], points[i3], local_t)


def interp_linear(points, t):
    count = len(points)
    if count < 2:
        raise ValueError("少なくとも2点必要です")

    num_segments = count - 1
    segment_f = t * num_segments
    segment_index = int(segment_f)
    local_t = segment_f - segment_index

    i0 = segment_index
    i1 = min(segment_index + 1, count - 1)

    return points[i0].lerp(points[i1], local_t)


def interp_slerp_quaternion(quats, t):
    if len(quats) < 2:
        raise ValueError("少なくとも2つのQuaternionが必要です")

    t = max(0.0, min(1.0, t))  # クランプ
    num_segments = len(quats) - 1

    segment_f = t * num_segments
    segment_index = int(segment_f)
    local_t = segment_f - segment_index

    i0 = segment_index
    i1 = min(segment_index + 1, len(quats) - 1)

    q0 = quats[i0].copy()
    q1 = quats[i1]

    return q0.slerp(q1, local_t)


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


def edge_center_point(edge):
    return (edge.verts[0].co + edge.verts[1].co) / 2


def edge_center_length(co1, co2):
    center = (co1 + co2) * 0.5
    length = (co1 - co2).length
    return center, length


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


def sign(v: float) -> int:
    return 1 if v > 0 else -1 if v < 0 else 0


def find_mirror_vertex(bm, verts, axis="X", threshold=1e-5):
    axis_index = 0 if axis == "X" else 1 if axis == "Y" else 2
    mirror_positions = []
    for v in verts:
        co = v.co.copy()
        co[axis_index] *= -1
        mirror_positions.append((co, sign(co[axis_index])))

    r = []
    for v in bm.verts:
        v_sign = sign(v.co[axis_index])
        for i in reversed(range(len(mirror_positions))):
            mirror_co, mirror_sign = mirror_positions[i]
            if v_sign != mirror_sign:
                continue
            if (v.co - mirror_co).length < threshold:
                r.append(v)
                del mirror_positions[i]
                break
    return r


def find_mirror_edges(bm, edges, axis="X", threshold=1e-5):
    axis_index = 0 if axis == "X" else 1 if axis == "Y" else 2
    mirror_positions = []
    for e in edges:
        co1 = e.verts[0].co.copy()
        co2 = e.verts[1].co.copy()
        co1[axis_index] *= -1
        co2[axis_index] *= -1
        mirror_positions.append((co1, co2))
    r = []
    for e in bm.edges:
        ev1 = e.verts[0].co
        ev2 = e.verts[1].co

        for i in reversed(range(len(mirror_positions))):
            mc1, mc2 = mirror_positions[i]
            if sign(ev1[axis_index]) != sign(mc1[axis_index]) and \
               sign(ev2[axis_index]) != sign(mc2[axis_index]):
                continue
            dest_center, dest_length = edge_center_length(ev1, ev2)
            mirrir_center, mirrir_length = edge_center_length(mc1, mc2)
            if (dest_center - mirrir_center).length < threshold and abs(dest_length - mirrir_length) < threshold:
                r.append(e)
                del mirror_positions[i]
                break
    return r


def find_mirror_edges_fast(bm, edges, axis="X", threshold=1e-5, precision=5):
    def _hash_key(center: Vector, length: float, precision=5):
        return (
            round(center.x, precision),
            round(center.y, precision),
            round(center.z, precision),
            round(length, precision)
        )
    axis_index = 0 if axis == "X" else 1 if axis == "Y" else 2
    mirror_dict = {}
    for e in edges:
        co1 = e.verts[0].co.copy()
        co2 = e.verts[1].co.copy()
        co1[axis_index] *= -1
        co2[axis_index] *= -1
        center, length = edge_center_length(co1, co2)
        key = _hash_key(center, length, precision)
        mirror_dict[key] = e

    r = []
    for e in bm.edges:
        ev1 = e.verts[0].co
        ev2 = e.verts[1].co
        center, length = edge_center_length(ev1, ev2)
        key = _hash_key(center, length, precision)
        if key in mirror_dict:
            r.append(e)
            del mirror_dict[key]  # 重複防止
    return r


def unselected_bm(bm, v=True, e=True, f=True):
    if v:
        for i in bm.verts:
            i.select = False
    if e:
        for i in bm.edges:
            i.select = False
    if f:
        for i in bm.faces:
            i.select = False


class Temp:
    tmpset1 = set()
    tmpset2 = set()

    @classmethod
    def set1_clear(cls, e):
        cls.tmpset1.clear()
        return cls.tmpset1

    @classmethod
    def set2_clear(cls, e):
        cls.tmpset2.clear()
        return cls.tmpset2

    @classmethod
    def set1_clear_set(cls, e):
        cls.tmpset1.clear()
        cls.tmpset1.set(e)
        return cls.tmpset1

    @classmethod
    def set2_clear_set(cls, e):
        cls.tmpset2.clear()
        cls.tmpset2.set(e)
        return cls.tmpset2

    @classmethod
    def set1_clear_update(cls, e):
        cls.tmpset1.clear()
        cls.tmpset1.update(e)
        return cls.tmpset1

    @classmethod
    def set2_clear_update(cls, e):
        cls.tmpset2.clear()
        cls.tmpset2.update(e)
        return cls.tmpset2

    @classmethod
    def intersect_sets(cls, set1, set2):
        cls.tmpset1.clear()
        cls.tmpset1.update(set1)
        cls.tmpset2.clear()
        cls.tmpset2.update(set2)
        return cls.tmpset1 & cls.tmpset2


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
