import bpy
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
    c = box.column(align=True)
    r = c.row()
    unified_paint_settings = context.tool_settings.unified_paint_settings
    brush = context.tool_settings.weight_paint.brush
    r = c.row()
    _Util.layout_prop(r, unified_paint_settings, "weight")
    r = r.row(align=True)
    _Util.MPM_OT_SetSingle.operator(r, "0.0", unified_paint_settings, "weight", 0.0)
    _Util.MPM_OT_SetSingle.operator(r, "0.1", unified_paint_settings, "weight", 0.1)
    _Util.MPM_OT_SetSingle.operator(r, "0.5", unified_paint_settings, "weight", 0.5)
    _Util.MPM_OT_SetSingle.operator(r, "1.0", unified_paint_settings, "weight", 1.0)
    r = c.row()
    _Util.layout_prop(r, brush, "strength")
    r = r.row(align=True)
    _Util.MPM_OT_SetSingle.operator(r, "50%", brush, "strength", brush.strength / 2)
    _Util.MPM_OT_SetSingle.operator(r, "200%", brush, "strength", brush.strength * 2)
    _Util.MPM_OT_SetSingle.operator(r, "0.1", brush, "strength", 0.1)
    _Util.MPM_OT_SetSingle.operator(r, "1.0", brush, "strength", 1.0)
    # Blends
    r = c.row(align=True)
    target_blends = ["mix", "add", "sub"]
    for i in _Util.enum_values(brush, "blend"):
        if i.lower() in target_blends:
            is_use = brush.blend == i
            _Util.MPM_OT_SetString.operator(r, i, brush, "blend", i, depress=is_use)
    # 蓄積
    _Util.layout_prop(c, brush, "use_accumulate")
    # ぼかしブラシの強さ
    smooth_brush = None
    for brush in bpy.data.brushes:
        if brush.use_paint_weight and brush.name.lower() == "blur":
            smooth_brush = brush
            break
    if smooth_brush:
        r = c.row(align=True)
        r.label(icon="BRUSH_BLUR")
        _Util.layout_prop(r, smooth_brush, "strength", "Blur Brush: Strength")
        r = r.row(align=True)
        r.scale_x = 0.8
        _Util.MPM_OT_SetSingle.operator(r, "50%", brush, "strength", max(0, brush.strength * 0.5))
        _Util.MPM_OT_SetSingle.operator(r, "75%", brush, "strength", max(0, brush.strength * 0.75))
        _Util.MPM_OT_SetSingle.operator(r, "150%", brush, "strength", min(1, brush.strength * 1.5))
        _Util.MPM_OT_SetSingle.operator(r, "200%", brush, "strength", min(1, brush.strength * 2))

    # util
    box = row.box()
    box.label(text="Utility", icon="MODIFIER")
    MirrorVertexGroup(box)


# --------------------------------------------------------------------------------


def MenuSecondary(pie, context):
    box = pie.split().box()
    box.label(text="WeightPaint Secondary")
# --------------------------------------------------------------------------------


def MirrorVertexGroup(layout):
    r = layout.row(align=True)
    r.label(text="Create VGroup Mirror")
    _Util.layout_operator(r, MPM_OT_MirrorVGFromSelectedListItem.bl_idname)
    _Util.layout_operator(r, MPM_OT_MirrorVGFromSelectedBone.bl_idname)


# --------------------------------------------------------------------------------


class MPM_OT_MirrorVGFromSelectedBone(bpy.types.Operator):
    bl_idname = "mpm.mirror_vg_from_bone"
    bl_label = "Selected Bones"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "ARMATURE" and 0 < len([bone for bone in obj.data.bones if bone.select]):
                return True
        return False

    def get_selected_bone_names(self, obj):
        if obj and obj.type == "ARMATURE":
            armature = obj.data
            active_bone = armature.bones.active
            selected_bones = [bone for bone in armature.bones if bone.select]
            selected_bone_names = [bone.name for bone in selected_bones]
            return selected_bone_names
        return None

    def execute(self, context):
        msg = ""
        selected_objects = context.selected_objects
        names = []
        g.is_force_cancelled_piemenu_modal = True
        for obj in selected_objects:
            names = self.get_selected_bone_names(obj)
            if names != None and context.active_object.type == "MESH":
                for name in names:
                    new_name, actural_name, is_replace = mirror_vgroup(context.active_object, name)
                    # 逐次起動ができないため、おかしくなる
                    # if is_replace:
                    #     bpy.ops.mpm.mirror_vg_overrite_confirm("INVOKE_DEFAULT", target_name=name, overwrite_name=new_name)
                    # else:
                    msg += f"{name} -> {actural_name}\n"
        _Util.show_msgbox(msg if msg else "Invalid Selection!", "Mirror VGroup from selected bones")
        return {"FINISHED"}


class MPM_OT_MirrorVGFromSelectedListItem(bpy.types.Operator):
    bl_idname = "mpm.mirror_vg_from_list"
    bl_label = "Active"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object != None and any(context.active_object.vertex_groups)

    def execute(self, context):
        msg = ""
        obj = context.active_object
        target_name = obj.vertex_groups.active.name
        new_name, actural_name, is_replace = mirror_vgroup(obj, target_name)
        g.is_force_cancelled_piemenu_modal = True
        if is_replace:
            bpy.ops.mpm.mirror_vg_overrite_confirm("INVOKE_DEFAULT", target_name=target_name, overwrite_name=new_name)
        else:
            msg += f"{target_name} -> {actural_name}\n"
            _Util.show_msgbox(msg if msg else "Invalid selection!", "Mirror VGroup from selected vgroup")
        return {"FINISHED"}


class MPM_OT_MirrorVGOverwriteConfirm(bpy.types.Operator):
    bl_idname = "mpm.mirror_vg_overrite_confirm"
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


def mirror_vgroup(obj, name):
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
    bpy.ops.object.vertex_group_mirror(use_topology=False)
    is_duplicate = new_name in obj.vertex_groups
    obj.vertex_groups.active.name = new_name
    return new_name, obj.vertex_groups.active.name, is_duplicate
# --------------------------------------------------------------------------------


classes = (
    MPM_OT_MirrorVGFromSelectedBone,
    MPM_OT_MirrorVGFromSelectedListItem,
    MPM_OT_MirrorVGOverwriteConfirm,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
