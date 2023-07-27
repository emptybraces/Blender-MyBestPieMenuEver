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
    _Util.layout_operator(box, _MenuPose.OT_ClearTransform.bl_idname, _Util.is_armature_in_selected())
    r = box.row(align=False)
    r.label(text="Copy Mirrored VG from ")
    _Util.layout_operator(r, OT_MirrorVGFromSelectedListItem.bl_idname)
    _Util.layout_operator(r, OT_MirrorVGFromSelectedBone.bl_idname, _Util.is_armature_in_selected())

# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    col_root = pie.split().column()
    col_root.label(text = 'Secondary')

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
    if name[-2:] != '.L' and name[-2:] != '.R':
        return None
    new_name = name[:-2]
    if name[-2:] == '.L':   new_name += '.R'
    elif name[-2:] == '.R': new_name += '.L'
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