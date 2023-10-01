import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util
from . import _AddonPreferences
# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Edit Mesh')
    r = box.row()
    box2 = r.box()

    box2.label(text = 'Selection')
    r2 = box2.row()
    _Util.layout_prop(r2, context.scene.tool_settings, "use_proportional_edit", text="")
    _Util.layout_prop(r2, context.scene.tool_settings, "use_proportional_connected", isActive=context.scene.tool_settings.use_proportional_edit)
    _Util.layout_prop(r2, context.scene.tool_settings, "proportional_edit_falloff", text="", isActive=context.scene.tool_settings.use_proportional_edit)
    _Util.layout_prop(box2, context.scene.tool_settings, "use_snap")
    _Util.layout_operator(box2, "mesh.select_mirror")

    box2 = r.box()
    box2.label(text = 'UV')
    r2 = box2.row(align=True)
    _Util.layout_operator(r2, "mesh.mark_seam").clear = False
    _Util.layout_operator(r2, "mesh.mark_seam", "", icon='REMOVE').clear = True
    _Util.layout_operator(r2, OT_MirrorSeam.bl_idname, "", icon='MOD_MIRROR')
    _Util.layout_operator(box2, "uv.unwrap")

    box2 = r.box()
    box2.label(text = 'Etc')
    r2 = box2.row(align=True)
    _Util.layout_operator(r2, "mesh.mark_sharp").clear = False
    _Util.layout_operator(r2, "mesh.mark_sharp", "", icon='REMOVE').clear = True
    _Util.layout_operator(r2, OT_MirrorSharp.bl_idname, "", icon='MOD_MIRROR')

# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    box = pie.split().box()

# --------------------------------------------------------------------------------
class OT_MirrorSeam(bpy.types.Operator):
    bl_idname = "editmesh.mirror_seam"
    bl_label = "Mirror Seam"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        mirror_settings = context.object.data.use_mirror_topology
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_seam(clear=False)
        context.object.data.use_mirror_topology = True
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_seam(clear=False)
        context.object.data.use_mirror_topology = mirror_settings
        return {'FINISHED'}
class OT_MirrorSharp(bpy.types.Operator):
    bl_idname = "editmesh.mirror_sharp"
    bl_label = "Mirror Sharp"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        mirror_settings = context.object.data.use_mirror_topology
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_sharp(clear=False)
        context.object.data.use_mirror_topology = True
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_sharp(clear=False)
        context.object.data.use_mirror_topology = mirror_settings
        return {'FINISHED'}
# --------------------------------------------------------------------------------
classes = (
    OT_MirrorSeam,
    OT_MirrorSharp,
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)
