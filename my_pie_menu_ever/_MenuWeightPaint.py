import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util
# --------------------------------------------------------------------------------
# ウェイトペイントモードメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = "WeightPaint Primary")

    # icons
    row = box.row(align=True)
    _Util.layout_prop(row, bpy.context.object.data, "use_paint_mask", icon_only=True)
    _Util.layout_prop(row, bpy.context.object.data, "use_paint_mask_vertex", icon_only=True)
    # row.operator("screen.userpref_show", icon='PREFERENCES', text="")
    # row.operator("wm.console_toggle", icon='CONSOLE', text="")

    # box menu
    row = box.row()

    # util
    box = row.box()
    box.label(text = "Utility")
    MirrorVertexGroup(box)

    # brushes
    box = row.box()
    box.label(text = "Brush Property")
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
    _Util.layout_prop(r, context.tool_settings.weight_paint.brush, "strength")
    r = r.row(align=True)
    _Util.MPM_OT_SetSingle.operator(r, "50%", brush, "strength", brush.strength / 2)
    _Util.MPM_OT_SetSingle.operator(r, "200%", brush, "strength", brush.strength * 2)
    _Util.MPM_OT_SetSingle.operator(r, "0.1", brush, "strength", 0.1)
    _Util.MPM_OT_SetSingle.operator(r, "1.0", brush, "strength", 1.0)
    # Blends
    r = c.row(align=True)
    target_blends = ['mix', 'add', 'sub']
    for i in _Util.enum_values(brush, 'blend'):
        if i.lower() in target_blends:
            is_use = brush.blend == i
            _Util.MPM_OT_SetString.operator(r, i, brush, "blend", i, depress=is_use)

# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    box = pie.split().box()
    box.label(text = 'WeightPaint Secondary')
# --------------------------------------------------------------------------------
def MirrorVertexGroup(layout):
    r = layout.column(align=True)
    r.label(text="Create VGroup Mirror:")
    r = r.row(align=True)
    _Util.layout_operator(r, OT_MirrorVGFromSelectedListItem.bl_idname)
    _Util.layout_operator(r, OT_MirrorVGFromSelectedBone.bl_idname)

# --------------------------------------------------------------------------------
class OT_MirrorVGFromSelectedBone(bpy.types.Operator):
    bl_idname = "op.mirror_vgroup_from_bone"
    bl_label = "Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'ARMATURE' and 0 < len([bone for bone in obj.data.bones if bone.select]):
                return True
        return False
    def get_selected_bone_names(self, obj):
        if obj and obj.type == 'ARMATURE':
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
        for obj in selected_objects:
            names = self.get_selected_bone_names(obj)
            if names != None and context.active_object.type == 'MESH':
                for name in names:
                    new_vg = mirror_vgroup(context.active_object, name)
                    if new_vg:
                        msg += f"{name} -> {new_vg}\n"
        _Util.show_msgbox(msg if msg else "Invalid selection!", "Mirror VGroup from selected bones")
        return {'FINISHED'}
class OT_MirrorVGFromSelectedListItem(bpy.types.Operator):
    bl_idname = "op.mirror_vgroup_from_list"
    bl_label = "Selected VGroup"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object != None
    def execute(self, context):
        msg = ""
        obj = context.active_object
        target_name = obj.vertex_groups.active.name
        new_vg = mirror_vgroup(obj, target_name)
        if new_vg:
            msg += f"{target_name} -> {new_vg}\n"
        _Util.show_msgbox(msg if msg else "Invalid selection!", "Mirror VGroup from selected vgroup")
        return {'FINISHED'}
# --------------------------------------------------------------------------------
def mirror_vgroup(obj, name):
    # 接尾辞のリプレース
    postfix = name[-2:]
    new_name = name
    if postfix == ".L": new_name = new_name[:-2] + ".R"
    elif postfix == ".R": new_name = new_name[:-2] + ".l"
    elif postfix == ".l": new_name = new_name[:-2] + ".r"
    elif postfix == ".r": new_name = new_name[:-2] + ".l"
    # 中間のリプレース
    if ".L." in new_name:    new_name = new_name.replace(".L.", ".R.")
    elif ".R." in new_name:  new_name = new_name.replace(".R.", ".L.")
    elif ".l." in new_name:  new_name = new_name.replace(".l.", ".r.")
    elif ".r." in new_name:  new_name = new_name.replace(".r.", ".l.")

    # vgroup = obj.vertex_groups.get(name)
    bpy.ops.object.vertex_group_set_active(group=name)
    bpy.ops.object.vertex_group_copy()
    bpy.ops.object.vertex_group_mirror(use_topology=False)
    obj.vertex_groups.active.name = new_name
    return obj.vertex_groups.active.name
# --------------------------------------------------------------------------------

classes = (
    OT_MirrorVGFromSelectedBone,
    OT_MirrorVGFromSelectedListItem,
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)