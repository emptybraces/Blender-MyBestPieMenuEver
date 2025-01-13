import bpy
import bmesh
from . import _Util
from . import _UtilInput
from . import _UtilBlf
from . import g
from ._MenuObject import LayoutSwitchSelectionOperator
from mathutils import Vector, Matrix
import time
import math
# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------


def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text='Edit Mesh Primary')
    r = box.row(align=True)
    LayoutSwitchSelectionOperator(context, r)

    # ヘッダー
    r.label(text="Proportional")
    # プロポーショナル
    rr = r.row(align=True)
    tool_settings = context.scene.tool_settings
    _Util.layout_prop(rr, tool_settings, "use_proportional_edit", text="")
    rr.prop_with_popover(tool_settings, "proportional_edit_falloff", text="", icon_only=True, panel="VIEW3D_PT_proportional_edit",)
    _Util.layout_prop(rr, tool_settings, "use_proportional_connected")
    # r2.label(text="                                          ")

    # スナップ
    # box2 = r.box()
    r.label(text="Snap")
    rr = r.row(align=True)
    _Util.layout_prop(rr, tool_settings, "use_snap", text="")
    snap_items = bpy.types.ToolSettings.bl_rna.properties["snap_elements"].enum_items
    for elem in tool_settings.snap_elements:
        icon = snap_items[elem].icon
        break
    del snap_items
    rr.popover(panel="VIEW3D_PT_snapping", icon=icon, text="",)

    r = box.row(align=True)
    c = r.column(align=True)

    # overlay
    overlay = context.space_data.overlay
    box = c.box()
    box.label(text="Overlay", icon="OVERLAY")
    cc = box.column(align=True)
    _Util.layout_prop(cc, overlay, "show_weight", isActive=overlay.show_overlays)

    # 選択ボックス
    box = c.box()
    box.label(text="Selection", icon="ZOOM_SELECTED")
    cc = box.column(align=True)

    _Util.layout_operator(cc, "mesh.select_mirror").extend = True
    _Util.layout_operator(cc, "mesh.shortest_path_select").edge_mode = "SELECT"
    op = _Util.layout_operator(cc, "mesh.select_face_by_sides", "Ngons")
    op.number = 4
    op.type = "GREATER"

    # UVボックス
    box = c.box()
    box.label(text="UV", icon="UV")
    cc = box.column(align=True)
    rr = cc.row(align=True)
    _Util.layout_operator(rr, "mesh.mark_seam").clear = False
    _Util.layout_operator(rr, "mesh.mark_seam", "", icon="REMOVE").clear = True
    row, sub = _Util.layout_for_mirror(rr)
    _Util.layout_operator(sub, MPM_OT_MirrorSeam.bl_idname, "", icon="ADD").is_clear = False
    _Util.layout_operator(sub, MPM_OT_MirrorSeam.bl_idname, "", icon="REMOVE").is_clear = True
    _Util.layout_operator(cc, "uv.unwrap")

    # Vertexメニュー
    c2 = r.column()
    box = c2.box()
    box.label(text="Vertex", icon="VERTEXSEL")
    cc = box.column(align=True)
    _Util.layout_operator(cc, MPM_OT_VertCreasePanel.bl_idname)

    # 非表示
    rr = cc.row(align=True)
    _Util.layout_operator(rr, MPM_OT_HideVerts.bl_idname, "Hide", icon="HIDE_ON").mode = "Hide"
    _Util.layout_operator(rr, MPM_OT_HideVerts.bl_idname, "", icon="SELECT_SUBTRACT").mode = "Hide Other"
    _Util.layout_operator(rr, MPM_OT_ShowVerts.bl_idname, "Show", icon="HIDE_OFF").mode = "Show"
    _Util.layout_operator(rr, MPM_OT_ShowVerts.bl_idname, "", icon="SELECT_EXTEND").mode = "Show Only"
    _Util.layout_operator(rr, MPM_OT_ShowVerts.bl_idname, "", icon="SELECT_SUBTRACT").mode = "Show Selected"

    # VertexGroupメニュー
    box = c2.box()
    box.label(text="Vertex Group", icon="GROUP_VERTEX")
    cc = box.column(align=True)
    _Util.layout_operator(cc, MPM_OT_SelectVertexGroupPanel.bl_idname)
    _Util.layout_operator(cc, MPM_OT_AddVertexGroupPanel.bl_idname)

    # Edgeメニュー
    c3 = r.column()
    box = c3.box()
    box.label(text="Edge", icon="EDGESEL")
    c = box.column(align=True)
    rr = c.row(align=True)
    # シャープ
    _Util.layout_operator(rr, "mesh.mark_sharp").clear = False
    _Util.layout_operator(rr, "mesh.mark_sharp", "", icon="REMOVE").clear = True
    row, sub = _Util.layout_for_mirror(rr)
    _Util.layout_operator(sub, MPM_OT_MirrorSharp.bl_idname, "", icon="ADD").is_clear = False
    _Util.layout_operator(sub, MPM_OT_MirrorSharp.bl_idname, "", icon="REMOVE").is_clear = True
    # クリーズ
    _Util.layout_operator(c, MPM_OT_EdgeCreasePanel.bl_idname)
    # ボーンアーマチュア作成
    _Util.layout_operator(c, MPM_OT_GenterateBonesAlongSelectedEdge.bl_idname, icon="BONE_DATA")
    # 法線サイドへビューポートカメラを移動
    _Util.layout_operator(c, MPM_OT_AlignViewToEdgeNormalSideModal.bl_idname, icon="VIEW_CAMERA")

    # Applyメニュー
    box = c3.box()
    box.label(text="Apply", icon="MODIFIER")
    c = box.column(align=True)
    rr = c.row(align=False)
    rr.label(text="Symmetrize", icon="MOD_MIRROR")
    op = _Util.layout_operator(rr, "mesh.symmetry_snap", "+X to -X")
    op.direction = 'POSITIVE_X'
    op.factor = 1
    op = _Util.layout_operator(rr, "mesh.symmetry_snap", "-X to +X")
    op.direction = 'NEGATIVE_X'
    op.factor = 1
    # 頂点ミラー複製
    _Util.layout_operator(c, MPM_OT_DuplicateMirror.bl_idname, icon="SEQ_STRIP_DUPLICATE")
    # 法線
    _Util.layout_operator(c, "mesh.normals_make_consistent", icon="NORMALS_FACE").inside = False
    # マージ
    rr = c.row(align=True)
    rr.operator_menu_enum("mesh.merge", "type")
    _Util.layout_operator(rr, "mesh.remove_doubles", icon="X")
    _Util.layout_operator(c, "mesh.delete_loose", icon="X")

# --------------------------------------------------------------------------------


class MPM_OT_AddVertexGroupPanel(bpy.types.Operator):
    bl_idname = "mpm.editmesh_add_vertex_group_panel"
    bl_label = "Add Vertex Group"
    bl_options = {"REGISTER", "UNDO"}
    vgroup_name: bpy.props.StringProperty(name="Name", default="Group", description="Vertex group name")
    weight: bpy.props.FloatProperty(name="Weight", default=1.0, min=0.0, max=1.0)

    @classmethod
    def poll(self, context):
        return _Util.is_selected_verts(context.edit_object)

    def execute(self, context):
        obj = context.object
        if obj:
            bpy.ops.object.mode_set(mode="OBJECT")
            obj.vertex_groups.new(name=self.vgroup_name)
            group = obj.vertex_groups[-1]
            obj.vertex_groups.active_index = group.index
            # bmesh.from_edit_mesh(obj.data).verts:
            for v in obj.data.vertices:
                if v.select:
                    group.add([v.index], self.weight, "REPLACE")
            self.report({"INFO"}, f"Added vertex group '{self.name}' with weight {self.weight} to selected vertices")
            bpy.ops.object.mode_set(mode="EDIT")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}
        return {"FINISHED"}

    def invoke(self, context, event):
        g.is_force_cancelled_piemenu = True
        return context.window_manager.invoke_props_dialog(self)
# --------------------------------------------------------------------------------


class MPM_OT_SelectVertexGroupPanel(bpy.types.Operator):
    bl_idname = "mpm.editmesh_select_vertex_group_panel"
    bl_label = "Select Vertex Groups"
    vg_counts = []
    init_verts = []
    limit_rows = 50
    single_width = 170

    @classmethod
    def poll(self, context):
        obj = context.object
        return obj and obj.type == "MESH" and 0 < len(context.object.vertex_groups)

    def invoke(self, context, event):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        deform_layer = bm.verts.layers.deform.active
        self.vg_counts = [0] * len(obj.vertex_groups)
        self.init_verts.clear()
        for v in bm.verts:
            # 現在選択中の頂点を保存
            if v.select:
                self.init_verts.append(v.index)
            # 頂点グループごとの登録頂点数を取得
            for i in v[deform_layer].keys():
                self.vg_counts[i] += 1
        g.is_force_cancelled_piemenu = True
        column_cnt = int(1 + int(len(obj.vertex_groups) / self.limit_rows))
        return context.window_manager.invoke_props_dialog(self, width=self.single_width * column_cnt)

    def draw(self, context):
        self.layout.label(text="Click the VGroup to Select/Unselect.")
        _Util.MPM_OT_CallbackOperator.operator(self.layout, "Deselect All", self.bl_idname + ".clear",
                                               self.on_click_clear, (context, ), "X", _Util.is_selected_verts(context.edit_object))
        # vgrupsボタン
        cnt = 0
        r = self.layout.row(align=True)
        c = r.column(align=True)
        obj = context.object
        for vg in obj.vertex_groups:
            vcnt = self.vg_counts[vg.index]
            _Util.MPM_OT_CallbackOperator.operator(c, f"{vg.name} (vcnt={vcnt})", self.bl_idname + vg.name,
                                                   self.on_click_item, (context, vg.name), isActive=0 < vcnt)
            cnt += 1
            if cnt % self.limit_rows == 0:
                c = r.column(align=True)

    def cancel(self, context):
        # 復元
        bm = bmesh.from_edit_mesh(context.object.data)
        for v in bm.verts:
            v.select = False
        for index in self.init_verts:
            bm.verts[index].select = True
        bmesh.update_edit_mesh(context.object.data)
        context.object.update_from_editmode()
        _Util.MPM_OT_CallbackOperator.clear()

    def execute(self, context):
        _Util.MPM_OT_CallbackOperator.clear()
        return {"FINISHED"}

    def on_click_clear(self, context):
        bpy.ops.mesh.select_all(action="DESELECT")

    def on_click_item(self, context, vgname):
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="VERT")
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        deform_layer = bm.verts.layers.deform.active
        if not deform_layer:
            self.report({"WARNING"}, f"Unexptected: {vgname}")
            return {"CANCELLED"}

        # 選択されている頂点があるかどうか調べる
        bm.select_flush(False)
        is_select = True
        vg_idx = obj.vertex_groups[vgname].index
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

# --------------------------------------------------------------------------------


class MPM_OT_HideVerts(bpy.types.Operator):
    bl_idname = "mpm.editmesh_hide_verts"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Hides the selected vertex.
Option1: Hides all vertices except the selected."""
    mode: bpy.props.EnumProperty(name="Mode", items=[("Hide", "Hide", ""), ("Hide Other", "Hide Other", "")])

    @classmethod
    def poll(self, context):
        return _Util.is_selected_verts(context.edit_object)

    def execute(self, context):
        if self.mode == "Hide":
            return bpy.ops.mesh.hide(unselected=False)
        else:
            return bpy.ops.mesh.hide(unselected=True)


class MPM_OT_ShowVerts(bpy.types.Operator):
    bl_idname = "mpm.editmesh_show_verts"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Show the hide vertices.
Option1: Shown vertices are selected.
Option2: Select only the shown vertices."""
    mode: bpy.props.EnumProperty(name="Mode", items=[("Show", "Show", ""), ("Show Only", "Show Only", ""), ("Show Selected", "Show Selected", "")])

    @classmethod
    def poll(self, context):
        obj = context.edit_object
        return obj and obj.type == "MESH" and any(e.hide for e in bmesh.from_edit_mesh(obj.data).verts)

    def execute(self, context):
        if self.mode == "Show":
            bpy.ops.mesh.reveal(select=False)
        elif self.mode == "Show Only":
            bpy.ops.mesh.reveal(select=True)
        elif self.mode == "Show Selected":
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.mesh.reveal(select=True)
        return {"FINISHED"}

# --------------------------------------------------------------------------------


class MPM_OT_MirrorSeam(bpy.types.Operator):
    bl_idname = "mpm.editmesh_mirror_seam"
    bl_label = "Mirror Seam"
    bl_options = {"REGISTER", "UNDO"}
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
    bl_idname = "mpm.editmesh_mirror_sharp"
    bl_label = "Mirror Sharp"
    bl_options = {"REGISTER", "UNDO"}
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


class MPM_OT_VertCreasePanel(bpy.types.Operator):
    bl_idname = "mpm.editmesh_vert_crease_panel"
    bl_label = "Vert Crease"
    bl_options = {"REGISTER", "UNDO"}
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
        return _Util.is_selected_verts(context.edit_object)

    def execute(self, context):
        mesh = context.object.data
        bm = bmesh.from_edit_mesh(mesh)
        crease_layer = bm.verts.layers.float.get("crease_vert", None)
        if crease_layer is None:
            crease_layer = bm.verts.layers.float.new("crease_vert")
        for v in [v for v in bm.verts if v.select]:
            v[crease_layer] = self.crease_value
        bmesh.update_edit_mesh(context.object.data)
        return {"FINISHED"}

    def invoke(self, context, event):
        g.is_force_cancelled_piemenu = True
        return context.window_manager.invoke_props_dialog(self)


class MPM_OT_EdgeCreasePanel(bpy.types.Operator):
    bl_idname = "mpm.editmesh_edge_crease_panel"
    bl_label = "Edge Crease"
    bl_options = {"REGISTER", "UNDO"}
    crease_value: bpy.props.FloatProperty(name="Crease", description="Adjust the crease value of selected edges",
                                          min=0.0, max=1.0, default=0.0, step=0.1, precision=2)

    @classmethod
    def poll(self, context):
        return _Util.is_selected_edges(context.edit_object)

    def execute(self, context):
        mesh = context.object.data
        bm = bmesh.from_edit_mesh(mesh)
        crease_layer = bm.edges.layers.float.get("crease_edge", None)
        if crease_layer is None:
            crease_layer = bm.edges.layers.float.new("crease_edge")
        for edge in [v for v in bm.edges if v.select]:
            edge[crease_layer] = self.crease_value
        bmesh.update_edit_mesh(context.object.data)
        return {"FINISHED"}

    def invoke(self, context, event):
        g.is_force_cancelled_piemenu = True
        return context.window_manager.invoke_props_dialog(self)
# --------------------------------------------------------------------------------


class MPM_OT_DuplicateMirror(bpy.types.Operator):
    bl_idname = "mpm.duplicate_mirror"
    bl_label = "Mirror Duplication"
    bl_options = {"REGISTER", "UNDO"}
    mirror_x: bpy.props.BoolProperty(name="Mirror X", default=True)
    mirror_y: bpy.props.BoolProperty(name="Mirror Y", default=False)
    mirror_z: bpy.props.BoolProperty(name="Mirror Z", default=False)

    @classmethod
    def poll(self, context):
        return _Util.is_selected_verts(context.edit_object)

    def execute(self, context):
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)

        selected_verts = [v for v in bm.verts if v.select]
        vert_map = {}
        new_edge_face = []

        # 複製
        # print(dir(bm.loops.layers))
        # print(dir(bm.loops.layers.color))
        # print(bm.loops.layers.color.active)
        # print(bm.loops.layers.color.items())
        # print(bm.loops.layers.color.keys())
        # print(bm.loops.layers.float.keys())
        # print(bm.loops.layers.float_color.keys())
        # print(bm.loops.layers.float_vector.keys())
        # print(bm.loops.layers.int.keys())
        # print(bm.loops.layers.string.keys())
        # print(bm.loops.layers.uv.keys())
        # print(bm.verts.layers.deform.keys())
        vg = obj.vertex_groups
        deform_layer = bm.verts.layers.deform.active
        # 選択中の頂点
        for v in selected_verts:
            new_vert = bm.verts.new(v.co)
            vert_map[v] = new_vert
            for layer in bm.verts.layers.float:
                new_vert[layer] = v[layer]
        for edge in bm.edges:
            # 選択中の辺
            if edge.verts[0] in vert_map and edge.verts[1] in vert_map:
                new_edge = bm.edges.new(
                    (vert_map[edge.verts[0]], vert_map[edge.verts[1]]))
                new_edge_face.append(new_edge)
                new_edge.seam = edge.seam
                new_edge.smooth = edge.smooth
                for layer in bm.edges.layers.float:
                    new_edge[layer] = edge[layer]

        for face in bm.faces:
            # 選択中の面
            if all(vert in vert_map for vert in face.verts):
                new_verts = [vert_map[vert] for vert in face.verts]
                new_face = bm.faces.new(new_verts)
                new_edge_face.append(new_face)
                for old_loop, new_loop in zip(face.loops, new_face.loops):
                    for layer in bm.loops.layers.uv:
                        new_loop[layer].uv = old_loop[layer].uv
                    for layer in bm.loops.layers.color:
                        new_loop[layer] = old_loop[layer]
                    for layer in bm.loops.layers.float:
                        new_loop[layer] = old_loop[layer]
                    for layer in bm.loops.layers.float_color:
                        new_loop[layer] = old_loop[layer]
                    for layer in bm.loops.layers.float_vector:
                        new_loop[layer] = old_loop[layer]
                    for layer in bm.loops.layers.int:
                        new_loop[layer] = old_loop[layer]
                    for layer in bm.loops.layers.string:
                        new_loop[layer] = old_loop[layer]

        # 選択解除
        bm.select_flush(False)
        for v in selected_verts:
            v.select = False
        for v in bm.edges:
            v.select = False
        for v in bm.faces:
            v.select = False

        # 選択
        for v in vert_map.values():
            v.select = True
            if self.mirror_x:
                v.co.x = -v.co.x
            if self.mirror_y:
                v.co.y = -v.co.y
            if self.mirror_z:
                v.co.z = -v.co.z
        for edge_face in new_edge_face:
            edge_face.select = True

        bm.normal_update()
        bmesh.update_edit_mesh(obj.data)

        # indexが-1だから登録できない
        target_vgs = set()
        for oldv, newv in vert_map.items():
            for g in vg:
                if g.index in oldv[deform_layer]:
                    target_vgs.add(g)
                    # weight = g.weight(oldv.index)
                    # _Util.show_report(self, newv.index, newv, weight)
                    # g.add([new_vert.index], weight, "REPLACE")
        # 頂点グループコピー、なぜかmirrorするとコピー元の登録が消える。
        bpy.ops.object.mode_set(mode="OBJECT")
        # bpy.ops.object.vertex_group_mirror(all_groups = True, use_topology=False)
        if obj.vertex_groups.active:
            current_vg_name = obj.vertex_groups.active.name
            # まずミラー作って、
            vg_copy_from_to = []
            for vg in target_vgs:
                bpy.ops.object.vertex_group_set_active(group=vg.name)
                bpy.ops.object.vertex_group_copy()
                bpy.ops.object.vertex_group_mirror(use_topology=False)
                vg_copy_from_to.append((obj.vertex_groups.active, vg))

            # マージする。
            for v in [v for v in obj.data.vertices if v.select]:
                for g in v.groups:
                    for gg in vg_copy_from_to:
                        if g.group == gg[0].index:
                            if 0 < g.weight:
                                gg[1].add([v.index], g.weight, "REPLACE")
            # ミラーを削除
            for g in vg_copy_from_to:
                bpy.ops.object.vertex_group_set_active(group=g[0].name)
                bpy.ops.object.vertex_group_remove()
            # アクティブを戻す
            bpy.ops.object.vertex_group_set_active(group=current_vg_name)

        # Editに戻す
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}

# --------------------------------------------------------------------------------


class MPM_OT_GenterateBonesAlongSelectedEdge(bpy.types.Operator):
    bl_idname = "mpm.generate_along_from_edge"
    bl_label = "Generate bones along selected edges"
    bl_options = {"REGISTER", "UNDO"}

    order_dir: bpy.props.EnumProperty(name="Order", items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")])
    order_invert: bpy.props.BoolProperty(name="Invert", description="")
    bone_chain: bpy.props.BoolProperty(name="Bone Chain", description="",  default=True)
    bone_ratio: bpy.props.FloatProperty(name="Bone Ratio", description="", default=1.0, min=0.01, max=2.0)
    slide_to_normal: bpy.props.FloatProperty(name="Slide To Normal", description="", default=0.0, min=-1.0, max=1.0)
    angle_for_isolate: bpy.props.IntProperty(
        name="Separates edge groups by vertices with edge pairs that are lower than the specified angle", description="", default=0, min=0, max=120)

    @classmethod
    def poll(self, context):
        return _Util.is_selected_edges(context.edit_object)

    def execute(self, context):
        obj = context.edit_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        if not any(e.select for e in bm.edges):
            _Util.show_report_error(self, "Please select at least one edge.")
            return {"CANCELLED"}

        def find_isolated_vert_edge_groups(bm, limit_angle):
            # 孤立された頂点・辺グループを取得。グループは指定鋭角、３つ以上の分岐で分離する。

            # 分岐対象頂点を検索する
            branch_verts = set()  # 鋭角を持つ頂点
            for v in [e for e in bm.verts if e.select]:
                # 辺で接続されている頂点
                connected_edge_count = sum(1 for e in v.link_edges if e.select)
                # 端っこまたは、複数分岐
                if connected_edge_count != 2:
                    branch_verts.add(v)
                    continue
                # 辺が２つは確定
                else:
                    connected_vecs = [(e.other_vert(v).co - v.co).normalized() for e in v.link_edges if e.select]
                    # for i, j in itertools.combinations(connected_vecs, 2):
                    # _Util.show_report(self, "combinations", i, j)
                    angle = math.degrees(connected_vecs[0].angle(connected_vecs[1]))
                    # _Util.show_report(self, "angle=", angle)
                    # 指定鋭角だった場合
                    if angle <= limit_angle:
                        branch_verts.add(v)

            # _Util.show_report(self, "branch_verts=", len(branch_verts), branch_verts)
            # 分岐対象頂点から始める辺グループを作成
            visited_edges = set()
            vert_groups = []
            edge_groups = []
            for v in branch_verts:
                for e in [e for e in v.link_edges if e.select]:
                    if e in visited_edges:
                        continue
                    cur_v = v
                    vert_group = [cur_v]
                    edge_group = []
                    cur_edge = e
                    for _infinite in range(100000):
                        next_v = cur_edge.other_vert(cur_v)
                        # _Util.show_report(self, f"{cur_v} > {next_v}")
                        vert_group.append(next_v)
                        edge_group.append(cur_edge)
                        visited_edges.add(cur_edge)
                        if next_v in branch_verts:
                            vert_groups.append(vert_group)
                            edge_groups.append(edge_group)
                            break
                        # 次の接続辺へ
                        le = [e for e in next_v.link_edges if e.select and e not in visited_edges]
                        # 必ず一つの辺が見つかるはず
                        if 1 != len(le):
                            raise Exception(f"Expecting to find one edge. found count is {len(le)}")
                        cur_edge = le[0]
                        cur_v = next_v
                    else:
                        raise Exception("Error: Prevent inifinite loop!")

            # 辺ループなど分岐対象頂点が存在しない孤立された辺グループ
            # 選択された辺のうち、まだ走査してない辺
            for e in [e for e in bm.edges if e.select and e not in visited_edges]:
                if e in visited_edges:
                    continue
                cur_v = e.verts[0]
                vert_group = [cur_v]
                edge_group = []
                cur_edge = e
                for _infinite in range(100000):
                    next_v = cur_edge.other_vert(cur_v)
                    edge_group.append(cur_edge)
                    visited_edges.add(cur_edge)
                    # _Util.show_report(self, f"{cur_v.index} > {next_v.index}")
                    # 1周したら
                    if next_v in vert_group:
                        # _Util.show_report(self, f"vert_gropp = {[v.index for v in vert_group]}")
                        vert_group.append(next_v)  # ループボーンを閉じるために必要。また、ここで入れないと上のifが常に合格してしまう。
                        vert_groups.append(vert_group)
                        edge_groups.append(edge_group)
                        break
                    vert_group.append(next_v)  # ifの後に入れる
                    # 次の接続辺へ
                    le = [e for e in next_v.link_edges if e.select and e not in visited_edges]
                    # 必ず一つの辺が見つかるはず
                    if 1 != len(le):
                        raise Exception(f"Expecting to find one edge. found count is {len(le)}")
                    cur_edge = le[0]
                    cur_v = next_v
                else:
                    raise Exception("Error: Prevent inifinite loop!")

            return (vert_groups, edge_groups)

        # グループ
        vert_groups, edge_groups = find_isolated_vert_edge_groups(bm, self.angle_for_isolate)
        # _Util.show_report(self, "---------------")
        # _Util.show_report(self, "vert_groups=", len(vert_groups), [len(v) for v in vert_groups])
        # _Util.show_report(self, "edge_groups=", len(edge_groups), [len(v) for v in edge_groups])
        if len(vert_groups) != len(edge_groups):
            raise Exception(f"Expecting match to length of each group. {len(vert_groups)}, {len(edge_groups)}")

        # 位置と法線抜き出してソート
        sorted_lists = []
        for vgroup in vert_groups:
            sorted_lists.append([(v.co.copy(), v.normal.copy()) for v in vgroup])
        for i in range(len(sorted_lists)):
            pos_s = sorted_lists[i][0][0]
            pos_e = sorted_lists[i][-1][0]
            is_invert = False
            if self.order_dir == "X" and not self.order_invert and pos_e.x < pos_s.x:
                is_invert = True
            elif self.order_dir == "X" and self.order_invert and pos_s.x < pos_e.x:
                is_invert = True
            elif self.order_dir == "Y" and not self.order_invert and pos_e.y < pos_s.y:
                is_invert = True
            elif self.order_dir == "Y" and self.order_invert and pos_s.y < pos_e.y:
                is_invert = True
            elif self.order_dir == "Z" and not self.order_invert and pos_e.z < pos_s.z:
                is_invert = True
            elif self.order_dir == "Z" and self.order_invert and pos_s.z < pos_e.z:
                is_invert = True
            if is_invert:
                sorted_lists[i] = sorted_lists[i][::-1]
        # アーマチュアを追加
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.armature_add()
        armature = context.object
        armature.name = "bones_from_edges"
        # ボーン追加
        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones = armature.data.edit_bones
        for bone in edit_bones:
            edit_bones.remove(bone)
        # メッシュの辺を選択してボーンを作成
        for tuples in sorted_lists:
            prev_bone = None
            co_list = [e[0] for e in tuples]
            n_list = [e[1] for e in tuples]
            fixed_count = max(2, int(len(tuples) * self.bone_ratio))
            _Util.show_report(self, f"bone count = {fixed_count-1}")
            for i in range(fixed_count-1):
                bone = edit_bones.new("Bone")
                if 1 == self.bone_ratio:
                    bone.head = obj.matrix_world @ co_list[i]
                    bone.tail = obj.matrix_world @ co_list[i+1]
                    bone.head += n_list[i] * self.slide_to_normal
                    bone.tail += n_list[i+1] * self.slide_to_normal
                else:
                    bone.head = obj.matrix_world @ _Util.lerp_segments_by_distance(co_list, (i) / (fixed_count-1))[0]
                    bone.tail = obj.matrix_world @ _Util.lerp_segments_by_distance(co_list, (i+1) / (fixed_count-1))[0]
                    bone.head += _Util.lerp_segments_by_distance(n_list, (i) / (fixed_count-1))[0] * self.slide_to_normal
                    bone.tail += _Util.lerp_segments_by_distance(n_list, (i+1) / (fixed_count-1))[0] * self.slide_to_normal
                # print(i, (i) / fixed_count, (i+1) / fixed_count)
                # print("n=", info_list[i]["n"], info_list[i+1]["n"], self.slide_to_normal)
                bone.parent = prev_bone if self.bone_chain else None
                prev_bone = bone
                # _Util.show_report(self, f"{bone.name}, {p1}, {p2}, {bone.head}, {bone.tail}")
        return {"FINISHED"}


class MPM_OT_AlignViewToEdgeNormalSideModal(bpy.types.Operator):
    bl_idname = "mpm.align_view_to_edge_normal_side_modal"
    bl_label = "Align view to edge normal side"

    dir: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 1))
    invert: bpy.props.BoolProperty()
    original_location: Vector
    original_rotation: Matrix
    start_location: Vector
    start_rotation: Matrix
    target_location: Vector
    target_rotation: Matrix
    translate_duration = 0.2
    start_time = 0.0
    timer = None
    label_handler = None
    mouse_pos: Vector = Vector((0, 0, 0))

    @classmethod
    def poll(self, context):
        return _Util.is_selected_edges(context.edit_object)

    def invoke(self, context, event):
        self.is_reverting = False
        self.mouse_pos.x = event.mouse_x
        self.mouse_pos.y = event.mouse_y
        self.original_location = context.region_data.view_location.copy()
        self.original_rotation = context.region_data.view_rotation.copy()
        _UtilInput.init()
        return self.execute(context)

    def execute(self, context):
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        selected_edges = [edge for edge in bm.edges if edge.select]
        selected_faces = [face for face in bm.faces if face.select]
        total_center = _Util.VEC3()
        total_normal = _Util.VEC3()
        if any(selected_faces):
            for face in selected_faces:
                total_center += obj.matrix_world @ face.calc_center_median()
                total_normal += obj.matrix_world.to_3x3() @ face.normal
            average_center = total_center / len(selected_faces)
        else:
            for edge in selected_edges:
                v1 = obj.matrix_world @ edge.verts[0].co
                v2 = obj.matrix_world @ edge.verts[1].co
                total_center += (v1 + v2) / 2
                # 辺に接続する面の法線
                connected_faces = edge.link_faces
                if not connected_faces:
                    nv1 = obj.matrix_world.to_3x3() @ edge.verts[0].normal  # to_3x3は回転・スケール行列のフィルタ
                    nv2 = obj.matrix_world.to_3x3() @ edge.verts[1].normal
                    total_normal += (nv1 + nv2).normalized()
                else:
                    # 法線を計算（複数の面がある場合は平均法線を使用）
                    normal = Vector((0, 0, 0))
                    for face in connected_faces:
                        normal += face.normal
                    total_normal += normal.normalized()
            average_center = total_center / len(selected_edges)
        average_normal = total_normal.normalized()
        # 法線に対して横方向を計算
        # side_vector = average_direction.cross(average_normal).normalized()
        # side_vector = average_normal.cross(_Util.VEC3_Z()).normalized()
        side_vector = Vector(self.dir).cross(average_normal).normalized()
        # ビューポートの正面方向と一致するように回転を計算
        # rotation = _Util.view_rotation(side_vector, Vector(self.dir))
        # print(side_vector, Vector(self.dir))
        # if self.dir[0] != 0:
        #     side_vector.x *= self.dir[0]
        # if self.dir[1] != 0:
        #     side_vector.y *= self.dir[1]
        # if self.dir[2] != 0:
        #     side_vector.z *= self.dir[2]
        # side_vector = side_vector.normalized()
        # print(side_vector)
        rotation = _Util.view_rotation(side_vector, _Util.VEC3_Z())
        # ビューポート値を更新
        self.start_location = context.region_data.view_location.copy()
        self.start_rotation = context.region_data.view_rotation.copy()
        self.target_rotation = rotation
        self.target_location = average_center
        self.elapsed = 0.0
        self.start_time = time.time()
        if self.timer is None:
            self.timer = context.window_manager.event_timer_add(0.01, window=context.window)
            context.window_manager.modal_handler_add(self)
        if self.label_handler is None:
            self.label_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_label, (self, context), "WINDOW", 'POST_PIXEL')
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if self.is_reverting:
            self.elapsed = time.time() - self.start_time
            t = min(1.0, self.elapsed / self.translate_duration)
            context.region_data.view_location = self.target_location.lerp(self.original_location, t)
            context.region_data.view_rotation = self.target_rotation.slerp(self.original_rotation, t)
            if 1 <= self.elapsed:
                return self.cancel(context)
            else:
                return {"RUNNING_MODAL"}

        context.area.tag_redraw()
        self.mouse_pos.x = _Util.lerp(self.mouse_pos.x, event.mouse_x, 0.05)
        self.mouse_pos.y = _Util.lerp(self.mouse_pos.y, event.mouse_y, 0.05)
        if _UtilInput.is_pressed_key(event, "X")[0]:
            self.dir = Vector((-1 if self.dir[0] == 1 else 1, 0, 0))
            return self.execute(context)
        if _UtilInput.is_pressed_key(event, "Y")[0]:
            self.dir = Vector((0, -1 if self.dir[1] == 1 else 1, 0))
            return self.execute(context)
        if _UtilInput.is_pressed_key(event, "Z")[0]:
            if event.alt:
                context.space_data.shading.show_xray = not context.space_data.shading.show_xray
            else:
                self.dir = Vector((0, 0, -1 if self.dir[2] == 1 else 1))
                return self.execute(context)
        if event.type == "WHEELUPMOUSE":
            context.region_data.view_distance -= 0.5
        elif event.type == "WHEELDOWNMOUSE":
            context.region_data.view_distance += 0.5

            return {"PASS_THROUGH"}
        if _UtilInput.is_pressed_keys(event, "LEFTMOUSE", "RET"):
            return self.cancel(context)
        if _UtilInput.is_pressed_keys(event, "RIGHTMOUSE", "ESC", "SPACE", "RET"):
            self.is_reverting = True
            self.start_time = time.time()
            return {"RUNNING_MODAL"}
            # アニメ
        if self.elapsed <= self.translate_duration and event.type == "TIMER":
            self.elapsed = time.time() - self.start_time
            t = min(1.0, self.elapsed / self.translate_duration)
            context.region_data.view_location = self.start_location.lerp(self.target_location, t)
            context.region_data.view_rotation = self.start_rotation.slerp(self.target_rotation, t)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        # _Util.show_report(self, "CANCELLED")
        if self.label_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self.label_handler, "WINDOW")
            self.label_handler = None
        if self.timer:
            context.window_manager.event_timer_remove(self.timer)
            self.timer = None
        return {"CANCELLED"}

    def draw_label(self, context, event):
        if self.is_reverting:
            return
        fid = 0  # デフォルトのフォントを使用
        x = self.mouse_pos.x
        y = self.mouse_pos.y
        _UtilBlf.animate_clipping(fid, x, 500, self.timer.time_duration)
        text = "Align view to edge normal side"
        _UtilBlf.draw_title(fid, text, x, y)

        if self.dir[0] != 0:
            text = "+X" if self.dir[0] == 1 else "-X"
        elif self.dir[1] != 0:
            text = "+Y" if self.dir[1] == 1 else "-Y"
        elif self.dir[2] != 0:
            text = "+Z" if self.dir[2] == 1 else "-Z"

        _UtilBlf.draw_field(fid, "Direction = ", text, "| press X, Y, Z, twice to invert", x, y, 0)
        _UtilBlf.draw_field(fid, "Wireframe = ", str(bpy.context.space_data.shading.show_xray), "| press ALT + Z", x, y, 1)
        _UtilBlf.draw_field(fid, "Zoom", None, "| mousewheel", x, y, 2)
        _UtilBlf.draw_field(fid, "Cancel", None, "| right click", x + 100, y, 2)
        _UtilBlf.draw_field(fid, "Finish", None, "| left click", x + 200, y, 2)
        # _UtilBlf.draw_msg(fid, "Mousewheel: Zoom", x, y, 4)
        # _UtilBlf.draw_msg(fid, "LMB: Finish", x, y, 5)


# --------------------------------------------------------------------------------
classes = (
    MPM_OT_MirrorSeam,
    MPM_OT_MirrorSharp,
    MPM_OT_AddVertexGroupPanel,
    MPM_OT_SelectVertexGroupPanel,
    MPM_OT_VertCreasePanel,
    MPM_OT_EdgeCreasePanel,
    MPM_OT_HideVerts,
    MPM_OT_ShowVerts,
    MPM_OT_DuplicateMirror,
    MPM_OT_GenterateBonesAlongSelectedEdge,
    MPM_OT_AlignViewToEdgeNormalSideModal,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
