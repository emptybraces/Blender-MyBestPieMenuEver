import bpy
import bmesh
from . import _Util
from . import g
from math import degrees
from ._MenuObject import LayoutSwitchSelectionOperator

import itertools
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
    r2 = r.row(align=True)
    tool_settings = context.scene.tool_settings
    _Util.layout_prop(r2, tool_settings, "use_proportional_edit", text="")
    r2.prop_with_popover(tool_settings, "proportional_edit_falloff", text="", icon_only=True, panel="VIEW3D_PT_proportional_edit",)
    _Util.layout_prop(r2, tool_settings, "use_proportional_connected")
    # r2.label(text="                                          ")

    # スナップ
    # box2 = r.box()
    r.label(text="Snap")
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
    r2 = cc.row(align=True)
    _Util.layout_operator(r2, "mesh.mark_seam").clear = False
    _Util.layout_operator(r2, "mesh.mark_seam", "", icon="REMOVE").clear = True
    row, sub = _Util.layout_for_mirror(r2)
    _Util.layout_operator(sub, MPM_OT_MirrorSeam.bl_idname, "", icon="ADD").is_clear = False
    _Util.layout_operator(sub, MPM_OT_MirrorSeam.bl_idname, "", icon="REMOVE").is_clear = True
    _Util.layout_operator(cc, "uv.unwrap")

    # Vertexメニュー
    c2 = r.column()
    box = c2.box()
    box.label(text="Vertex", icon="VERTEXSEL")
    cc = box.column(align=True)
    _Util.layout_operator(cc, MPM_OT_VertCreasePanel.bl_idname)

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
    r2 = c.row(align=True)
    # シャープ
    _Util.layout_operator(r2, "mesh.mark_sharp").clear = False
    _Util.layout_operator(r2, "mesh.mark_sharp", "", icon="REMOVE").clear = True
    row, sub = _Util.layout_for_mirror(r2)
    _Util.layout_operator(sub, MPM_OT_MirrorSharp.bl_idname, "", icon="ADD").is_clear = False
    _Util.layout_operator(sub, MPM_OT_MirrorSharp.bl_idname, "", icon="REMOVE").is_clear = True
    # クリーズ
    _Util.layout_operator(c, MPM_OT_EdgeCreasePanel.bl_idname)
    # ボーンアーマチュア作成
    _Util.layout_operator(c, MPM_OT_GenterateBoneFromEdge.bl_idname, icon="BONE_DATA")

    # Applyメニュー
    box = c3.box()
    box.label(text="Apply", icon="MODIFIER")
    c = box.column(align=True)
    r2 = c.row(align=False)
    r2.label(text="Symmetrize", icon="MOD_MIRROR")
    op = _Util.layout_operator(r2, "mesh.symmetry_snap", "+X to -X")
    op.direction = 'POSITIVE_X'
    op.factor = 1
    op = _Util.layout_operator(r2, "mesh.symmetry_snap", "-X to +X")
    op.direction = 'NEGATIVE_X'
    op.factor = 1
    # 頂点ミラー複製
    _Util.layout_operator(c, MPM_OT_DuplicateMirror.bl_idname, icon="SEQ_STRIP_DUPLICATE")
    # 法線
    _Util.layout_operator(c, "mesh.normals_make_consistent", icon="NORMALS_FACE").inside = False
    # マージ
    r2 = c.row(align=True)
    r2.operator_menu_enum("mesh.merge", "type")
    _Util.layout_operator(r2, "mesh.remove_doubles", icon="X")
    _Util.layout_operator(c, "mesh.delete_loose", icon="X")

# --------------------------------------------------------------------------------


class MPM_OT_AddVertexGroupPanel(bpy.types.Operator):
    bl_idname = "op.mpm_editmesh_add_vertex_group_panel"
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
    bl_idname = "op.mpm_editmesh_select_vertex_group_panel"
    bl_label = "Select Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}
    map_vgname_to_label = {}
    init_verts = []

    @classmethod
    def poll(self, context):
        obj = context.object
        return obj and obj.type == "MESH" and 0 < len(context.object.vertex_groups)

    def invoke(self, context, event):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        deform_layer = bm.verts.layers.deform.active
        self.map_vgname_to_label.clear()
        # アクティブオブジェクトの頂点グループをリストに追加
        for vgroup in obj.vertex_groups:
            self.map_vgname_to_label[vgroup.name] = 0
        # 現在選択中の頂点を保存
        self.init_verts.clear()
        for v in bm.verts:
            if v.select:
                self.init_verts.append(v.index)
            #
            for vg in obj.vertex_groups:
                vg_idx = obj.vertex_groups[vg.name].index
                if vg_idx in v[deform_layer]:
                    self.map_vgname_to_label[vg.name] += 1

        for k, v in self.map_vgname_to_label.items():
            self.map_vgname_to_label[k] = (f"{k} (vcnt={v})")
        g.is_force_cancelled_piemenu = True
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.label(text="Click the VGroup to Select/Unselect.")
        # clear ボタン
        _Util.layout_operator(self.layout, MPM_OT_SelectVertexGroup.bl_idname,
                              text=MPM_OT_SelectVertexGroup.ID_CLEAR_SELS).vgroup_name = MPM_OT_SelectVertexGroup.ID_CLEAR_SELS
        # vgrupsボタン
        cnt = 0
        limit_rows = 25
        r = self.layout.row(align=True)
        cc = r.column(align=True)
        for k, v in self.map_vgname_to_label.items():
            _Util.layout_operator(cc, MPM_OT_SelectVertexGroup.bl_idname, text=v, isActive="vcnt=0" not in v).vgroup_name = k
            cnt += 1
            if cnt % limit_rows == 0:
                cc = r.column(align=True)

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


class MPM_OT_SelectVertexGroup(bpy.types.Operator):
    bl_idname = "op.mpm_editmesh_select_vertex_group"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    ID_CLEAR_SELS = "CLEAR SELECTION"
    vgroup_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = context.object
        if self.vgroup_name == MPM_OT_SelectVertexGroup.ID_CLEAR_SELS:
            bm = bmesh.from_edit_mesh(obj.data)
            bm.select_flush(False)
            for v in bm.verts:
                v.select = False
            bmesh.update_edit_mesh(obj.data)
            obj.update_from_editmode()
            return {"FINISHED"}
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
    bl_idname = "op.mpm_editmesh_mirror_seam"
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
    bl_idname = "op.mpm_editmesh_mirror_sharp"
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


class MPM_OT_VertCreasePanel(bpy.types.Operator):
    bl_idname = "op.mpm_editmesh_vert_crease_panel"
    bl_label = "Vert Crease"
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
        return obj and obj.type == "MESH" and any(e.select for e in bm.verts)

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
    bl_idname = "op.mpm_editmesh_edge_crease_panel"
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
    bl_idname = "op.mpm_duplicate_mirror"
    bl_label = "Mirror Duplication"
    bl_options = {'REGISTER', 'UNDO'}
    mirror_x: bpy.props.BoolProperty(name="Mirror X", default=True)
    mirror_y: bpy.props.BoolProperty(name="Mirror Y", default=False)
    mirror_z: bpy.props.BoolProperty(name="Mirror Z", default=False)

    @classmethod
    def poll(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        return any(e.select for e in bm.verts)

    def execute(self, context):
        obj = context.object
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


class MPM_OT_GenterateBoneFromEdge(bpy.types.Operator):
    bl_idname = "op.mpm_generate_bone_from_edge"
    bl_label = "Generate Bone from Selected Edge"
    bl_options = {'REGISTER', 'UNDO'}

    order_dir: bpy.props.EnumProperty(name="Order", items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")])
    order_invert: bpy.props.BoolProperty(name="Invert", description="")
    bone_chain: bpy.props.BoolProperty(name="Bone Chain", description="",  default=True)
    bone_ratio: bpy.props.FloatProperty(name="Bone Ratio", description="", default=1.0, min=0.01, max=2.0)
    slide_to_normal: bpy.props.FloatProperty(name="Slide To Normal", description="", default=0.0, min=-1.0, max=1.0)
    angle_for_isolate: bpy.props.IntProperty(
        name="Separates edge groups by vertices with edge pairs that are lower than the specified angle", description="", default=0, min=0, max=120)

    def execute(self, context):
        obj = context.object
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
                    angle = degrees(connected_vecs[0].angle(connected_vecs[1]))
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
                    bone.head = obj.matrix_world @ _Util.lerp_multi_distance(co_list, (i) / (fixed_count-1))
                    bone.tail = obj.matrix_world @ _Util.lerp_multi_distance(co_list, (i+1) / (fixed_count-1))
                    bone.head += _Util.lerp_multi_distance(n_list, (i) / (fixed_count-1)) * self.slide_to_normal
                    bone.tail += _Util.lerp_multi_distance(n_list, (i+1) / (fixed_count-1)) * self.slide_to_normal
                # print(i, (i) / fixed_count, (i+1) / fixed_count)
                # print("n=", info_list[i]["n"], info_list[i+1]["n"], self.slide_to_normal)
                bone.parent = prev_bone if self.bone_chain else None
                prev_bone = bone
                # _Util.show_report(self, f"{bone.name}, {p1}, {p2}, {bone.head}, {bone.tail}")
        return {"FINISHED"}


# --------------------------------------------------------------------------------
classes = (
    MPM_OT_MirrorSeam,
    MPM_OT_MirrorSharp,
    MPM_OT_AddVertexGroupPanel,
    MPM_OT_SelectVertexGroupPanel,
    MPM_OT_SelectVertexGroup,
    MPM_OT_VertCreasePanel,
    MPM_OT_EdgeCreasePanel,
    MPM_OT_DuplicateMirror,
    MPM_OT_GenterateBoneFromEdge,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
