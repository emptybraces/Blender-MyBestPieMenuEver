import bpy
import os
from . import _Util
from . import g
# --------------------------------------------------------------------------------
# ウェイトペイントモードメニュー
# --------------------------------------------------------------------------------

def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text="WeightPaint Primary")

    # icons
    row = box.row(align=True)
    _Util.layout_prop(row, bpy.context.object.data, "use_paint_mask", icon_only=True)
    _Util.layout_prop(row, bpy.context.object.data, "use_paint_mask_vertex", icon_only=True)
    # row.operator("screen.userpref_show", icon='PREFERENCES', text="")
    # row.operator("wm.console_toggle", icon='CONSOLE', text="")

    # box menu
    row = box.row()

    # brushes
    box = row.box()
    box.label(text="Brush Property", icon="BRUSH_DATA")
    cc = box.column(align=True)
    r = cc.row()
    current_brush = context.tool_settings.weight_paint.brush
    unified_paint_settings = context.tool_settings.unified_paint_settings

    # weight
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_weight else current_brush
    r = cc.row()
    _Util.layout_prop(r, brush_property_target, "weight")
    r = r.row(align=True)
    _Util.MPM_OT_SetSingle.operator(r, "0.0", brush_property_target, "weight", 0.0)
    _Util.MPM_OT_SetSingle.operator(r, "0.1", brush_property_target, "weight", 0.1)
    _Util.MPM_OT_SetSingle.operator(r, "0.5", brush_property_target, "weight", 0.5)
    _Util.MPM_OT_SetSingle.operator(r, "1.0", brush_property_target, "weight", 1.0)
    _Util.layout_prop(r, unified_paint_settings, "use_unified_weight")
    
    # size
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_size else current_brush
    r = cc.row()
    _Util.layout_prop(r, brush_property_target, "size")
    r = r.row(align=True)
    _Util.MPM_OT_SetInt.operator(r, "50%", brush_property_target, "size", int(brush_property_target.size * 0.5))
    _Util.MPM_OT_SetInt.operator(r, "80%", brush_property_target, "size", int(brush_property_target.size * 0.8))
    _Util.MPM_OT_SetInt.operator(r, "150%", brush_property_target, "size", int(brush_property_target.size * 1.5))
    _Util.MPM_OT_SetInt.operator(r, "200%", brush_property_target, "size", int(brush_property_target.size * 2.0))
    _Util.layout_prop(r, unified_paint_settings, "use_unified_size")

    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_strength else current_brush
    r = cc.row()
    _Util.layout_prop(r, brush_property_target, "strength")
    r = r.row(align=True)
    _Util.MPM_OT_SetSingle.operator(r, "50%", brush_property_target, "strength", brush_property_target.strength / 2)
    _Util.MPM_OT_SetSingle.operator(r, "200%", brush_property_target, "strength", brush_property_target.strength * 2)
    _Util.MPM_OT_SetSingle.operator(r, "0.1", brush_property_target, "strength", 0.1)
    _Util.MPM_OT_SetSingle.operator(r, "1.0", brush_property_target, "strength", 1.0)
    _Util.layout_prop(r, unified_paint_settings, "use_unified_strength")
    # Blends
    r = cc.row(align=True)
    target_blends = ["mix", "add", "sub"]
    for i in _Util.enum_values(current_brush, "blend"):
        if i.lower() in target_blends:
            is_use = current_brush.blend == i
            _Util.MPM_OT_SetString.operator(r, i, current_brush, "blend", i, depress=is_use)
    # 蓄積
    _Util.layout_prop(cc, current_brush, "use_accumulate")
    # ぼかしブラシの強さ
    blur_brush = None
    if bpy.app.version < (4, 2, 9):
        for current_brush in bpy.data.brushes:
            if current_brush.use_paint_weight and current_brush.name.lower() == "blur":
                blur_brush = current_brush
                break
    else:
        blender_install_dir = os.path.dirname(bpy.app.binary_path)
        blur_brush = bpy.data.brushes["Blur", blender_install_dir + "\\4.3\\datafiles\\assets\\brushes\\essentials_brushes-mesh_weight.blend"]
    if blur_brush:
        r = cc.row(align=True)
        r.enabled = not unified_paint_settings.use_unified_strength
        _Util.layout_prop(r, blur_brush, "strength", "Blur Brush: Strength")
        r = r.row(align=True)
        r.scale_x = 0.8
        _Util.MPM_OT_SetSingle.operator(r, "50%", blur_brush, "strength", max(0, blur_brush.strength * 0.5))
        _Util.MPM_OT_SetSingle.operator(r, "75%", blur_brush, "strength", max(0, blur_brush.strength * 0.75))
        _Util.MPM_OT_SetSingle.operator(r, "150%", blur_brush, "strength", min(1, blur_brush.strength * 1.5))
        _Util.MPM_OT_SetSingle.operator(r, "200%", blur_brush, "strength", min(1, blur_brush.strength * 2))
    # util
    c = row.column()
    box = c.box()
    box.label(text="Utility", icon="MODIFIER")
    cc = box.column(align=True)
    _Util.layout_prop(cc, context.space_data.overlay, "weight_paint_mode_opacity")
    r = cc.row(align=True)
    r.label(text="Zero Weights")
    _Util.layout_prop(r, context.scene.tool_settings, "vertex_group_user", expand=True)
    _Util.layout_prop(cc, context.space_data.overlay, "show_paint_wire")

    # apply
    box = c.box()
    box.label(text="Apply", icon="CHECKMARK")
    cc = box.column(align=True)
    rr = cc.row(align=True)
    _Util.layout_operator(rr, MPM_OT_Weight_SetWeight.bl_idname).is_mask = False
    _Util.layout_operator(rr, MPM_OT_Weight_SetWeight.bl_idname, "", icon="MOD_MASK").is_mask = True
    MirrorVertexGroup(cc)
    _Util.layout_operator(cc, MPM_OT_Weight_RemoveUnusedVertexGroup.bl_idname, icon="X")

# --------------------------------------------------------------------------------


def MirrorVertexGroup(layout):
    r = layout.row(align=True)
    r.label(text="Create VGroup Mirror")
    _Util.layout_operator(r, MPM_OT_Weight_MirrorVGFromActive.bl_idname, "Active")
    _Util.layout_operator(r, MPM_OT_Weight_MirrorVGFromActiveTopology.bl_idname, "", icon="MOD_MIRROR")
    _Util.layout_operator(r, MPM_OT_Weight_MirrorVGFromSelectedBone.bl_idname, "Selected Bones")
    _Util.layout_operator(r, MPM_OT_Weight_MirrorVGFromSelectedBoneTopology.bl_idname, "", icon="MOD_MIRROR")


# --------------------------------------------------------------------------------

class MPM_OT_Weight_MirrorVGFromSelectedBoneBase():
    @classmethod
    def poll(cls, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "ARMATURE" and 0 < len([bone for bone in obj.data.bones if bone.select]):
                return True
        return False

    def get_selected_bone_names(self, obj):
        if obj and obj.type == "ARMATURE":
            armature = obj.data
            selected_bones = [bone for bone in armature.bones if bone.select]
            selected_bone_names = [bone.name for bone in selected_bones]
            return selected_bone_names
        return None

    def execute(self, context, use_topology):
        msg = ""
        selected_objects = context.selected_objects
        names = []
        g.force_cancel_piemenu_modal(context)
        for obj in selected_objects:
            names = self.get_selected_bone_names(obj)
            if names != None and context.active_object.type == "MESH":
                for name in names:
                    new_name, actural_name, is_replace = mirror_vgroup(context.active_object, name, use_topology)
                    msg += f"{name} -> {actural_name}\n"
        _Util.show_msgbox(msg if msg else "Invalid Selection!", "Mirror VGroup from selected bones")
        return {"FINISHED"}


class MPM_OT_Weight_MirrorVGFromSelectedBoneTopology(bpy.types.Operator, MPM_OT_Weight_MirrorVGFromSelectedBoneBase):
    bl_idname = "mpm.weight_mirror_vg_from_bone_topology"
    bl_label = "Create VertexGroup mirror from selected bones with Topology"
    bl_description = "Create VertexGroup mirror from selected bones with Topology"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        super().poll(context)

    def execute(self, context):
        return super().execute(context, True)


class MPM_OT_Weight_MirrorVGFromSelectedBone(bpy.types.Operator, MPM_OT_Weight_MirrorVGFromSelectedBoneBase):
    bl_idname = "mpm.weight_mirror_vg_from_bone"
    bl_label = "Create VertexGroup mirror from selected bones"
    bl_description = "Create mirror VertexGroup from selected bones"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return super().poll(context)

    def execute(self, context):
        return super().execute(context, False)


class MPM_OT_Weight_MirrorVGFromActiveBase():
    @classmethod
    def poll(cls, context):
        return context.active_object != None and any(context.active_object.vertex_groups)

    def get_selected_bone_names(self, obj):
        if obj and obj.type == "ARMATURE":
            armature = obj.data
            selected_bones = [bone for bone in armature.bones if bone.select]
            selected_bone_names = [bone.name for bone in selected_bones]
            return selected_bone_names
        return None

    def execute(self, context, use_topology):
        current_mode = context.active_object.mode
        if current_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        obj = context.active_object
        target_name = obj.vertex_groups.active.name
        new_name, actural_name, is_replace = mirror_vgroup(obj, target_name, use_topology)
        g.force_cancel_piemenu_modal(context)
        if is_replace:
            bpy.ops.mpm.mirror_vg_overrite_confirm("INVOKE_DEFAULT", target_name=target_name, overwrite_name=new_name)
        else:
            msg = f"{target_name} -> {actural_name}\n"
            _Util.show_msgbox(msg if msg else "Invalid selection!", "Mirror VGroup from selected vgroup")
        if current_mode != "OBJECT":
            bpy.ops.object.mode_set(mode=current_mode)
        # bpy.app.timers.register(__popup, first_interval=0)
        return {"FINISHED"}


class MPM_OT_Weight_MirrorVGFromActive(bpy.types.Operator, MPM_OT_Weight_MirrorVGFromActiveBase):
    bl_idname = "mpm.weight_mirror_vg_from_active"
    bl_label = "Create VertexGroup mirror from active"
    bl_description = "Create VertexGroup mirror from active"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return super().poll(context)

    def execute(self, context):
        return super().execute(context, False)


class MPM_OT_Weight_MirrorVGFromActiveTopology(bpy.types.Operator, MPM_OT_Weight_MirrorVGFromActiveBase):
    bl_idname = "mpm.weight_mirror_vg_from_active_topology"
    bl_label = "Create VertexGroup mirror from active with topology"
    bl_description = "Create VertexGroup mirror from active with topology"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return super().poll(context)

    def execute(self, context):
        return super().execute(context, True)


class MPM_OT_Weight_MirrorVGOverwriteConfirm(bpy.types.Operator):
    bl_idname = "mpm.weight_mirror_vg_overrite_confirm"
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
        bpy.ops.object.vertex_group_set_active(group=self.overwrite_name)
        bpy.ops.object.vertex_group_remove()
        bpy.ops.object.vertex_group_set_active(group=active_name)
        obj.vertex_groups.active.name = self.overwrite_name
        _Util.show_msgbox(f"{self.target_name} -> {self.overwrite_name}\n", "Mirror VGroup from selected vgroup")
        return {"FINISHED"}

class MPM_OT_Weight_RemoveUnusedVertexGroup(bpy.types.Operator):
    bl_idname = "mpm.weight_mirror_vg_overrite_confirm"
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
        bpy.ops.object.vertex_group_set_active(group=self.overwrite_name)
        bpy.ops.object.vertex_group_remove()
        bpy.ops.object.vertex_group_set_active(group=active_name)
        obj.vertex_groups.active.name = self.overwrite_name
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

    bpy.ops.object.vertex_group_set_active(group=name)
    bpy.ops.object.vertex_group_copy()
    bpy.ops.object.vertex_group_mirror(use_topology=use_topology)
    is_duplicate = new_name in obj.vertex_groups
    obj.vertex_groups.active.name = new_name
    return new_name, obj.vertex_groups.active.name, is_duplicate
# --------------------------------------------------------------------------------


class MPM_OT_Weight_RemoveUnusedVertexGroup(bpy.types.Operator):
    bl_idname = "mpm.remove_unused_vgroup"
    bl_label = "Remove Unused VGroup"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Bulk remove vertex groups that do not have weights set"

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

# --------------------------------------------------------------------------------


classes = (
    MPM_OT_Weight_MirrorVGFromSelectedBone,
    MPM_OT_Weight_MirrorVGFromSelectedBoneTopology,
    MPM_OT_Weight_MirrorVGFromActive,
    MPM_OT_Weight_MirrorVGFromActiveTopology,
    MPM_OT_Weight_MirrorVGOverwriteConfirm,
    MPM_OT_Weight_RemoveUnusedVertexGroup,
    MPM_OT_Weight_SetWeight,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
