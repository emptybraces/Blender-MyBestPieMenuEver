import bpy
import bmesh
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

    _Util.layout_operator(cc, "mesh.select_mirror").extend=True
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
    _Util.layout_operator(sub, MPM_OT_MirrorSeam.bl_idname, "", icon='ADD').is_clear = False
    _Util.layout_operator(sub, MPM_OT_MirrorSeam.bl_idname, "", icon='REMOVE').is_clear = True
    _Util.layout_operator(cc, "uv.unwrap")
    # Etcボックス
    box = r.box()
    box.label(text = 'Etc')
    c = box.column(align=True)
    r2 = c.row(align=True)
    _Util.layout_operator(r2, "mesh.mark_sharp").clear = False
    _Util.layout_operator(r2, "mesh.mark_sharp", "", icon='REMOVE').clear = True
    row, sub = _Util.layout_for_mirror(r2)
    _Util.layout_operator(sub, MPM_OT_MirrorSharp.bl_idname, "", icon='ADD').is_clear = False
    _Util.layout_operator(sub, MPM_OT_MirrorSharp.bl_idname, "", icon='REMOVE').is_clear = True
    r2 = c.row(align=False)
    r2.label(text="Symmetry");
    op = _Util.layout_operator(r2, "mesh.symmetry_snap", "+X to -X")
    op.direction = 'POSITIVE_X'
    op = _Util.layout_operator(r2, "mesh.symmetry_snap", "-X to +X")
    op.direction = 'NEGATIVE_X'
    # 法線 
    _Util.layout_operator(c, "mesh.normals_make_consistent").inside=False
    # マージ
    r2 = c.row(align=True)
    r2.label(text="Merge");
    # 選択されている頂点を調べる
    is_any_select_verts = False
    if context.object:
        bm = bmesh.from_edit_mesh(context.object.data)
        for v in bm.verts:
             is_any_select_verts = v.select
             if is_any_select_verts:
                break
    merge_operator = bpy.ops.mesh.merge.get_rna_type()
    props = merge_operator.properties['type']
    is_vertex_mode = context.tool_settings.mesh_select_mode[0]
    i = 0
    for item in props.enum_items:
        if item.identifier in ("FIRST", "LAST"):
            if not is_vertex_mode: # 頂点モードじゃなかったら中断
                continue;
            if not is_any_select_verts: # 選択している頂点がなければ中断
                continue
        _Util.layout_operator(r2, "mesh.merge", item.name, is_any_select_verts).type=item.identifier
        # 3ボタンずつ開業
        i += 1
        if i % 3 == 0:
            r2 = c.row(align=True)
            r2.label(text="     ");
    # 距離でマージ
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
    is_clear: bpy.props.BoolProperty()
    def execute(self, context):
        mirror_settings = context.object.data.use_mirror_topology
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_seam(clear=self.is_clear)
        context.object.data.use_mirror_topology = True
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_seam(clear=self.is_clear)
        context.object.data.use_mirror_topology = mirror_settings
        return {'FINISHED'}
class MPM_OT_MirrorSharp(bpy.types.Operator):
    bl_idname = "editmesh.mirror_sharp"
    bl_label = "Mirror Sharp"
    bl_options = {'REGISTER', 'UNDO'}
    is_clear: bpy.props.BoolProperty()
    def execute(self, context):
        mirror_settings = context.object.data.use_mirror_topology
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_sharp(clear=self.is_clear)
        context.object.data.use_mirror_topology = True
        bpy.ops.mesh.select_mirror(extend=True)
        bpy.ops.mesh.mark_sharp(clear=self.is_clear)
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
