import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util
from . import _AddonPreferences
# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Edit Mesh Primary')

    # ヘッダー
    r = box.row()
    r2 = r.row(align=True)
    tool_settings = context.scene.tool_settings
    _Util.layout_prop(r2, tool_settings, "use_proportional_edit", text="")
    r2.prop_with_popover(tool_settings, "proportional_edit_falloff", text="", icon_only=True, panel="VIEW3D_PT_proportional_edit",)

    r2 = r.row(align=True)
    _Util.layout_prop(r2, tool_settings, "use_snap", text="")
    snap_items = bpy.types.ToolSettings.bl_rna.properties["snap_elements"].enum_items
    for elem in tool_settings.snap_elements:
        icon = snap_items[elem].icon
        break
    del snap_items
    r2.popover(panel="VIEW3D_PT_snapping", icon=icon, text="",)

    r = box.row(align=True)
    c = r.column(align=True)
    
    # 選択ボックス
    box = c.box()
    box.label(text = 'Selection')
    cc = box.column(align=True)

    _Util.layout_operator(cc, "mesh.select_mirror")
    _Util.layout_operator(cc, "mesh.shortest_path_select").edge_mode = "SELECT"
    op = _Util.layout_operator(cc, "mesh.select_face_by_sides", "Ngons")
    op.number = 4
    op.type='GREATER'

    # UVボックス
    box = c.box()
    box.label(text = 'UV')
    cc = box.column(align=True)
    r2 = cc.row(align=True)
    _Util.layout_operator(r2, "mesh.mark_seam").clear = False
    _Util.layout_operator(r2, "mesh.mark_seam", "", icon='REMOVE').clear = True
    row, sub = _Util.layout_for_mirror(r2)
    _Util.layout_operator(sub, MPM_OT_MirrorSeam.bl_idname, "", icon='ADD').is_seam = False
    _Util.layout_operator(sub, MPM_OT_MirrorSeam.bl_idname, "", icon='REMOVE').is_seam = True
    _Util.layout_operator(cc, "uv.unwrap")
    # Etcボックス
    box = r.box()
    box.label(text = 'Etc')
    c = box.column(align=True)
    r2 = c.row(align=True)
    _Util.layout_operator(r2, "mesh.mark_sharp").clear = False
    _Util.layout_operator(r2, "mesh.mark_sharp", "", icon='REMOVE').clear = True
    row, sub = _Util.layout_for_mirror(r2)
    _Util.layout_operator(sub, MPM_OT_MirrorSharp.bl_idname, "", icon='ADD').is_seam = False
    _Util.layout_operator(sub, MPM_OT_MirrorSharp.bl_idname, "", icon='REMOVE').is_seam = False
    r2 = c.row(align=False)
    r2.label(text="Symmetry");
    op = _Util.layout_operator(r2, "mesh.symmetry_snap", "+X to -X")
    op.direction = 'POSITIVE_X'
    # op.factor = 1.0
    op = _Util.layout_operator(r2, "mesh.symmetry_snap", "-X to +X")
    op.direction = 'NEGATIVE_X'
    # op.factor = 1.0
    # 法線 
    _Util.layout_operator(c, "mesh.normals_make_consistent").inside=False
    # マージ
    r2 = c.row(align=True)
    r2.label(text="Merge");
    _Util.layout_operator(r2, "mesh.merge", "Center").type="CENTER"
    _Util.layout_operator(r2, "mesh.merge", "First").type="FIRST"
    _Util.layout_operator(r2, "mesh.merge", "Last").type="LAST"

    _Util.layout_operator(c, "mesh.remove_doubles")

# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    box = pie.split().box()
    box.label(text = 'Edit Mesh Secondary')

# --------------------------------------------------------------------------------
class MPM_OT_MirrorSeam(bpy.types.Operator):
    bl_idname = "editmesh.mirror_seam"
    bl_label = "Mirror Seam"
    bl_options = {'REGISTER', 'UNDO'}
    is_seam: bpy.props.BoolProperty()
    def execute(self, context):
        mirror_settings = context.object.data.use_mirror_topology
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_seam(clear=self.is_seam)
        context.object.data.use_mirror_topology = True
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_seam(clear=self.is_seam)
        context.object.data.use_mirror_topology = mirror_settings
        return {'FINISHED'}
class MPM_OT_MirrorSharp(bpy.types.Operator):
    bl_idname = "editmesh.mirror_sharp"
    bl_label = "Mirror Sharp"
    bl_options = {'REGISTER', 'UNDO'}
    is_seam: bpy.props.BoolProperty()
    def execute(self, context):
        mirror_settings = context.object.data.use_mirror_topology
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_sharp(clear=self.is_seam)
        context.object.data.use_mirror_topology = True
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_sharp(clear=self.is_seam)
        context.object.data.use_mirror_topology = mirror_settings
        return {'FINISHED'}
# --------------------------------------------------------------------------------
classes = (
    MPM_OT_MirrorSeam,
    MPM_OT_MirrorSharp,
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)
