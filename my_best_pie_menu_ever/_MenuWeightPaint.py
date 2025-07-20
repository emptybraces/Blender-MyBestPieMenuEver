import bpy
import importlib
import os
from bpy.app.translations import pgettext_iface as iface_
from . import (
    g,
    _Util,
    _UtilInput,
    _AddonPreferences,
)
for m in (
    g,
    _Util,
    _UtilInput,
    _AddonPreferences,
):
    importlib.reload(m)
# --------------------------------------------------------------------------------
# ウェイトペイントモードメニュー
# --------------------------------------------------------------------------------


def draw(pie, context):
    box = pie.split().box()
    box.label(text="WeightPaint Primary")
    topbar_menu = box.row(align=True)
    r = box.row()
    brush_property_box = r.box()
    utility_box = r.box()

    # icons
    r = topbar_menu
    _Util.layout_prop(r, context.object.data, "use_paint_mask", icon_only=True)
    _Util.layout_prop(r, context.object.data, "use_paint_mask_vertex", icon_only=True)
    _Util.layout_prop(r, context.object.data, "use_paint_bone_selection", icon_only=True)
    r = r.split(factor=0.2, align=True)
    _Util.layout_prop(r, _AddonPreferences.Accessor.get_ref(), "weightPaintHideBone", "HideBoneOnPaint")

    # brushes
    brush_property_box.label(text="Brush Property", icon="BRUSH_DATA")
    current_brush = context.tool_settings.weight_paint.brush
    unified_paint_settings = context.tool_settings.unified_paint_settings

    def _get_row3(layout):
        s = layout.row().split(factor=0.25, align=True)
        r1 = s.row(align=True)
        s = s.row(align=True).split(factor=0.6, align=True)
        r2 = s.row(align=True)
        r3 = s.row(align=True)
        return r1, r2, r3
    # ウェイト
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_weight else current_brush
    c = brush_property_box.column(align=True)
    r1, r2, r3 = _get_row3(c)
    _Util.layout_prop(r1, brush_property_target, "weight")
    _Util.MPM_OT_SetSingle.operator(r2, "0.0", brush_property_target, "weight", 0.0)
    _Util.MPM_OT_SetSingle.operator(r2, "0.1", brush_property_target, "weight", 0.1)
    _Util.MPM_OT_SetSingle.operator(r2, "0.5", brush_property_target, "weight", 0.5)
    _Util.MPM_OT_SetSingle.operator(r2, "1.0", brush_property_target, "weight", 1.0)
    _Util.layout_prop(r3, unified_paint_settings, "use_unified_weight")
    # size
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_size else current_brush
    r1, r2, r3 = _get_row3(c)
    _Util.layout_prop(r1, brush_property_target, "size")
    _Util.MPM_OT_SetInt.operator(r2, "50%", brush_property_target, "size", int(brush_property_target.size * 0.5))
    _Util.MPM_OT_SetInt.operator(r2, "80%", brush_property_target, "size", int(brush_property_target.size * 0.8))
    _Util.MPM_OT_SetInt.operator(r2, "150%", brush_property_target, "size", int(brush_property_target.size * 1.5))
    _Util.MPM_OT_SetInt.operator(r2, "200%", brush_property_target, "size", int(brush_property_target.size * 2.0))
    _Util.layout_prop(r3, unified_paint_settings, "use_unified_size")
    # 強さ
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_strength else current_brush
    r1, r2, r3 = _get_row3(c)
    _Util.layout_prop(r1, brush_property_target, "strength")
    _Util.MPM_OT_SetSingle.operator(r2, "0.1", brush_property_target, "strength", 0.1)
    _Util.MPM_OT_SetSingle.operator(r2, "0.5", brush_property_target, "strength", 0.5)
    _Util.MPM_OT_SetSingle.operator(r2, "1.0", brush_property_target, "strength", 1.0)
    _Util.MPM_OT_SetSingle.operator(r2, "50%", brush_property_target, "strength", brush_property_target.strength / 2)
    _Util.MPM_OT_SetSingle.operator(r2, "200%", brush_property_target, "strength", brush_property_target.strength * 2)
    _Util.layout_prop(r3, unified_paint_settings, "use_unified_strength")
    # Blends
    r1, r2, _ = _get_row3(c)
    r1.label(text="Blend")
    target_blends = ["mix", "add", "sub"]
    for i in current_brush.bl_rna.properties["blend"].enum_items:
        if i.identifier.lower() in target_blends:
            is_use = current_brush.blend == i.identifier
            _Util.MPM_OT_SetString.operator(r2, iface_(i.name), current_brush, "blend", i.identifier, depress=is_use)
    # ぼかしブラシの強さ
    blur_brush = None
    if g.is_v4_3_later():
        blender_install_dir = os.path.dirname(bpy.app.binary_path)
        if bpy.data.brushes.get("Blur") == None:
            path = os.path.join(blender_install_dir, f"{bpy.app.version[0]}.{bpy.app.version[1]}",
                                "datafiles", "assets", "brushes", "essentials_brushes-mesh_weight.blend")
            with bpy.data.libraries.load(path, link=True, assets_only=True) as (data_from, data_to):
                for i in data_from.brushes:
                    if i == "Blur":
                        data_to.brushes = [i]  # これでひとつだけロードしたことになる
                        break
        blur_brush = bpy.data.brushes["Blur"]
    else:
        for current_brush in bpy.data.brushes:
            if current_brush.use_paint_weight and current_brush.name.lower() == "blur":
                blur_brush = current_brush
                break
    if blur_brush:
        s = c.split(factor=0.4, align=True)
        r1 = s.row(align=True)
        r2 = s.row(align=True)
        s.enabled = not unified_paint_settings.use_unified_strength
        _Util.layout_prop(r1, blur_brush, "strength", "Blur Strength")
        _Util.MPM_OT_SetSingle.operator(r2, "50%", blur_brush, "strength", max(0, blur_brush.strength * 0.5))
        _Util.MPM_OT_SetSingle.operator(r2, "75%", blur_brush, "strength", max(0, blur_brush.strength * 0.75))
        _Util.MPM_OT_SetSingle.operator(r2, "150%", blur_brush, "strength", min(1, blur_brush.strength * 1.5))
        _Util.MPM_OT_SetSingle.operator(r2, "200%", blur_brush, "strength", min(1, blur_brush.strength * 2))
    # 蓄積
    s = c.split(factor=0.2, align=True)
    _Util.layout_prop(s, current_brush, "use_accumulate")

    # util
    utility_box.label(text="Utility", icon="MODIFIER")
    c = utility_box.column(align=True)
    _Util.layout_prop(c, context.space_data.overlay, "weight_paint_mode_opacity")
    r = c.row(align=True)
    r.label(text="Zero Weights")
    _Util.layout_prop(r, context.scene.tool_settings, "vertex_group_user", expand=True)
    _Util.layout_prop(c, context.space_data.overlay, "show_paint_wire")

    # apply
    box = c.box()
    box.label(text="Apply", icon="CHECKMARK")
    c = box.column(align=True)
    r = c.row(align=True)
    _Util.layout_operator(r, MPM_OT_Weight_SetWeight.bl_idname).is_mask = False
    _Util.layout_operator(r, MPM_OT_Weight_SetWeight.bl_idname, "", icon="MOD_MASK").is_mask = True
    _Util.layout_operator(r, MPM_OT_Weight_RemoveWeight.bl_idname).is_mask = False
    _Util.layout_operator(r, MPM_OT_Weight_RemoveWeight.bl_idname, "", icon="MOD_MASK").is_mask = True
    MirrorVertexGroup(c, "VGroup Mirror")
    _Util.layout_operator(c, MPM_OT_Weight_RemoveUnusedVertexGroup.bl_idname, icon="X")
    r = c.row(align=True)
    _Util.layout_operator(r, MPM_OT_Weight_MaskActiveVertexGroup.bl_idname, icon="MOD_MASK").is_invert = False
    _Util.layout_operator(r, MPM_OT_Weight_MaskActiveVertexGroup.bl_idname, "", icon="ARROW_LEFTRIGHT").is_invert = True


# --------------------------------------------------------------------------------


def MirrorVertexGroup(layout, label, factor=0.3):
    r = layout.row(align=True)
    r1, r2 = _Util.layout_split_row2(r, factor)
    r1.label(text=label)
    r1.scale_x = 0.9
    _Util.layout_operator(r2, MPM_OT_Weight_VGroupMirrorActive.bl_idname, "Active")
    _Util.layout_operator(r2, MPM_OT_Weight_VGroupMirrorActive.bl_idname, "", icon="MOD_MIRROR").use_topology = True
    _Util.layout_operator(r2, MPM_OT_Weight_VGroupMirrorBoneSelection.bl_idname, "Selected Bones")
    _Util.layout_operator(r2, MPM_OT_Weight_VGroupMirrorBoneSelection.bl_idname, "", icon="MOD_MIRROR").use_topology = True


# --------------------------------------------------------------------------------

def rename_vertexgroup(obj, target, rename):
    bpy.ops.object.vertex_group_set_active(group=rename)
    bpy.ops.object.vertex_group_remove()
    bpy.ops.object.vertex_group_set_active(group=target)
    obj.vertex_groups.active.name = rename


class MPM_OT_Weight_VGroupMirrorBoneSelection(bpy.types.Operator):
    bl_idname = "mpm.weight_mirror_vg_from_bone"
    bl_label = "Mirror VertexGroup"
    bl_description = "Create mirror VertexGroup from selected bones"
    bl_options = {"REGISTER", "UNDO"}
    use_topology: bpy.props.BoolProperty()
    replace: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        is_mesh = False
        arm_cnt = 0
        for obj in _Util.selected_objects():
            is_mesh |= obj.type == "MESH"
            if obj.type == "ARMATURE" and any(bone.select for bone in obj.data.bones):
                arm_cnt += 1
        return is_mesh and arm_cnt == 1

    def execute(self, context):
        g.force_cancel_piemenu_modal(context)
        msg = ""
        selected_bone_names = None
        for obj in _Util.selected_objects():
            if obj.type == "ARMATURE" and any(bone.select for bone in obj.data.bones):
                selected_bone_names = [bone.name for bone in obj.data.bones if bone.select]
                break
        print(selected_bone_names)
        if selected_bone_names:
            for obj in _Util.selected_objects():
                if obj.type != "MESH":
                    continue
                for bone_name in selected_bone_names:
                    if bone_name in obj.vertex_groups:
                        print("mirror!", obj, bone_name)
                        new_name, actual_name, is_replace = mirror_vgroup(obj, bone_name, self.use_topology)
                        if is_replace and self.replace:
                            rename_vertexgroup(obj, actual_name, new_name)
                            msg += f"{bone_name} -> {new_name}\n"
                        else:
                            msg += f"{bone_name} -> {actual_name}\n"
            _Util.show_msgbox(msg if msg else "Invalid Selection!", "Mirror VGroup from selected bones")
        return {"FINISHED"}


class MPM_OT_Weight_VGroupMirrorActive(bpy.types.Operator):
    bl_idname = "mpm.weight_vgroup_mirror_active"
    bl_label = "VertexGroup Mirror"
    bl_description = "Mirroring active VertexGroup"
    bl_options = {"REGISTER", "UNDO"}
    use_topology: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object != None and any(context.active_object.vertex_groups)

    def execute(self, context):
        current_mode = context.active_object.mode
        if current_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        obj = context.active_object
        target_name = obj.vertex_groups.active.name
        new_name, actural_name, is_replace = mirror_vgroup(obj, target_name, self.use_topology)
        g.force_cancel_piemenu_modal(context)
        if is_replace:
            bpy.ops.mpm.weight_vgroup_mirror_overrite_confirm("INVOKE_DEFAULT", target_name=actural_name, overwrite_name=new_name)
        else:
            msg = f"{target_name} -> {actural_name}\n"
            _Util.show_msgbox(msg if msg else "Invalid selection!", "Mirror VGroup from selected vgroup")
        if current_mode != "OBJECT":
            bpy.ops.object.mode_set(mode=current_mode)
        return {"FINISHED"}


class MPM_OT_Weight_VGroupMirrorOverwriteConfirm(bpy.types.Operator):
    bl_idname = "mpm.weight_vgroup_mirror_overrite_confirm"
    bl_label = ""
    target_name: bpy.props.StringProperty()
    overwrite_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        self.layout.label(text=f"Already exist mirrored name '{self.overwrite_name}' Are you overwrite?")

    def cancel(self, context):
        pass

    def execute(self, context):
        obj = context.active_object
        active_name = obj.vertex_groups.active.name
        rename_vertexgroup(obj, active_name, self.overwrite_name)
        _Util.show_msgbox(f"{self.target_name} -> {self.overwrite_name}\n", "Mirror VGroup from selected vgroup")
        return {"FINISHED"}


# --------------------------------------------------------------------------------


def mirror_vgroup(obj, name, use_topology):
    new_name = name
    # 中間のリプレース
    if ".L." in new_name:
        new_name = new_name.replace(".L.", ".R.")
    elif ".R." in new_name:
        new_name = new_name.replace(".R.", ".L.")
    elif ".l." in new_name:
        new_name = new_name.replace(".l.", ".r.")
    elif ".r." in new_name:
        new_name = new_name.replace(".r.", ".l.")
    # 接尾辞のリプレース
    postfix = name[-2:]
    if postfix == ".L":
        new_name = new_name[:-2] + ".R"
    elif postfix == ".R":
        new_name = new_name[:-2] + ".l"
    elif postfix == ".l":
        new_name = new_name[:-2] + ".r"
    elif postfix == ".r":
        new_name = new_name[:-2] + ".l"

    if new_name == name:
        new_name = new_name + "_mirror"

    _Util.select_active(obj)
    bpy.ops.object.vertex_group_set_active(group=name)
    bpy.ops.object.vertex_group_copy()
    bpy.ops.object.vertex_group_mirror(use_topology=use_topology)
    is_duplicate = new_name in obj.vertex_groups
    obj.vertex_groups.active.name = new_name
    return new_name, obj.vertex_groups.active.name, is_duplicate
# --------------------------------------------------------------------------------


class MPM_OT_Weight_RemoveUnusedVertexGroup(bpy.types.Operator):
    bl_idname = "mpm.weight_vgroup_remove_unused"
    bl_label = "Remove Unused VGroup"
    bl_description = "Bulk remove VertexGroups that do not have weights set"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and any(context.active_object.vertex_groups)

    def execute(self, context):
        g.force_cancel_piemenu_modal(context)
        current_mode = context.active_object.mode
        if current_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        obj = bpy.context.active_object
        remove_groups = []
        for vg in obj.vertex_groups:
            has_weight = False
            for vertex in obj.data.vertices:
                for group in vertex.groups:
                    if group.group == vg.index:
                        has_weight = True
                        break
                if has_weight:
                    break
            # ウェイトが存在しない頂点グループ
            if not has_weight:
                remove_groups.append(vg)

        # 削除
        if 0 < len(remove_groups):
            _Util.show_msgbox("\n".join(["Remove: " + i.name for i in remove_groups]), "Remove Unused Vetex Group")
            for vg in remove_groups:
                _Util.show_report(self, f"Remove: {vg.name}")
                obj.vertex_groups.remove(vg)
        else:
            _Util.show_msgbox("Not found unused vertex groups.", "Remove Unused Vetex Group")

        if current_mode != "OBJECT":
            bpy.ops.object.mode_set(mode=current_mode)
        return {"FINISHED"}

# --------------------------------------------------------------------------------


class MPM_OT_Weight_MaskActiveVertexGroup(bpy.types.Operator):
    bl_idname = "mpm.weight_mask_active_vgroup"
    bl_label = "Mask Active Vgroup"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Mask only the vertices with the current weight set"
    is_invert: bpy.props.BoolProperty()

    def execute(self, context):
        context.object.data.use_paint_mask_vertex = True
        _Util.deselect_all(context)
        bpy.ops.object.vertex_group_select()
        if self.is_invert:
            bpy.ops.paint.vert_select_all(action='INVERT')
        return {"FINISHED"}

# --------------------------------------------------------------------------------


class MPM_OT_Weight_SetWeight(bpy.types.Operator):
    bl_idname = "mpm.weight_set"
    bl_label = "Set Weight"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Weights set. Option1: mask only"
    is_mask: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object != None and any(context.active_object.vertex_groups)

    def execute(self, context):
        if self.is_mask:
            bpy.context.object.data.use_paint_mask_vertex = True
        bpy.ops.paint.weight_set()
        if self.is_mask:
            bpy.context.object.data.use_paint_mask_vertex = False
        return {"FINISHED"}


class MPM_OT_Weight_RemoveWeight(bpy.types.Operator):
    bl_idname = "mpm.weight_remove"
    bl_label = "Delete Weight"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Weights remove. Option1: mask only"
    is_mask: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object != None and any(context.active_object.vertex_groups)

    def execute(self, context):
        vg = context.active_object.vertex_groups.active
        if self.is_mask:
            vg.remove([v.index for v in context.active_object.data.vertices if v.select])
        else:
            vg.remove([v.index for v in context.active_object.data.vertices])
        return {"FINISHED"}
# --------------------------------------------------------------------------------


def on_update_HideBoneOnPaint(value):
    # スクリプトロード時の登録クラッシュ回避
    def __safe_start_modal():
        bpy.ops.mpm.weight_hide_bone_on_paint_monitor_modal("INVOKE_DEFAULT")
        return None

    if value:
        bpy.app.timers.register(__safe_start_modal, first_interval=0.2)
    else:
        MPM_OT_Weight_HideBoneOnPaintMonitorModal.is_cancelled = True


class MPM_OT_Weight_HideBoneOnPaintMonitorModal(bpy.types.Operator):
    bl_idname = "mpm.weight_hide_bone_on_paint_monitor_modal"
    bl_label = ""
    is_started = False
    is_cancelled = False

    def invoke(self, context, event):
        cls = self.__class__
        if cls.is_started:
            return {"CANCELLED"}
        cls.is_cancelled = False
        self.is_press = False
        # self.input = _UtilInput.Monitor()

        # timer起動だとcontextから直接辿れない
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == "VIEW_3D":
                    # print("start")
                    cls.is_started = True
                    context.window_manager.modal_handler_add(self)
                    return {"RUNNING_MODAL"}
        else:
            return {"CANCELLED"}

    def modal(self, context, e):
        if self.__class__.is_cancelled or not _AddonPreferences.Accessor.get_weight_paint_hide_bone():
            # print("cancelled")
            self.__class__.is_started = False
            return {"CANCELLED"}
        self.mx = e.mouse_x
        self.my = e.mouse_y
        # self.input.update(e, "LEFTMOUSE")
        if context.mode == "PAINT_WEIGHT":
            if e.type == "LEFTMOUSE" and e.value == "PRESS" and not (e.ctrl and e.shift):  # ボーン選択操作のみ条件排除
                self.is_press = True
                self.show_bone(context, False)
            # Release呼ばれないのでこれ
            elif self.is_press and e.type == "MOUSEMOVE" and e.value == "NOTHING":
                self.is_press = False
                self.show_bone(context, True)
        return {"PASS_THROUGH"}

    def show_bone(self, context, is_on):
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == "VIEW_3D":
                    x, y = area.x, area.y
                    w, h = area.width, area.height
                    if x <= self.mx < x + w and y <= self.my < y + h:
                        overlay = getattr(area.spaces.active, "overlay", None)
                        if overlay:
                            overlay.show_bones = is_on
# --------------------------------------------------------------------------------


classes = (
    MPM_OT_Weight_VGroupMirrorBoneSelection,
    MPM_OT_Weight_VGroupMirrorActive,
    MPM_OT_Weight_VGroupMirrorOverwriteConfirm,
    MPM_OT_Weight_RemoveUnusedVertexGroup,
    MPM_OT_Weight_MaskActiveVertexGroup,
    MPM_OT_Weight_SetWeight,
    MPM_OT_Weight_RemoveWeight,
    MPM_OT_Weight_HideBoneOnPaintMonitorModal,


)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
