import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util
from . import _MenuPose
# --------------------------------------------------------------------------------
# ウェイトペイントモードメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'WeightPaint')
    _Util.layout_operator(box, _MenuPose.OT_ClearTransform.bl_idname, isActive=_Util.is_armature_in_selected())
    r = box.row(align=False)
    r.label(text="Copy Mirrored VG from ")
    _Util.layout_operator(r, OT_MirrorVGFromSelectedListItem.bl_idname)
    _Util.layout_operator(r, OT_MirrorVGFromSelectedBone.bl_idname, isActive=_Util.is_armature_in_selected())

# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    box = pie.split().box()
    r = box.row(align=False)
    r.label(text = 'Weight')
    _Util.layout_prop(r, context.tool_settings.unified_paint_settings, "weight")
    _Util.OT_SetterBase.operator(_Util.OT_SetSingle.bl_idname, r, "0.0", context.tool_settings.unified_paint_settings, "weight", 0.0)
    _Util.OT_SetterBase.operator(_Util.OT_SetSingle.bl_idname, r, "0.1", context.tool_settings.unified_paint_settings, "weight", 0.1)
    _Util.OT_SetterBase.operator(_Util.OT_SetSingle.bl_idname, r, "0.5", context.tool_settings.unified_paint_settings, "weight", 0.5)
    _Util.OT_SetterBase.operator(_Util.OT_SetSingle.bl_idname, r, "1.0", context.tool_settings.unified_paint_settings, "weight", 1.0)
    r = box.row(align=False)
    r.label(text = 'Strength')
    _Util.layout_prop(r, context.tool_settings.weight_paint.brush, "strength")
    _Util.OT_SetterBase.operator(_Util.OT_SetSingle.bl_idname, r, "0.1", context.tool_settings.weight_paint.brush, "strength", 0.1)
    _Util.OT_SetterBase.operator(_Util.OT_SetSingle.bl_idname, r, "0.2", context.tool_settings.weight_paint.brush, "strength", 0.2)
    _Util.OT_SetterBase.operator(_Util.OT_SetSingle.bl_idname, r, "0.4", context.tool_settings.weight_paint.brush, "strength", 0.4)
    _Util.OT_SetterBase.operator(_Util.OT_SetSingle.bl_idname, r, "1.0", context.tool_settings.weight_paint.brush, "strength", 1.0)

# --------------------------------------------------------------------------------
class OT_MirrorVGFromSelectedBone(bpy.types.Operator):
    bl_idname = "op.mirror_vgroup_from_bone"
    bl_label = "Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}
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
            if names != None: break
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
    print (name, '.L' not in name , '.R' not in name)
    if '.L' not in name and '.R' not in name:
        return None
    new_name = name.replace('.L', '.R') if '.L' in name else name.replace('.R', '.L')
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