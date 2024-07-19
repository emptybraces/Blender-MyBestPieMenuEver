import bpy
import bmesh
from bpy.types import Panel, Menu, Operator
from . import _Util
from . import _AddonPreferences
from . import _PieMenu
# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Edit Mesh Primary')

    # ヘッダー
    r = box.row()
    box2 = r.box()
    box2.label(text = "Proportional")
    # プロポーショナル
    r2 = box2.row(align=True)
    tool_settings = context.scene.tool_settings
    _Util.layout_prop(r2, tool_settings, "use_proportional_edit", text="")
    r2.prop_with_popover(tool_settings, "proportional_edit_falloff", text="", icon_only=True, panel="VIEW3D_PT_proportional_edit",)
    _Util.layout_prop(r2, tool_settings, "use_proportional_connected")
    r2.label(text="                                          ")

    # スナップ
    box2 = r.box()
    box2.label(text = "Snap")
    r2 = box2.row(align=True)
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
    box.label(text = "Selection")
    cc = box.column(align=True)

    _Util.layout_operator(cc, "mesh.select_mirror").extend=True
    _Util.layout_operator(cc, "mesh.shortest_path_select").edge_mode = "SELECT"
    op = _Util.layout_operator(cc, "mesh.select_face_by_sides", "Ngons")
    op.number = 4
    op.type="GREATER"

    # UVボックス
    box = c.box()
    box.label(text = "UV")
    cc = box.column(align=True)
    r2 = cc.row(align=True)
    _Util.layout_operator(r2, "mesh.mark_seam").clear = False
    _Util.layout_operator(r2, "mesh.mark_seam", "", icon="REMOVE").clear = True
    row, sub = _Util.layout_for_mirror(r2)
    _Util.layout_operator(sub, MPM_OT_MirrorSeam.bl_idname, "", icon="ADD").is_clear = False
    _Util.layout_operator(sub, MPM_OT_MirrorSeam.bl_idname, "", icon="REMOVE").is_clear = True
    _Util.layout_operator(cc, "uv.unwrap")

    # 頂点グループ
    box = r.box()
    box.label(text = "Vertex Group")
    cc = box.column(align=True)
    _Util.layout_operator(cc, MPM_OT_SelectVertexGroups.bl_idname)
    _Util.layout_operator(cc, MPM_OT_AddVertexGroup.bl_idname)

    # Edge
    c3 = r.column();
    box = c3.box()
    box.label(text = "Edge")
    c = box.column(align=True)
    r2 = c.row(align=True)
    # シャープ
    _Util.layout_operator(r2, "mesh.mark_sharp").clear = False
    _Util.layout_operator(r2, "mesh.mark_sharp", "", icon="REMOVE").clear = True
    row, sub = _Util.layout_for_mirror(r2)
    _Util.layout_operator(sub, MPM_OT_MirrorSharp.bl_idname, "", icon="ADD").is_clear = False
    _Util.layout_operator(sub, MPM_OT_MirrorSharp.bl_idname, "", icon="REMOVE").is_clear = True
    # クリーズ
    _Util.layout_operator(c, MPM_OT_AdjustCrease.bl_idname)

    # Apply
    box = c3.box()
    box.label(text = "Apply")
    c = box.column(align=True)
    r2 = c.row(align=False)
    r2.label(text="Symmetrize");
    op = _Util.layout_operator(r2, "mesh.symmetry_snap", "+X to -X")
    op.direction = 'POSITIVE_X'
    op = _Util.layout_operator(r2, "mesh.symmetry_snap", "-X to +X")
    op.direction = 'NEGATIVE_X'
    # 法線 
    _Util.layout_operator(c, "mesh.normals_make_consistent").inside=False
    # マージ
    r2 = c.row(align=True)
    r2.operator_menu_enum("mesh.merge", "type")
    _Util.layout_operator(r2, "mesh.remove_doubles")
    _Util.layout_operator(c, "mesh.delete_loose")

# --------------------------------------------------------------------------------
class MPM_OT_AddVertexGroup(Operator):
    bl_idname = "editmesh.add_vertex_group"
    bl_label = "Add Vertex Group"
    bl_options = {'REGISTER', 'UNDO'}
    vgroup_name: bpy.props.StringProperty(name="Name", default="Group", description="Vertex group name")
    weight: bpy.props.FloatProperty(name="Weight", default=1.0, min=0.0, max=1.0)
    @classmethod
    def poll(self, context):
        # 選択されたオブジェクトがメッシュであり、少なくとも1つの頂点が選択されているかどうかをチェック
        obj = context.object
        return obj and obj.type == "MESH" and any(v.select for v in bmesh.from_edit_mesh(obj.data).verts)
    def execute(self, context):
        obj = context.object
        if obj:
            bpy.ops.object.mode_set(mode='OBJECT')
            obj.vertex_groups.new(name=self.vgroup_name)
            group = obj.vertex_groups[-1]
            obj.vertex_groups.active_index = group.index;
            for v in obj.data.vertices: #bmesh.from_edit_mesh(obj.data).verts:
                if v.select:
                    group.add([v.index], self.weight, 'REPLACE')
            self.report({'INFO'}, f"Added vertex group '{self.name}' with weight {self.weight} to selected vertices")
            bpy.ops.object.mode_set(mode='EDIT')
            return {"FINISHED"}
        else:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        return {"FINISHED"}
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
# --------------------------------------------------------------------------------
class MPM_SelectVertexPropertyGroup(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="")
    select: bpy.props.BoolProperty(name="", default=False)
# --------------------------------------------------------------------------------
class MPM_OT_SelectVertexGroups(bpy.types.Operator):
    bl_idname = "editmesh.select_vertex_groups"
    bl_label = "Select Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}
    vgroup_names = []
    init_verts = []
    @classmethod
    def poll(self, context):
        obj = context.object
        return obj and obj.type == "MESH" and 0 < len(context.object.vertex_groups)
    def invoke(self, context, event):
        self.vgroup_names.clear()
        # アクティブオブジェクトの頂点グループをリストに追加
        for vgroup in context.object.vertex_groups:
            self.vgroup_names.append(vgroup.name)
        # 現在選択中の頂点を保存
        self.init_verts.clear()
        for v in bmesh.from_edit_mesh(context.object.data).verts:
            if v.select:
                self.init_verts.append(v.index)
        _PieMenu.MPM_OT_OpenPieMenu.is_force_cancelled = True
        return context.window_manager.invoke_props_dialog(self)
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Click the VGroup to Select/Unselect.")
        for name in self.vgroup_names:
            col.operator(MPM_OT_SelectVertex.bl_idname, text=name).vgroup_name = name
    def cancel(self, context):
        # 復元
        bm = bmesh.from_edit_mesh(context.object.data)
        for v in bm.verts:
            v.select = False
        for index in self.init_verts:
            bm.verts[index].select = True
        bmesh.update_edit_mesh(context.object.data)
        context.object.update_from_editmode()
    def execute(self, context):
        return {"FINISHED"}
class MPM_OT_SelectVertex(bpy.types.Operator):
    bl_idname = "editmesh.select_vertex"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    vgroup_name: bpy.props.StringProperty()
    def execute(self, context):
        obj = context.object
        if self.vgroup_name not in obj.vertex_groups:
            self.report({"WARNING"}, f"Can't found VGroup: {self.vgroup_name}")
            return {"CANCELLED"}
        vg_idx = obj.vertex_groups[self.vgroup_name].index
        bm = bmesh.from_edit_mesh(obj.data)
        deform_layer = bm.verts.layers.deform.active
        if not deform_layer:
            self.report({"WARNING"}, f"Unexptected: {self.vgroup_name}")
            return {"CANCELLED"}

        # 選択されている頂点があるかどう調べる
        bm.select_flush(False)
        is_select = True
        for v in bm.verts:
            if vg_idx in v[deform_layer]:
                if v.select:
                    is_select = False
                    break
                v.select = True
        if not is_select:
            for v in bm.verts:
                if vg_idx in v[deform_layer]:
                    v.select = False
        bmesh.update_edit_mesh(obj.data)
        obj.update_from_editmode()
        return {"FINISHED"}
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
        return {"FINISHED"}
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
        return {"FINISHED"}

# --------------------------------------------------------------------------------
class MPM_OT_AdjustCrease(bpy.types.Operator):
    bl_idname = "editmesh.adjust_crease"
    bl_label = "Edge Crease"
    bl_options = {'REGISTER', 'UNDO'}
    crease_value: bpy.props.FloatProperty(
        name="Crease",
        description="Adjust the crease value of selected edges",
        min=0.0,
        max=1.0,
        default=0.0,
        step=0.1,
        precision=2
    )
    @classmethod
    def poll(self, context):
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        return obj and obj.type == "MESH" and any(e.select for e in bm.edges)
    def execute(self, context):
        mesh = context.object.data        
        bm = bmesh.from_edit_mesh(mesh)
        crease_layer = bm.edges.layers.float.get(mesh.attributes["crease_edge"].name)
        for edge in [v for v in bm.edges if v.select]:
            edge[crease_layer] = self.crease_value
        return {"FINISHED"}
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
# --------------------------------------------------------------------------------
classes = (
    MPM_OT_MirrorSeam,
    MPM_OT_MirrorSharp,
    MPM_OT_AddVertexGroup,
    MPM_OT_SelectVertex,
    MPM_SelectVertexPropertyGroup,
    MPM_OT_SelectVertexGroups,
    MPM_OT_AdjustCrease
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)
