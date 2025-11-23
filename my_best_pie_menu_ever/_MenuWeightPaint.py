if "bpy" in locals():
    import importlib
    for m in (
        _Util,
        g,
        _MenuPose,
        _UtilInput,
        _AddonPreferences,
    ):
        importlib.reload(m)
else:
    import bpy
    from . import (
        _Util,
        g,
        _MenuPose,
        _UtilInput,
        _AddonPreferences,
    )
import os
from bpy.app.translations import pgettext_iface as iface_

# --------------------------------------------------------------------------------
# ウェイトペイントモードメニュー
# --------------------------------------------------------------------------------
blur_brush = None
has_selected_verts = False


def draw(pie, context):
    global has_selected_verts
    has_selected_verts = _Util.has_selected_verts(context)
    box = pie.split().box()
    box.label(text="WeightPaint Primary")
    topbar_menu = box.row(align=True)
    r = box.row()
    brush_property_box = r.box()
    utility_box = r.box()
    third_party_box = r.box()

    # icons
    r = topbar_menu
    _Util.layout_prop(r, context.object.data, "use_paint_mask", icon_only=True)
    _Util.layout_prop(r, context.object.data, "use_paint_mask_vertex", icon_only=True)
    _Util.layout_prop(r, context.object.data, "use_paint_bone_selection", icon_only=True)
    r = r.split(factor=0.2, align=True)
    _Util.layout_prop(r, _AddonPreferences.Accessor.get_ref(), "weightPaintHideBone", "HideBoneOnPaint")
    # brushes
    brush_property_box.label(text="Current Brush Property", icon="BRUSH_DATA")
    current_brush = context.tool_settings.weight_paint.brush
    unified_paint_settings = getattr(context.tool_settings, "unified_paint_settings", None) \
        or getattr(context.tool_settings.weight_paint, "unified_paint_settings", None)  # v5.0からunified_paint_settingsの場所が変わった

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
    # 蓄積
    # s = c.split(factor=0.2, align=True)
    r = c.row(align=True)
    r.alignment = "LEFT"
    _Util.layout_prop(r, current_brush, "use_accumulate")
    # ミラートポロジ
    _Util.layout_prop(r, context.object.data, "use_mirror_topology")
    # 自動正規化
    _Util.layout_prop(r, context.scene.tool_settings, "use_auto_normalize")

    # ぼかしブラシの強さ
    global blur_brush
    if not blur_brush:
        path = os.path.join(bpy.utils.system_resource("DATAFILES"), "assets", "brushes", "essentials_brushes-mesh_weight.blend")
        with bpy.data.libraries.load(path, link=True, assets_only=True) as (data_from, data_to):
            for i in data_from.brushes:
                if i == "Blur":
                    data_to.brushes = [i]  # これでひとつだけロードしたことになる
                    break
        blur_brush = bpy.data.brushes["Blur", path]
    if blur_brush:
        # s = c.row().split(factor=0.05)
        # s.row()
        # c = s.row().column()
        c.separator(factor=2.5)
        c.label(text="Blur Brush", icon="BRUSH_DATA")
        s = c.split(factor=0.4, align=True)
        r1 = s.row(align=True)
        r2 = s.row(align=True)
        s.enabled = not unified_paint_settings.use_unified_strength
        _Util.layout_prop(r1, blur_brush, "strength", "Blur Strength")
        _Util.MPM_OT_SetSingle.operator(r2, "50%", blur_brush, "strength", max(0, blur_brush.strength * 0.5))
        _Util.MPM_OT_SetSingle.operator(r2, "75%", blur_brush, "strength", max(0, blur_brush.strength * 0.75))
        _Util.MPM_OT_SetSingle.operator(r2, "150%", blur_brush, "strength", min(1, blur_brush.strength * 1.5))
        _Util.MPM_OT_SetSingle.operator(r2, "200%", blur_brush, "strength", min(1, blur_brush.strength * 2))

    # util
    utility_box.label(text="Utility", icon="MODIFIER")
    c = utility_box.column(align=True)
    _Util.layout_prop(c, context.space_data.overlay, "weight_paint_mode_opacity")
    r = c.row(align=True)
    r.label(text="Zero Weights")
    _Util.layout_prop(r, context.scene.tool_settings, "vertex_group_user", expand=True)
    _Util.layout_prop(c, context.space_data.overlay, "show_paint_wire")
    r = c.row(align=True)
    r.label(text="PoseBone Use Mirror", icon="MOD_MIRROR")
    _Util.layout_operator(r, MPM_OT_Weight_PoseBoneUseMirror.bl_idname, "ON").is_use = True
    _Util.layout_operator(r, MPM_OT_Weight_PoseBoneUseMirror.bl_idname, "OFF").is_use = False
    _Util.layout_operator(c, MPM_OT_Weight_PoseBoneMirrorSelect.bl_idname)
    _Util.layout_operator(c, MPM_OT_Weight_InspectSelectedVertices.bl_idname, isActive=has_selected_verts, icon="VIEWZOOM")

    # apply
    box = c.box()
    box.label(text="Apply", icon="CHECKMARK")
    c = box.column(align=True)
    r = c.row(align=True)
    _Util.layout_operator(r, MPM_OT_Weight_SetWeight.bl_idname).mode = 0
    _Util.layout_operator(r, MPM_OT_Weight_SetWeight.bl_idname, "", icon="MOD_MASK").mode = 1
    _Util.layout_operator(r, MPM_OT_Weight_SetWeight.bl_idname, "", icon="CLIPUV_HLT").mode = 2
    _Util.layout_operator(r, MPM_OT_Weight_RemoveWeight.bl_idname).mode = 0
    _Util.layout_operator(r, MPM_OT_Weight_RemoveWeight.bl_idname, "", icon="MOD_MASK").mode = 1
    _Util.layout_operator(r, MPM_OT_Weight_RemoveWeight.bl_idname, "", icon="CLIPUV_HLT").mode = 2
    MirrorVertexGroup(c, "VGroup Mirror")
    _Util.layout_operator(c, MPM_OT_Weight_RemoveUnusedVertexGroup.bl_idname, icon="X")
    r = c.row(align=True)
    _Util.layout_operator(r, MPM_OT_Weight_MaskNonZeroVGroup.bl_idname, icon="MOD_MASK").is_invert = False
    _Util.layout_operator(r, MPM_OT_Weight_MaskNonZeroVGroup.bl_idname, "", icon="CLIPUV_HLT").is_invert = True
    _Util.layout_operator(c, MPM_OT_Weight_GradientExpand.bl_idname, icon="COLORSET_04_VEC")
    r = c.row(align=True)
    r.label(text="Hide L/R Bones", icon="HIDE_ON")
    _Util.layout_operator(r, MPM_OT_Weight_HideLeftRightBones.bl_idname, "Left").mode = "LEFT"
    _Util.layout_operator(r, MPM_OT_Weight_HideLeftRightBones.bl_idname, "Right").mode = "RIGHT"

    # 3rdparty
    _MenuPose.draw_layout_3rdparty(context, third_party_box)


# --------------------------------------------------------------------------------


def MirrorVertexGroup(layout, label, factor=0.3):
    r = layout.row(align=True)
    r1, r2 = _Util.layout_split_row2(r, factor)
    r1.label(text=label)
    r1.scale_x = 0.9
    _Util.layout_operator(r2, MPM_OT_Weight_VGroupMirrorActive.bl_idname, "Active")
    _Util.layout_operator(r2, MPM_OT_Weight_VGroupMirrorActive.bl_idname, "", icon="MESH_DATA").use_topology = True
    _Util.layout_operator(r2, MPM_OT_Weight_VGroupMirrorBoneSelection.bl_idname, "Selected Bones")
    _Util.layout_operator(r2, MPM_OT_Weight_VGroupMirrorBoneSelection.bl_idname, "", icon="MESH_DATA").use_topology = True


# --------------------------------------------------------------------------------

def rename_vertexgroup(obj, target, rename):
    bpy.ops.object.vertex_group_set_active(group=rename)
    bpy.ops.object.vertex_group_remove()
    bpy.ops.object.vertex_group_set_active(group=target)
    obj.vertex_groups.active.name = rename


class MPM_OT_Weight_VGroupMirrorBoneSelection(bpy.types.Operator):
    bl_idname = "mpm.weight_mirror_vg_from_bone"
    bl_label = "Mirror VertexGroup"
    bl_description = "Create mirror VertexGroup from selected bones. Option: Use Topology"
    bl_options = {"REGISTER", "UNDO"}
    use_topology: bpy.props.BoolProperty()
    replace: bpy.props.BoolProperty()

    @classmethod
    def get_bone_for_select(cls, obj):
        if g.is_v5_0_later():
            return obj.pose.bones
        else:
            return obj.data.bones

    @classmethod
    def poll(cls, context):
        is_mesh = False
        arm_cnt = 0
        for obj in _Util.selected_objects():
            is_mesh |= obj.type == "MESH"
            if obj.type == "ARMATURE" and any(bone.select for bone in MPM_OT_Weight_VGroupMirrorBoneSelection.get_bone_for_select(obj)):
                arm_cnt += 1

        return is_mesh and arm_cnt == 1

    def execute(self, context):
        g.force_cancel_piemenu_modal(context)
        msg = ""
        selected_bone_names = None
        cls = MPM_OT_Weight_VGroupMirrorBoneSelection
        for obj in _Util.selected_objects():
            if obj.type == "ARMATURE" and any(bone.select for bone in cls.get_bone_for_select(obj)):
                selected_bone_names = [bone.name for bone in cls.get_bone_for_select(obj) if bone.select]
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
    bl_description = "Mirroring active VertexGroup. Option: Use Topology"
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


class MPM_OT_Weight_MaskNonZeroVGroup(bpy.types.Operator):
    bl_idname = "mpm.weight_mask_nonzero_vgroup"
    bl_label = "Non-Zero Weight Mask"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Mask only the current weight set. Option: Invert mask"
    is_invert: bpy.props.BoolProperty()

    def execute(self, context):
        context.object.data.use_paint_mask_vertex = True
        _Util.deselect_all(context)
        # 登録されていれば選択されてしまう。
        # bpy.ops.object.vertex_group_select()
        # if self.is_invert:
        #     bpy.ops.paint.vert_select_all(action="INVERT")
        # ウェイトが0より大きい頂点だけ選択
        vg = context.object.vertex_groups.active
        for v in context.object.data.vertices:
            try:
                weight = vg.weight(v.index)
                if self.is_invert and weight <= 0.0:
                    v.select = True
                elif not self.is_invert and 0.0 < weight:
                    v.select = True
            # 頂点グループに登録されていない場合
            except RuntimeError:
                if self.is_invert:
                    v.select = True
        return {"FINISHED"}


class MPM_OT_Weight_InspectSelectedVertices(bpy.types.Operator):
    bl_idname = "mpm.weight_inspect_selected_vertices"
    bl_label = "Inspect Selected Verts"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Checks which vertex groups the selected vertices are assigned to"

    def invoke(self, context, event):
        g.force_cancel_piemenu_modal(context)
        obj = context.object
        self.last_active_vg = obj.vertex_groups.active
        self.assigned = set()
        arm = obj.find_armature()
        dbones = [vg.name
                  for bone in arm.data.bones
                  if bone.use_deform and (vg := obj.vertex_groups.get(bone.name))
                  ] if arm else []
        if obj.mode == "EDIT":
            import bmesh
            bm = bmesh.from_edit_mesh(obj.data)
            verts = [obj.data.vertices[v.index] for v in bm.verts if v.select]
        else:
            verts = [v for v in obj.data.vertices if v.select]
        for v in verts:
            for group in v.groups:
                vg = obj.vertex_groups[group.group]
                if 0.0 < group.weight:
                    self.assigned.add((vg, vg.name in dbones))
        self.last_states = obj.data.use_paint_mask, obj.data.use_paint_mask_vertex, obj.data.use_paint_bone_selection
        obj.data.use_paint_mask_vertex = True
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        r = self.layout.row(align=False)
        c = r.column(align=True)
        for vg, is_deform in sorted(self.assigned, key=lambda x: (x[1], x[0].name)):
            r = c.row(align=True)
            _Util.MPM_OT_CallbackOperator.operator(r, f"{vg.name}", self.bl_idname + vg.name + "_select_vg",
                                                   self.select_vg, (context, vg), icon="BONE_DATA" if is_deform else "GROUP_VERTEX")
            _Util.MPM_OT_CallbackOperator.operator(r, "", self.bl_idname + vg.name + "_remove_from_vg",
                                                   self.remove_from_vg, (context, vg), icon="X")

    def select_vg(self, context, vg):
        context.object.vertex_groups.active = vg

    def remove_from_vg(self, context, vg):
        obj = context.object
        # 編集モード時は頂点グループの削除ができない
        if obj.mode == "EDIT":
            bpy.ops.object.mode_set(mode="OBJECT")
            vg.remove([v.index for v in obj.data.vertices if v.select])
            bpy.ops.object.mode_set(mode="EDIT")
        else:
            vg.remove([v.index for v in obj.data.vertices if v.select])
        self.assigned.discard((vg, True))
        self.assigned.discard((vg, False))

    def execute(self, context):
        self.finish(context)
        return {"FINISHED"}

    def cancel(self, context):
        self.finish(context)
        context.object.vertex_groups.active = self.last_active_vg

    def finish(self, context):
        _Util.MPM_OT_CallbackOperator.clear()
        obj = context.object
        if self.last_states[0]:
            obj.data.use_paint_mask = self.last_states[0]
        elif self.last_states[1]:
            obj.data.use_paint_mask_vertex = self.last_states[1]
        elif self.last_states[2]:
            obj.data.use_paint_bone_selection = self.last_states[2]


# --------------------------------------------------------------------------------


class MPM_OT_Weight_SetWeight(bpy.types.Operator):
    bl_idname = "mpm.weight_set"
    bl_label = "Set Weight"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Weights set. Option1: Selected only. Option2: Unselected only."
    mode: bpy.props.IntProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.active_object != None and any(context.active_object.vertex_groups)

    def execute(self, context):
        tmp = bpy.context.object.data.use_paint_mask_vertex
        if self.mode == 0:  # 全て
            bpy.context.object.data.use_paint_mask_vertex = False
            bpy.ops.paint.weight_set()
        if self.mode == 1:  # 選択のみ
            bpy.context.object.data.use_paint_mask_vertex = True
            bpy.ops.paint.weight_set()
        else:  # 反転選択のみ
            bpy.context.object.data.use_paint_mask_vertex = True
            bpy.ops.paint.vert_select_all(action="INVERT")
            bpy.ops.paint.weight_set()
            bpy.ops.paint.vert_select_all(action="INVERT")

        bpy.context.object.data.use_paint_mask_vertex = tmp
        return {"FINISHED"}


class MPM_OT_Weight_RemoveWeight(bpy.types.Operator):
    bl_idname = "mpm.weight_remove"
    bl_label = "Delete Weight"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Weights remove. Option1: Selected only. Option2: Unselected only."
    mode: bpy.props.IntProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.active_object != None and any(context.active_object.vertex_groups)

    def execute(self, context):
        vg = context.active_object.vertex_groups.active
        if self.mode == 0:  # 全て
            vg.remove([v.index for v in context.active_object.data.vertices])
        elif self.mode == 1:  # 選択のみ
            vg.remove([v.index for v in context.active_object.data.vertices if v.select])
        else:  # 反転選択のみ
            vg.remove([v.index for v in context.active_object.data.vertices if not v.select])

        return {"FINISHED"}
# --------------------------------------------------------------------------------


def on_update_HideBoneOnPaint(value):
    # スクリプトロード時の登録クラッシュ回避
    def __safe_start_modal():
        bpy.ops.mpm.weight_hide_bone_on_paint_monitor_modal("INVOKE_DEFAULT")
        return None

    if value:
        bpy.app.timers.register(__safe_start_modal, first_interval=0.2, persistent=True)
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


class MPM_OT_Weight_PoseBoneUseMirror(bpy.types.Operator):
    bl_idname = "mpm.weight_pose_bone_use_mirror"
    bl_label = "Update Pose Bone Use Mirror"
    bl_options = {"UNDO"}
    bl_description = "Update the pose bone use_mirror_x property"
    is_use: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        for obj in _Util.selected_objects():
            if obj.type == "ARMATURE":
                return True
        return False

    def execute(self, context):
        original_objects = _Util.selected_objects()
        original_active = context.view_layer.objects.active
        context.view_layer.objects.active = next((i for i in _Util.selected_objects() if i.type == "ARMATURE"), None)
        if context.view_layer.objects.active:
            bpy.ops.object.mode_set(mode="POSE")
            context.object.pose.use_mirror_x = self.is_use
        if original_active:
            for i in original_objects:
                i.select_set(True)
            bpy.context.view_layer.objects.active = original_active
        bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
        return {"FINISHED"}


class MPM_OT_Weight_PoseBoneMirrorSelect(bpy.types.Operator):
    bl_idname = "mpm.weight_pose_bone_mirror_select"
    bl_label = "Select Mirror Bone"
    bl_options = {"UNDO"}
    bl_description = "Select the mirror bone"

    @classmethod
    def poll(cls, context):
        for obj in _Util.selected_objects():
            if obj.type == "ARMATURE":
                return obj.data.bones.active != None
        return False

    def execute(self, context):
        mesh = context.active_object
        arm = mesh.find_armature()
        for obj in _Util.selected_objects():
            if obj.type == "ARMATURE" and obj == arm:
                break
        else:
            return {"FINISHED"}
        name = arm.data.bones.active.name
        if name[-2:] in [".L", ".R", ".l", ".r"]:
            name = name[:-1] + {"L": "R", "R": "L", "l": "r", "r": "l"}[name[-1]]
        else:
            _Util.show_msgbox(f"No corresponding mirror bone exists. {name}")
            return {"CANCELLED"}
        if not (bone := arm.data.bones.get(name)):
            _Util.show_msgbox(f"Mirror bone not found. {name}")
            return {"CANCELLED"}
        arm.data.bones.active.select = False
        bone.select = True
        arm.data.bones.active = bone
        group_names = mesh.vertex_groups.keys()
        if name in group_names:
            mesh.vertex_groups.active_index = group_names.index(name)
        return {"FINISHED"}


class MPM_OT_Weight_GradientExpand(bpy.types.Operator):
    bl_idname = "mpm.weight_gradient_expand"
    bl_label = "Gradient Weight Expand"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Expand vertex selection and apply gradually decreasing weights"
    steps: bpy.props.IntProperty(default=5, min=1)
    max_weight: bpy.props.FloatProperty(default=1.0, min=0.0, max=1.0, description="Weight falloff bias (0=early, 0.5=linear, 1=late)")
    weight_mode: bpy.props.EnumProperty(name="Weight Mode", description="How to apply weight", default='REPLACE',
                                        items=[
                                            ('REPLACE', "Replace", "Replace the weight"),
                                            ('ADD', "Add", "Add to existing weight"),
                                            ('SUBTRACT', "Subtract", "Subtract from existing weight"),
                                        ])
    gradation_bias: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.vertex_groups and obj.vertex_groups.active

    def execute(self, context):
        import bmesh
        mesh = context.object.data
        vg = context.object.vertex_groups.active
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        current = set(v for v in bm.verts if v.select)
        visited = set(current)
        for i in range(self.steps):
            t = i / self.steps
            weight = self.max_weight * self.biased_weight(t, self.gradation_bias)
            for v in current:
                vg.add([v.index], weight, self.weight_mode)
            # 隣接頂点へ拡張する
            next_current = set()
            for v in current:
                for e in v.link_edges:
                    other = e.other_vert(v)
                    if other not in visited:
                        next_current.add(other)
            visited |= next_current
            current = next_current
        bm.free()
        return {"FINISHED"}

    def biased_weight(self, t: float, bias: float) -> float:
        t = max(0.0, min(1.0, t))
        bias = max(0.0, min(1.0, bias))

        if abs(bias - 0.5) < 1e-6:
            return 1.0 - t  # リニア

        if bias < 0.5:
            k = bias * 2.0  # [0..1]
            exponent = 1.0 + (1.0 - k) * 4.0  # exponent >=1
            return (1.0 - t) ** exponent  # 始端寄りの減衰

        else:
            k = (bias - 0.5) * 2.0  # [0..1]
            exponent = 1.0 + k * 4.0  # exponent >=1
        return 1.0 - (t ** exponent)  # 終端寄りの減衰


class MPM_OT_Weight_HideLeftRightBones(bpy.types.Operator):
    bl_idname = "mpm.weight_hide_side_bones"
    bl_label = "Hide L/R Bones"
    bl_options = {"REGISTER", "UNDO"}
    mode: bpy.props.EnumProperty(name="Mode", default="LEFT",
                                 items=[
                                     ("LEFT", "Left", ""),
                                     ("RIGHT", "Right", ""),
                                 ])

    @classmethod
    def poll(cls, context):
        return _Util.get_armature(context.active_object) != None

    def execute(self, context):
        sels = _Util.selected_objects()
        arm = _Util.get_armature(context.active_object)
        _Util.select_active(arm)
        # アーマチュア選択後じゃないと、ポーズモードに変更できない
        arms = [i for i in bpy.context.selected_objects if i.type == "ARMATURE"]
        if 0 == len(arms):
            return {"CANCELLED"}
        bpy.ops.object.mode_set(mode="POSE")
        conditions = (".r", ".R") if self.mode == "RIGHT" else (".l", ".L")
        for arm in arms:
            for pbone in arm.pose.bones:
                bone = pbone.bone
                # ボーンコレクションが表示されているなら
                if any(coll.is_visible for coll in bone.collections):
                    if bone.name.endswith(conditions):
                        if g.is_v5_0_later():
                            pbone.hide = True
                        else:
                            bone.hide = True
        _Util.select_active(sels[0])
        for i in sels[1:]:
            _Util.select_add(i)
        bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
        return {"FINISHED"}

    def convert(self, bone, func):
        bpy.ops.pose.select_all(action="DESELECT")
        bone.select = True
        func()

# --------------------------------------------------------------------------------


classes = (
    MPM_OT_Weight_VGroupMirrorBoneSelection,
    MPM_OT_Weight_VGroupMirrorActive,
    MPM_OT_Weight_VGroupMirrorOverwriteConfirm,
    MPM_OT_Weight_RemoveUnusedVertexGroup,
    MPM_OT_Weight_MaskNonZeroVGroup,
    MPM_OT_Weight_InspectSelectedVertices,
    MPM_OT_Weight_SetWeight,
    MPM_OT_Weight_RemoveWeight,
    MPM_OT_Weight_HideBoneOnPaintMonitorModal,
    MPM_OT_Weight_PoseBoneUseMirror,
    MPM_OT_Weight_PoseBoneMirrorSelect,
    MPM_OT_Weight_GradientExpand,
    MPM_OT_Weight_HideLeftRightBones,
)


def register():
    _Util.register_classes(classes)
    on_update_HideBoneOnPaint(_AddonPreferences.get_data().weightPaintHideBone)


def unregister():
    _Util.unregister_classes(classes)
