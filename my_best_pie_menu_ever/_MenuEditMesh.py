if "bpy" in locals():
    import importlib
    importlib.reload(_AddonPreferences)
    importlib.reload(_Util)
    importlib.reload(_UtilInput)
    importlib.reload(_UtilBlf)
    importlib.reload(g)
else:
    from . import _AddonPreferences
    from . import _Util
    from . import _UtilInput
    from . import _UtilBlf
    from . import g
import bpy
import bmesh
from mathutils import Vector, Matrix
import time
import math
import gpu
from gpu_extras.batch import batch_for_shader
# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------


def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text="Edit Mesh Primary")
    r = box.row(align=True)
    from ._MenuObject import LayoutSwitchSelectionOperator
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
    rr.popover(panel="VIEW3D_PT_snapping", icon=icon, text="",)

    r = box.row(align=True)
    c = r.column(align=True)

    # overlay
    overlay = context.space_data.overlay
    box = c.box()
    box.label(text="Overlay", icon="OVERLAY")
    cc = box.column(align=True)
    _Util.layout_prop(cc, overlay, "show_weight", isActive=overlay.show_overlays)

    # 選択
    box = c.box()
    box.label(text="Selection", icon="ZOOM_SELECTED")
    c = box.column(align=True)
    rr = c.row(align=True)
    _Util.layout_operator(rr, "mesh.select_mirror", "Mirror").extend = False
    _Util.layout_operator(rr, "mesh.select_mirror", "", icon="ADD").extend = True
    _Util.layout_operator(c, "mesh.shortest_path_select", "Shortest Path").edge_mode = "SELECT"
    op = _Util.layout_operator(c, "mesh.select_face_by_sides", "Ngons")
    op.number = 4
    op.type = "GREATER"
    # 辺リングの拡張選択
    _Util.layout_operator(c, MPM_OT_EditMesh_GrowEdgeRingSelection.bl_idname, icon="EDGESEL")

    # UVボックス
    box = c.box()
    box.label(text="UV", icon="UV")
    c = box.column(align=True)
    rr = c.row(align=True)
    _Util.layout_operator(rr, "mesh.mark_seam").clear = False
    _Util.layout_operator(rr, "mesh.mark_seam", "", icon="REMOVE").clear = True
    row, sub = _Util.layout_for_mirror(rr)
    _Util.layout_operator(sub, MPM_OT_EditMesh_MirrorSeam.bl_idname, "", icon="ADD").is_clear = False
    _Util.layout_operator(sub, MPM_OT_EditMesh_MirrorSeam.bl_idname, "", icon="REMOVE").is_clear = True
    _Util.layout_operator(c, "uv.unwrap")

    # 頂点メニュー
    c2 = r.column()
    box = c2.box()
    box.label(text="Vertex", icon="VERTEXSEL")
    c = box.column(align=True)
    rr = c.row(align=True)
    _Util.layout_prop(rr, context.scene, "mpm_editmesh_vertcrease", "Crease", vert_crease_poll(context))
    _Util.layout_prop(rr, context.scene, "mpm_editmesh_vertbevel", "Bevel", vert_crease_poll(context))

    # 非表示
    rr = c.row(align=True)
    _Util.layout_operator(rr, MPM_OT_EditMesh_HideVerts.bl_idname, "Hide", icon="HIDE_ON").mode = "Hide"
    _Util.layout_operator(rr, MPM_OT_EditMesh_HideVerts.bl_idname, "", icon="SELECT_SUBTRACT").mode = "Hide Other"
    _Util.layout_operator(rr, MPM_OT_EditMesh_ShowVerts.bl_idname, "Show", icon="HIDE_OFF").mode = "Show"
    _Util.layout_operator(rr, MPM_OT_EditMesh_ShowVerts.bl_idname, "", icon="SELECT_EXTEND").mode = "Show Only"
    _Util.layout_operator(rr, MPM_OT_EditMesh_ShowVerts.bl_idname, "", icon="SELECT_SUBTRACT").mode = "Show Selected"
    # 3Dカーソルミラー
    rr1, rr2 = _Util.layout_split_row2(c, 0.6)
    rr1.label(text="3DCursor Mirror", icon="PIVOT_CURSOR")
    _Util.layout_operator(rr2, MPM_OT_EditMesh_MirrorBy3DCursor.bl_idname, "X").axis = "x"
    _Util.layout_operator(rr2, MPM_OT_EditMesh_MirrorBy3DCursor.bl_idname, "Y").axis = "y"
    _Util.layout_operator(rr2, MPM_OT_EditMesh_MirrorBy3DCursor.bl_idname, "Z").axis = "z"
    _Util.layout_operator(c, MPM_OT_EditMesh_PinSelectedVertsModal.bl_idname)
    rr = c.row(align=True)
    _Util.layout_operator(rr, MPM_OT_EditMesh_Ghost.bl_idname, icon="GHOST_ENABLED").with_hide = False
    _Util.layout_operator(rr, MPM_OT_EditMesh_Ghost.bl_idname, "", icon="HIDE_ON").with_hide = True

    # Edgeメニュー
    box = c2.box()
    box.label(text="Edge", icon="EDGESEL")
    c = box.column(align=True)

    # クリーズ
    rr = c.row(align=True)
    _Util.layout_prop(rr, context.scene, "mpm_editmesh_edgecrease", "Crease", edge_crease_poll(context))
    _Util.layout_prop(rr, context.scene, "mpm_editmesh_edgebevel", "Bevel", edge_crease_poll(context))
    # シャープ
    rr = c.row(align=True)
    _Util.layout_operator(rr, "mesh.mark_sharp").clear = False
    _Util.layout_operator(rr, "mesh.mark_sharp", "", icon="REMOVE").clear = True
    row, sub = _Util.layout_for_mirror(rr)
    _Util.layout_operator(sub, MPM_OT_EditMesh_MirrorSharp.bl_idname, "", icon="ADD").is_clear = False
    _Util.layout_operator(sub, MPM_OT_EditMesh_MirrorSharp.bl_idname, "", icon="REMOVE").is_clear = True
    # ボーンアーマチュア作成
    _Util.layout_operator(c, MPM_OT_EditMesh_GenterateBonesAlongSelectedEdge.bl_idname, icon="BONE_DATA")
    # 法線サイドへビューポートカメラを移動
    _Util.layout_operator(c, MPM_OT_EditMesh_AlignViewToEdgeNormalSideModal.bl_idname, icon="VIEW_CAMERA")
    # エッジループのセンタリング
    _Util.layout_operator(c, MPM_OT_EditMesh_CenteringEdgeLoop.bl_idname)

    # VertexGroupメニュー
    c = r.column()
    box = c.box()
    box.label(text="Vertex Group", icon="GROUP_VERTEX")
    c = box.column(align=True)
    rr = c.row(align=True)
    _Util.layout_operator(rr, MPM_OT_VertexGroupSelectPanel.bl_idname)
    _Util.layout_operator(rr, MPM_OT_VertexGroupNewPanel.bl_idname)
    _Util.layout_operator(rr, MPM_OT_VertexGroupAdd.bl_idname)
    _Util.layout_operator(rr, MPM_OT_VertexGroupRemove.bl_idname)
    from ._MenuWeightPaint import MirrorVertexGroup, MPM_OT_Weight_RemoveUnusedVertexGroup
    MirrorVertexGroup(c)
    _Util.layout_operator(c, MPM_OT_Weight_RemoveUnusedVertexGroup.bl_idname, icon="X")

    # Applyメニュー
    box = c.box()
    box.label(text="Apply", icon="CHECKMARK")
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
    _Util.layout_operator(c, MPM_OT_EditMesh_DuplicateMirror.bl_idname, icon="SEQ_STRIP_DUPLICATE")
    # 法線
    _Util.layout_operator(c, "mesh.normals_make_consistent", icon="NORMALS_FACE").inside = False
    # マージ
    rr = c.row(align=True)
    rr.label(text="Merge")
    _Util.layout_operator(rr, "mesh.merge", "Center").type = "CENTER"
    _Util.layout_operator(rr, "mesh.merge", "Collapse").type = "COLLAPSE"
    _Util.layout_operator(rr, "mesh.merge", "Cursor").type = "CURSOR"
    _Util.layout_operator(rr, "mesh.remove_doubles", "Distance")

    _Util.layout_operator(c, "mesh.delete_loose", icon="X")

# --------------------------------------------------------------------------------


class MPM_OT_VertexGroupNewPanel(bpy.types.Operator):
    bl_idname = "mpm.editmesh_ertex_group_new_panel"
    bl_label = "New"
    bl_options = {"REGISTER", "UNDO"}
    vgroup_name: bpy.props.StringProperty(name="Name", default="Group", description="Vertex group name")
    weight: bpy.props.FloatProperty(name="Weight", default=1.0, min=0.0, max=1.0)

    @classmethod
    def poll(self, context):
        return _Util.has_selected_verts(context)

    def invoke(self, context, event):
        g.force_cancel_piemenu_modal(context)
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.object
        bpy.ops.object.mode_set(mode="OBJECT")
        obj.vertex_groups.new(name=self.vgroup_name)
        group = obj.vertex_groups[-1]
        obj.vertex_groups.active_index = group.index
        group.add([v.index for v in obj.data.vertices if v.select], self.weight, "REPLACE")
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class MPM_OT_VertexGroupAdd(bpy.types.Operator):
    bl_idname = "mpm.editmesh_ertex_group_add"
    bl_label = "Add"
    bl_description = "Add the selected vertices to the active vertex group"
    bl_options = {"REGISTER", "UNDO"}
    weight: bpy.props.FloatProperty(name="Weight", default=1.0, min=0.0, max=1.0)

    @classmethod
    def poll(self, context):
        return _Util.has_selected_verts(context) and _Util.has_active_vgroup(context)

    def execute(self, context):
        obj = context.object
        bpy.ops.object.mode_set(mode="OBJECT")
        group = obj.vertex_groups.active
        group.add([v.index for v in obj.data.vertices if v.select], self.weight, "REPLACE")
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class MPM_OT_VertexGroupRemove(bpy.types.Operator):
    bl_idname = "mpm.editmesh_vertex_group_remove"
    bl_label = "Remove"
    bl_description = "Remove the selected vertices to the active vertex group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        return _Util.has_selected_verts(context) and _Util.has_active_vgroup(context)

    def execute(self, context):
        obj = context.object
        bpy.ops.object.mode_set(mode="OBJECT")
        group = obj.vertex_groups.active
        group.remove([v.index for v in obj.data.vertices if v.select])
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}
# --------------------------------------------------------------------------------


class MPM_OT_VertexGroupSelectPanel(bpy.types.Operator):
    bl_idname = "mpm.editmesh_vertex_group_select_panel"
    bl_label = "Select"
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
            if deform_layer:
                for i in v[deform_layer].keys():
                    self.vg_counts[i] += 1
        g.force_cancel_piemenu_modal(context)
        column_cnt = int(1 + int(len(obj.vertex_groups) / self.limit_rows))
        return context.window_manager.invoke_props_dialog(self, width=max(200, self.single_width * column_cnt))

    def draw(self, context):
        self.layout.label(text="Click the VGroup to Select/Unselect.")
        _Util.MPM_OT_CallbackOperator.operator(self.layout, "Deselect All", self.bl_idname + ".clear",
                                               self.on_click_clear, (context, ), "X", _Util.has_selected_verts(context))
        # vgrupsボタン
        cnt = 0
        r = self.layout.row(align=False)
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


class MPM_OT_EditMesh_HideVerts(bpy.types.Operator):
    bl_idname = "mpm.editmesh_hide_verts"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Hides the selected vertex.
Option1: Invert."""
    mode: bpy.props.EnumProperty(name="Mode", items=[("Hide", "Hide", ""), ("Hide Other", "Hide Other", "")])

    @classmethod
    def poll(self, context):
        return _Util.has_selected_verts(context)

    def execute(self, context):
        if self.mode == "Hide":
            return bpy.ops.mesh.hide(unselected=False)
        else:
            return bpy.ops.mesh.hide(unselected=True)


class MPM_OT_EditMesh_ShowVerts(bpy.types.Operator):
    bl_idname = "mpm.editmesh_show_verts"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Show the hide vertices.
Option1: Selection will be expanded to include the shown vertices.
Option2: Selection will be refreshed to match the shown vertices."""
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


class MPM_OT_EditMesh_MirrorBy3DCursor(bpy.types.Operator):
    bl_idname = "mpm.editmesh_mirror_by_3dcursor"
    bl_label = ""
    bl_options = {"UNDO"}
    bl_description = "Mirrors vertices based on the position of the 3D cursor"
    axis: bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        return _Util.has_selected_verts(context)

    def execute(self, context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        cur_pos_local = obj.matrix_world.inverted() @ bpy.context.scene.cursor.location
        selected_verts = [v for v in bm.verts if v.select]
        if len(selected_verts) != 2 or not isinstance(bm.select_history.active, bmesh.types.BMVert):
            for vert in selected_verts:
                if self.axis == "x":
                    vert.co.x = cur_pos_local.x - (vert.co.x - cur_pos_local.x)
                elif self.axis == "y":
                    vert.co.y = cur_pos_local.y - (vert.co.y - cur_pos_local.y)
                else:
                    vert.co.z = cur_pos_local.z - (vert.co.z - cur_pos_local.z)
        else:
            active = bm.select_history.active
            other = selected_verts[1] if selected_verts[0] == active else selected_verts[0]
            other.co = active.co.copy()
            if self.axis == "x":
                other.co.x = cur_pos_local.x - (active.co.x - cur_pos_local.x)
            elif self.axis == "y":
                other.co.y = cur_pos_local.y - (active.co.y - cur_pos_local.y)
            else:
                other.co.z = cur_pos_local.z - (active.co.z - cur_pos_local.z)
        bmesh.update_edit_mesh(obj.data)
        return {"FINISHED"}

# --------------------------------------------------------------------------------


class MPM_OT_EditMesh_MirrorSeam(bpy.types.Operator):
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


class MPM_OT_EditMesh_MirrorSharp(bpy.types.Operator):
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


def vert_crease_poll(context):
    return _Util.has_selected_verts(context)


def edge_crease_poll(context):
    return _Util.has_selected_edges(context)


def vert_crease_get(self):
    if not _Util.has_selected_verts(bpy.context):
        return 0
    obj = bpy.context.edit_object
    bm = bmesh.from_edit_mesh(obj.data)
    return get_layer_property(obj, bm, bm.verts.layers.float, "crease_vert")


def vert_crease_set(self, value):
    obj = bpy.context.edit_object
    bm = bmesh.from_edit_mesh(obj.data)
    return set_layer_property(obj, bm, bm.verts.layers.float, "crease_vert", value)


def vert_bevel_weight_get(self):
    if not _Util.has_selected_verts(bpy.context):
        return 0
    obj = bpy.context.edit_object
    bm = bmesh.from_edit_mesh(obj.data)
    return get_layer_property(obj, bm, bm.verts.layers.float, "bevel_weight_vert")


def vert_bevel_weight_set(self, value):
    obj = bpy.context.edit_object
    bm = bmesh.from_edit_mesh(obj.data)
    return set_layer_property(obj, bm, bm.verts.layers.float, "bevel_weight_vert", value)


def edge_crease_get(self):
    if not _Util.has_selected_edges(bpy.context):
        return 0
    obj = bpy.context.edit_object
    bm = bmesh.from_edit_mesh(obj.data)
    return get_layer_property(obj, bm, bm.edges.layers.float, "crease_edge")


def edge_crease_set(self, value):
    obj = bpy.context.edit_object
    bm = bmesh.from_edit_mesh(obj.data)
    return set_layer_property(obj, bm, bm.edges.layers.float, "crease_edge", value)


def edge_bevel_weight_get(self):
    if not _Util.has_selected_edges(bpy.context):
        return 0
    obj = bpy.context.edit_object
    bm = bmesh.from_edit_mesh(obj.data)
    return get_layer_property(obj, bm, bm.edges.layers.float, "bevel_weight_edge")


def edge_bevel_weight_set(self, value):
    obj = bpy.context.edit_object
    bm = bmesh.from_edit_mesh(obj.data)
    return set_layer_property(obj, bm, bm.edges.layers.float, "bevel_weight_edge", value)


def get_layer_property(obj, bm, layer_correction, prop_name):
    # print(bm.verts.layers.float.items())
    item = layer_correction.get(prop_name, None)
    if item is None:
        item = layer_correction.new(prop_name)
        return 0
    targets = bm.verts if "vert" in prop_name else bm.edges
    values = [v[item] for v in targets if v.select]
    return sum(values) / len(values)


def set_layer_property(obj, bm, layer_correction, prop_name, value):
    item = layer_correction.get(prop_name, None)
    if item is None:
        item = layer_correction.new(prop_name)
        return 0
    targets = bm.verts if "vert" in prop_name else bm.edges
    for v in [v for v in targets if v.select]:
        v[item] = value
    bmesh.update_edit_mesh(obj.data)


# --------------------------------------------------------------------------------


class MPM_OT_EditMesh_DuplicateMirror(bpy.types.Operator):
    bl_idname = "mpm.duplicate_mirror"
    bl_label = "Mirror Duplication"
    bl_options = {"REGISTER", "UNDO"}
    mirror_x: bpy.props.BoolProperty(name="Mirror X", default=True)
    mirror_y: bpy.props.BoolProperty(name="Mirror Y", default=False)
    mirror_z: bpy.props.BoolProperty(name="Mirror Z", default=False)

    @classmethod
    def poll(self, context):
        return _Util.has_selected_verts(context)

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


class MPM_OT_EditMesh_GenterateBonesAlongSelectedEdge(bpy.types.Operator):
    bl_idname = "mpm.generate_along_from_edge"
    bl_label = "Generate bones along selected edges"
    bl_description = "Generates bones along the selected edge"
    bl_options = {"REGISTER", "UNDO"}

    order_dir: bpy.props.EnumProperty(name="Order", items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")])
    order_invert: bpy.props.BoolProperty(name="Invert", description="")
    bone_chain: bpy.props.BoolProperty(name="Bone Chain", description="",  default=True)
    bone_ratio: bpy.props.FloatProperty(name="Bone Ratio", description="", default=1.0, min=0.01, max=2.0)
    slide_to_normal: bpy.props.FloatProperty(name="Slide To Normal", description="", default=0.0, min=-1.0, max=1.0)
    angle_for_isolate: bpy.props.IntProperty(
        name="Angle For Isolate", description="Separates edge groups by vertices with edge pairs that are lower than the specified angle", default=0, min=0, max=120)

    @classmethod
    def poll(self, context):
        return _Util.has_selected_edges(context)

    def invoke(self, context, event):
        self.target_object = context.edit_object
        self.target_armature = None
        g.force_cancel_piemenu_modal(context)
        return context.window_manager.invoke_props_popup(self, event)

    def draw(self, context):
        layout = self.layout
        c = layout.column(align=True)
        c.prop(self, "order_dir")
        c.prop(self, "order_invert")
        c.prop(self, "bone_chain")
        c.prop(self, "bone_ratio")
        c.prop(self, "slide_to_normal")
        c.prop(self, "angle_for_isolate")
        _Util.MPM_OT_CallbackOperator.operator(c, "Execute", self.bl_idname,
                                               self.execute, (context, ))

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        _Util.select_active(self.target_object)
        bpy.ops.object.mode_set(mode="EDIT")
        obj = self.target_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

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
        if self.target_armature is None:
            bpy.ops.object.armature_add()
            self.target_armature = armature = context.object
            armature.name = "bones_from_edges"
        else:
            armature = self.target_armature
            _Util.select_active(armature)
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


class MPM_OT_EditMesh_GenterateBonesAlongSelectedEdgeInternal(bpy.types.Operator):
    bl_idname = "mpm.generate_along_from_edge_internal"
    bl_label = ""
    bl_options = {'INTERNAL'}  # UIに出ない

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.armature_add()
        armature = context.object
        armature.name = "bones_from_edges"
        # ボーン追加
        bpy.ops.object.mode_set(mode="EDIT")
        edit_bones = armature.data.edit_bones
        for bone in edit_bones:
            edit_bones.remove(bone)
        return {"FINISHED"}


class MPM_OT_EditMesh_AlignViewToEdgeNormalSideModal(bpy.types.Operator):
    bl_idname = "mpm.align_view_to_edge_normal_side_modal"
    bl_label = "Align view to edge normal side"
    bl_description = "Transition the view to a position looking perpendicular to the normal of the selected edge along any axis"

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
    mouse_pos: Vector = Vector((0, 0, 0))

    @classmethod
    def poll(self, context):
        return _Util.has_selected_edges(context)

    def invoke(self, context, event):
        self.is_reverting = False
        self.mouse_pos.x = event.mouse_x
        self.mouse_pos.y = event.mouse_y
        self.original_location = context.region_data.view_location.copy()
        self.original_rotation = context.region_data.view_rotation.copy()
        self.timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        self.label_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_label, (), "WINDOW", "POST_PIXEL")
        g.force_cancel_piemenu_modal(context)
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
                    # 平均法線
                    normal = Vector((0, 0, 0))
                    for face in connected_faces:
                        normal += face.normal
                    total_normal += normal.normalized()
            average_center = total_center / len(selected_edges)
        self.average_normal = total_normal.normalized()
        self.target_location = average_center
        return self.execute(context)

    def execute(self, context):
        # 法線に対して横方向を計算
        # side_vector = average_direction.cross(average_normal).normalized()
        # side_vector = average_normal.cross(_Util.VEC3_Z()).normalized()
        side_vector = Vector(self.dir).cross(self.average_normal).normalized()
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
        # self.target_location = average_center
        self.elapsed = 0.0
        self.start_time = time.time()
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
        # アニメ
        if self.elapsed <= self.translate_duration:
            self.elapsed = time.time() - self.start_time
            t = min(1.0, self.elapsed / self.translate_duration)
            context.region_data.view_location = self.start_location.lerp(self.target_location, t)
            context.region_data.view_rotation = self.start_rotation.slerp(self.target_rotation, t)
            return {"RUNNING_MODAL"}

        context.area.tag_redraw()
        self.mouse_pos.x = _Util.lerp(self.mouse_pos.x, event.mouse_x, 0.05)
        self.mouse_pos.y = _Util.lerp(self.mouse_pos.y, event.mouse_y, 0.05)
        _UtilInput.update(event, "X", "Y", "Z", "LEFTMOUSE", "RET", "RIGHTMOUSE", "ESC", "SPACE", "RET")
        if _UtilInput.is_pressed_key("X"):
            self.dir = Vector((-1 if self.dir[0] == 1 else 1, 0, 0))
            return self.execute(context)
        if _UtilInput.is_pressed_key("Y"):
            self.dir = Vector((0, -1 if self.dir[1] == 1 else 1, 0))
            return self.execute(context)
        if _UtilInput.is_pressed_key("Z"):
            if event.alt:
                context.space_data.shading.show_xray = not context.space_data.shading.show_xray
            else:
                self.dir = Vector((0, 0, -1 if self.dir[2] == 1 else 1))
                return self.execute(context)
        if event.type == "WHEELUPMOUSE":
            context.region_data.view_distance -= 0.5
            return {"RUNNING_MODAL"}
        elif event.type == "WHEELDOWNMOUSE":
            context.region_data.view_distance += 0.5
            return {"RUNNING_MODAL"}
        if _UtilInput.is_pressed_key("LEFTMOUSE", "RET"):
            return self.cancel(context)
        if _UtilInput.is_pressed_key("RIGHTMOUSE", "ESC", "SPACE", "RET"):
            self.is_reverting = True
            self.start_time = time.time()
            return {"RUNNING_MODAL"}
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        # _Util.show_report(self, "CANCELLED")
        if self.label_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self.label_handler, "WINDOW")
            context.area.tag_redraw()
            self.label_handler = None
        if self.timer:
            context.window_manager.event_timer_remove(self.timer)
            self.timer = None
        return {"CANCELLED"}

    def draw_label(self):
        if self.is_reverting:
            return
        fid = 0  # デフォルトのフォントを使用
        x = _Util.clamp(self.mouse_pos.x - bpy.context.area.x, 0, bpy.context.area.width)
        y = _Util.clamp(self.mouse_pos.y - bpy.context.area.y, 0, bpy.context.area.height)
        _UtilBlf.animate_clipping(fid, x, 500, self.timer.time_duration)
        _UtilBlf.draw_title(fid, "Align view to edge normal side", x, y)
        text = ""
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


class MPM_OT_EditMesh_GrowEdgeRingSelection(bpy.types.Operator):
    bl_idname = "mpm.editmesh_grow_edge_ring_selection"
    bl_label = "Edge Ring Ex"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    steps: bpy.props.IntProperty(name="Steps", default=1, min=1)
    skip_offset: bpy.props.IntProperty(name="Skip Offset", default=0, min=0)
    direction: bpy.props.EnumProperty(
        name="Direction",
        items=[
            ("BOTH", "Both", "Expand in both directions"),
            ("FORWARD", "Forward", "Expand only in forward direction"),
            ("BACKWARD", "Backward", "Expand only in backward direction"),
        ],
        default="BOTH"
    )
    alignment: bpy.props.EnumProperty(
        name="Alignment",
        items=[
            ("None", "None", ""),
            ("X+", "X+", ""),
            ("X-", "X-", ""),
            ("Y+", "Y+", ""),
            ("Y-", "Y-", ""),
            ("Z+", "Z+", ""),
            ("Z-", "Z-", ""),
        ],
        default="None"
    )

    @classmethod
    def poll(self, context):
        return _Util.has_selected_edges(context)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        c = layout.column(align=True)
        c.prop(self, "steps")
        c.prop(self, "skip_offset")
        c.prop(self, "direction")
        r = c.row(align=True)
        r.enabled = self.direction != "BOTH"
        r.prop(self, "alignment")

    def invoke(self, context, event):
        self.steps = 0
        return self.execute(context)

    def execute(self, context):
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)

        selected_edges = [e for e in bm.edges if e.select]
        visited_edges = set(selected_edges)
        result_edges = set()
        candidate_edges = list()
        to_visit = list()
        to_visit_next = list()
        face_list = list()
        edge_verts_set = set()

        alignment_filter_func = self.get_alignment_filter_func()

        for edge in selected_edges:
            current_step = 0
            current_offset = self.skip_offset
            to_visit.clear()
            to_visit_next.clear()
            to_visit_next.append(edge)
            while to_visit_next:
                to_visit.extend(to_visit_next)
                to_visit_next.clear()
                while to_visit:
                    edge = to_visit.pop(0)
                    edge_verts_set.clear()
                    edge_verts_set.update(edge.verts)
                    candidate_edges.clear()
                    face_list.clear()
                    face_list.extend(edge.link_faces)
                    if self.direction == "BACKWARD":
                        face_list.reverse()
                    for face in face_list:
                        for loop in face.loops:
                            other_edge = loop.edge
                            # 各エッジの頂点が重複している
                            if edge_verts_set & set(other_edge.verts):
                                continue
                            # 一旦、候補用のリストに格納して後でまとめて比較して、最適なものを処理する
                            if other_edge not in visited_edges:
                                candidate_edges.insert(0, other_edge)  # appendより安定する。
                                break
                    # 片方向かつ、複数が見つかっている場合はアラインメントに適した方を採用する
                    if 1 < len(candidate_edges) and self.direction != "BOTH":
                        for candidate_edge in candidate_edges:
                            if alignment_filter_func(edge, candidate_edge):
                                continue
                            if current_offset == 0:
                                result_edges.add(candidate_edge)
                            visited_edges.add(candidate_edge)
                            to_visit_next.append(candidate_edge)
                            break
                    else:
                        if current_offset == 0:
                            result_edges.update(candidate_edges)
                        visited_edges.update(candidate_edges)
                        to_visit_next.extend(candidate_edges)

                current_offset -= 1
                if current_offset < 0:
                    current_offset = self.skip_offset
                # step処理
                current_step += 1
                if self.steps <= current_step:
                    current_step = 0
                    break
        for edge in result_edges:
            edge.select_set(True)
        bmesh.update_edit_mesh(obj.data)
        return {"FINISHED"}

    def get_alignment_filter_func(self):
        if self.direction == "BOTH" or self.alignment == "None":
            return lambda edge, other_edge: False
        if self.alignment == "X+":
            return lambda edge, other_edge: other_edge.verts[0].co.x < edge.verts[0].co.x
        elif self.alignment == "X-":
            return lambda edge, other_edge: other_edge.verts[0].co.x > edge.verts[0].co.x
        elif self.alignment == "Y+":
            return lambda edge, other_edge: other_edge.verts[0].co.y < edge.verts[0].co.y
        elif self.alignment == "Y-":
            return lambda edge, other_edge: other_edge.verts[0].co.y > edge.verts[0].co.y
        elif self.alignment == "Z+":
            return lambda edge, other_edge: other_edge.verts[0].co.z < edge.verts[0].co.z
        elif self.alignment == "Z-":
            return lambda edge, other_edge: other_edge.verts[0].co.z > edge.verts[0].co.z
        else:
            return lambda edge, other_edge: False


class MPM_OT_EditMesh_CenteringEdgeLoop(bpy.types.Operator):
    bl_idname = "mpm.editmesh_centering_edge_loop"
    bl_label = "Centering Edge Ring"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    bias: bpy.props.FloatProperty(name="Bias", default=0.5, min=0, max=1)

    @classmethod
    def poll(self, context):
        return _Util.has_selected_edges(context) and context.tool_settings.mesh_select_mode[1]

    def execute(self, context):
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = [e for e in bm.verts if e.select]
        selected_edges = [e for e in bm.edges if e.select]
        # 隣接するエッジリングを取得
        adjacent_ring_edges = set()
        for e in selected_edges:
            for face in e.link_faces:
                for other_edge in face.edges:
                    if other_edge is e:
                        continue
                    # エッジ同士が1つの頂点だけ共有していれば隣接とみなす
                    shared_verts = _Util.Temp.intersect_sets(e.verts, other_edge.verts)
                    if len(shared_verts) == 1:
                        adjacent_ring_edges.add(other_edge)
        # 両サイドの端エッジを取得
        end_edges = []
        for e in adjacent_ring_edges:
            connected = 0
            for v in e.verts:
                for linked_edge in v.link_edges:
                    if linked_edge != e and linked_edge in adjacent_ring_edges:
                        connected += 1
            if connected == 1:
                end_edges.append(e)
        # 一つ端っこの頂点を取得する
        edge = min(end_edges, key=lambda e: (e.verts[0].co + e.verts[1].co) / 2)
        cur_v = edge.verts[1] if edge.verts[0] in selected_verts else edge.verts[0]
        # 端っこの頂点リストを取得
        end_edge_verts = [cur_v]
        stack = [cur_v]
        visited = {cur_v}
        while stack:
            v = stack.pop()
            # 最初の端の頂点から繋がる辺
            for e in v.link_edges:
                # 端エッジリストに含まれない辺
                if not e in end_edges:
                    other_vert = e.other_vert(v)  # 端の頂点の隣接頂点
                    # 一度見た頂点はスキップ
                    if other_vert in visited:
                        continue
                    visited.add(other_vert)
                    # 端エッジリストから隣接頂点が含まれるかどうか確認
                    for ee in end_edges:
                        if other_vert in ee.verts:
                            stack.append(other_vert)
                            end_edge_verts.append(other_vert)
        # 端っこの頂点から、反対の端の頂点までのリストを作成
        edge_ring_verts = []
        for v in end_edge_verts:
            verts = [v]
            stack.clear()
            stack.append(v)
            while stack:
                v = stack.pop()
                for e in v.link_edges:
                    if e in adjacent_ring_edges:
                        ov = e.other_vert(v)
                        stack.append(ov)
                        verts.append(ov)
                        adjacent_ring_edges.remove(e)
            edge_ring_verts.append(verts)
        # 位置更新
        for verts in edge_ring_verts:
            start = verts[0].co.copy()
            end = verts[-1].co.copy()
            cnt = len(verts) - 1
            # 中間の頂点を線形補完
            for i in range(1, cnt):
                linear = i / cnt
                factor = 0.5 + (linear - 0.5) * (1 - self.bias)
                verts[i].co = start.lerp(end, self.remap(linear, self.bias))

        bmesh.update_edit_mesh(obj.data)
        return {"FINISHED"}

    def remap(self, linear, bias):
        if linear == 0.5 or bias == 0.5:
            return linear
        # 偏差（中央からどれだけ離れているか）
        deviation = linear - 0.5
        # 吸着の強さ：bias < 0.5 で中央に、bias > 0.5 で端に吸着
        factor = abs(bias - 0.5) * 2  # 0〜1の範囲
        if bias < 0.5:
            # 中央に近づける
            return linear - deviation * factor
        else:
            # 中心から遠ざける
            return linear + deviation * factor
# --------------------------------------------------------------------------------


class MPM_OT_EditMesh_PinSelectedVertsModal(bpy.types.Operator):
    bl_idname = "mpm.editmesh_pin_selected_verts_modal"
    bl_label = "Pin Selected"
    bl_description = ""
    attr_name = "mpm_tmp_vcolor"
    draw_modal = None
    mx, my = 0.0, 0.0

    @classmethod
    def poll(self, context):
        return _Util.has_selected_verts(context)

    def invoke(self, context, event):
        # 頂点カラー表示
        self.set_shading_color(context, "VERTEX")
        obj = context.edit_object
        self.fixed_positions = {}
        self.obj_data = obj.data
        # self.bmに入れないと後でbm.vertの参照がNoneになる
        self.bm = bmesh.from_edit_mesh(self.obj_data)
        self.bm.verts.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()
        color_layers = self.bm.verts.layers.color
        if self.attr_name in color_layers:
            color_layers.remove(color_layers[self.attr_name])
        attr = color_layers.new(self.attr_name)
        # アクティブ化
        for i, a in enumerate(obj.data.color_attributes):
            if a.name == self.attr_name:
                obj.data.color_attributes.active_color_index = i
                break
        for v in self.bm.verts:
            if v.select:
                v[attr] = (0.3, 0.3, 0.3, 1)
                self.fixed_positions[v] = v.co.copy()
            else:
                v[attr] = (1, 1, 1, 1)
        bmesh.update_edit_mesh(self.obj_data)
        cls = MPM_OT_EditMesh_PinSelectedVertsModal
        if not cls.draw_modal:
            context.window_manager.modal_handler_add(self)
            cls.draw_modal = cls.DrawModal()
        g.force_cancel_piemenu_modal(context)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        cls = MPM_OT_EditMesh_PinSelectedVertsModal
        cls.mx = event.mouse_x
        cls.my = event.mouse_y
        context.area.tag_redraw()  # draw2dを毎フレーム呼ぶため。
        _UtilInput.update(event, "LEFTMOUSE", "ESC")
        if context.object.mode != "EDIT":  # モード変更でキャンセル
            return self.cancel(context)
        if cls.draw_modal.is_hover_cancel and _UtilInput.is_pressed_key("LEFTMOUSE"):
            return self.cancel(context)
        # undo時にbm参照が失われるので例外キャッチで再作成
        try:
            for v, pos in self.fixed_positions.items():
                v.co = pos
            bmesh.update_edit_mesh(self.obj_data)
        except Exception as e:
            # print(e)
            self.bm = bmesh.from_edit_mesh(self.obj_data)
            self.bm.verts.ensure_lookup_table()
            self.bm.edges.ensure_lookup_table()
            self.fixed_positions.clear()
            attr = self.bm.verts.layers.color.get(self.attr_name, None)
            # undoして属性追加がundoされたらNoneになる
            if not attr:
                return self.cancel(context)
            for v in self.bm.verts:
                if v[attr][0] < 1:
                    self.fixed_positions[v] = v.co.copy()
            if 0 == len(self.fixed_positions):
                return self.cancel(context)
        return {"PASS_THROUGH"}

    def cancel(self, context):
        context.area.tag_redraw()
        self.bm = None
        self.obj_data = None
        MPM_OT_EditMesh_PinSelectedVertsModal.draw_modal = None
        self.set_shading_color(context, "MATERIAL")
        return {"CANCELLED"}

    def set_shading_color(self, context, mode):
        view = context.space_data
        shading = view.shading if view.type == "VIEW_3D" else context.scene.display.shading
        shading.color_type = mode

    class DrawModal(_Util.MPM_OT_ModalMonitor):
        def __init__(self):
            super().__init__()
            self.handler2d = bpy.types.SpaceView3D.draw_handler_add(self.draw2d, (), "WINDOW", "POST_PIXEL")
            self.is_hover_cancel = False
            g.space_view_command_display_stack_sety("pin verts")

        def draw2d(self):
            cls = MPM_OT_EditMesh_PinSelectedVertsModal
            if cls.draw_modal == None:
                self.cancel()
                return
            # label
            x, y = g.space_view_command_display_begin_pos("pin verts")
            _UtilBlf.draw_label(0, "Pin Selected Verts: ", x, y, "right")
            self.is_hover_cancel = _UtilBlf.draw_label_mousehover(0, "[X]", "left click: Cancelling pin verts.",
                                                                  x, y, cls.mx, cls.my, active=self.is_hover_cancel, align="left")

        def cancel(self):
            super().cancel()
            if self.handler2d:
                bpy.types.SpaceView3D.draw_handler_remove(self.handler2d, "WINDOW")
            self.handler2d = None
            g.space_view_command_display_stack_remove("pin verts")


class MPM_OT_EditMesh_Ghost(bpy.types.Operator):
    bl_idname = "mpm.editmesh_ghost"
    bl_label = "Add Ghost of Selection"
    bl_description = "Add a ghost of the current selection. Listed below the viewport — click 'X' to remove."
    with_hide:  bpy.props.BoolProperty()
    mx, my = 0.0, 0.0
    current_hover_idx, current_focus_type = -1, ""
    modals = []

    @classmethod
    def poll(self, context):
        if context.mode == "EDIT_MESH":
            return _Util.has_selected_verts(context)
        return context.mode == "OBJECT" and context.object.type == "MESH"

    def invoke(self, context, event):
        cls = MPM_OT_EditMesh_Ghost
        if not cls.modals:
            context.window_manager.modal_handler_add(self)
        cls.modals.append(MPM_OT_EditMesh_Ghost.DrawModal.make_instance(context.active_object))
        if self.with_hide:
            bpy.ops.mesh.hide(unselected=False)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        # このモーダルは最後のDrawModalまで生存
        cls = MPM_OT_EditMesh_Ghost
        if not cls.modals:
            g.space_view_command_display_stack_remove("ghost")
            return {"CANCELLED"}
        g.space_view_command_display_stack_sety("ghost", len(self.modals) * (_UtilBlf.LABEL_SIZE_Y * 2))
        context.area.tag_redraw()  # draw2dを毎フレーム呼ぶため。
        cls.mx = event.mouse_x
        cls.my = event.mouse_y
        _UtilInput.update(event, "LEFTMOUSE", "RIGHTMOUSE")
        if 0 <= cls.current_hover_idx:
            modal = cls.modals[cls.current_hover_idx]
            if cls.current_focus_type == "depth_test" and _UtilInput.is_pressed_key("LEFTMOUSE"):
                modal.depth_test = "LESS_EQUAL" if modal.depth_test != "LESS_EQUAL" else "ALWAYS"
                return {"RUNNING_MODAL"}
            elif cls.current_focus_type == "remove" and _UtilInput.is_pressed_key("LEFTMOUSE"):
                modal.cancel()
                cls.current_hover_idx = -1
                if event.shift:
                    bpy.ops.mesh.reveal(select=False)
                return {"RUNNING_MODAL"}
            elif cls.current_focus_type == "extrude":
                if event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
                    value = 0.05 if event.shift else 0.01
                    modal.extrude_offset += value if event.type == "WHEELUPMOUSE" else -value
                    modal.make_batch()
                    return {"RUNNING_MODAL"}
                elif _UtilInput.is_pressed_key("RIGHTMOUSE"):
                    modal.extrude_offset = 0
                    modal.make_batch()
                    return {"RUNNING_MODAL"}
        return {"PASS_THROUGH"}

    class DrawModal(_Util.MPM_OT_ModalMonitor):
        shader = None

        def __init__(self):
            super().__init__()
            self.verts = []
            self.edges = []
            self.normals = []
            self.tris = []
            self.obj = None
            self.extrude_offset = 0.0001
            self.batch_v = None
            self.batch_e = None
            self.batch_f = None
            self.handler3d = None
            self.handler2d = None
            self.depth_test = "LESS_EQUAL"
            if MPM_OT_EditMesh_Ghost.DrawModal.shader is None:
                MPM_OT_EditMesh_Ghost.DrawModal.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        @classmethod
        def make_instance(cls, obj):
            c = cls()
            c.Obj = obj
            # 常に編集モードでの編集後のメッシュ情報が欲しいため、一時メッシュを取得する
            depsgraph = bpy.context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)
            bm = bmesh.new()
            bm.from_mesh(obj_eval.to_mesh())
            obj_eval.to_mesh_clear()  # しないとメモリリークする
            bm.verts.ensure_lookup_table()
            bm.faces.ensure_lookup_table()
            bm.normal_update()
            vert_index_map = {}
            cnt = 0
            for v in bm.verts:
                if bpy.context.mode == "OBJECT" or v.select:
                    c.verts.append(obj.matrix_world @ v.co)
                    c.normals.append(v.normal)  # obj.matrix_world @ v.normalとすると、ワールド原点をピボットになる。
                    vert_index_map[v] = cnt
                    cnt += 1
            for e in bm.edges:
                v1, v2 = e.verts
                if v1 in vert_index_map and v2 in vert_index_map:
                    c.edges.append((vert_index_map[v1], vert_index_map[v2]))
            for tri in bm.calc_loop_triangles():
                for loop in tri:
                    if bpy.context.mode == "OBJECT" or loop.face.select:
                        try:
                            idxs = [vert_index_map[loop.vert] for loop in tri]
                            c.tris.append(idxs)
                        except KeyError:
                            # 選択された頂点以外が混ざっている三角形はスキップ
                            pass
            bm.free()
            c.make_batch()
            c.handler3d = bpy.types.SpaceView3D.draw_handler_add(c.draw3d, (), "WINDOW", "POST_VIEW")  # POST_VIEWは3D用
            c.handler2d = bpy.types.SpaceView3D.draw_handler_add(c.draw2d, (), "WINDOW", "POST_PIXEL")  # POST_VIEWは3D用
            return c

        def make_batch(self):
            verts = [(v + n * self.extrude_offset) for v, n in zip(self.verts, self.normals)]
            self.batch_v = batch_for_shader(MPM_OT_EditMesh_Ghost.DrawModal.shader, "POINTS", {"pos": verts})
            self.batch_e = batch_for_shader(MPM_OT_EditMesh_Ghost.DrawModal.shader, "LINES", {"pos": verts}, indices=self.edges)
            self.batch_f = batch_for_shader(MPM_OT_EditMesh_Ghost.DrawModal.shader, "TRIS", {"pos": verts}, indices=self.tris)

        def draw3d(self):
            shader = MPM_OT_EditMesh_Ghost.DrawModal.shader
            if not shader:
                self.cancel()
                return
            shader.bind()
            # 面
            gpu.state.depth_test_set(self.depth_test)
            gpu.state.blend_set("ALPHA")
            shader.bind()
            shader.uniform_float("color", _AddonPreferences.Accessor.get_ref().ghostColorFace)
            self.batch_f.draw(shader)
            # 辺
            gpu.state.line_width_set(2.0)
            shader.uniform_float("color", _AddonPreferences.Accessor.get_ref().ghostColorEdge)
            self.batch_e.draw(shader)
            # 頂点
            gpu.state.point_size_set(5.0)
            shader.uniform_float("color", _AddonPreferences.Accessor.get_ref().ghostColorVertex)
            self.batch_v.draw(shader)
            gpu.state.blend_set("NONE")

        def draw2d(self):
            ghost_cls = MPM_OT_EditMesh_Ghost
            if not self in ghost_cls.modals:
                self.cancel()
                return
            index = ghost_cls.modals.index(self)
            if ghost_cls.current_hover_idx == index:
                ghost_cls.current_hover_idx = -1
                ghost_cls.current_focus_type = ""
            # label
            text = "Ghost: "
            w, h = _UtilBlf.draw_label_dimensions(0, text)
            h *= 2
            x, y = g.space_view_command_display_begin_pos("ghost")
            y += h * index
            _UtilBlf.draw_label(0, text, x, y, "right")
            # depth test button
            x += 10
            if _UtilBlf.draw_label_mousehover(0, self.depth_test, "left click: Change depth test mode.",
                                              x, y, ghost_cls.mx, ghost_cls.my, active=ghost_cls.current_hover_idx == index and ghost_cls.current_focus_type == "depth_test", align="left"):
                ghost_cls.current_hover_idx = index
                ghost_cls.current_focus_type = "depth_test"
            # extrude value
            w, h = _UtilBlf.draw_label_dimensions(0, "LESS_EQUAL")
            x += 10 + w
            if _UtilBlf.draw_label_mousehover(0, f"{self.extrude_offset:.3f}", "mouse wheel: Adjust extrusion distance.(shift: Increase amount)",
                                              x, y, ghost_cls.mx, ghost_cls.my, active=ghost_cls.current_hover_idx == index and ghost_cls.current_focus_type == "extrude", align="left"):
                ghost_cls.current_hover_idx = index
                ghost_cls.current_focus_type = "extrude"
            # remove button
            w, h = _UtilBlf.draw_label_dimensions(0, "-00.00")
            x += 10 + w
            if _UtilBlf.draw_label_mousehover(0, "[X]", "left click: Remove ghost.(shift: With unhide verts)",
                                              x, y, ghost_cls.mx, ghost_cls.my, active=ghost_cls.current_hover_idx == index and ghost_cls.current_focus_type == "remove", align="left"):
                ghost_cls.current_hover_idx = index
                ghost_cls.current_focus_type = "remove"

        def cancel(self):
            # print("cancel")
            super().cancel()
            if self.handler3d:
                bpy.types.SpaceView3D.draw_handler_remove(self.handler3d, "WINDOW")
            self.handler3d = None
            if self.handler2d:
                bpy.types.SpaceView3D.draw_handler_remove(self.handler2d, "WINDOW")
            self.handler2d = None
            if self in MPM_OT_EditMesh_Ghost.modals:
                MPM_OT_EditMesh_Ghost.modals.remove(self)


# --------------------------------------------------------------------------------
classes = (
    MPM_OT_EditMesh_MirrorSeam,
    MPM_OT_EditMesh_MirrorSharp,
    MPM_OT_VertexGroupNewPanel,
    MPM_OT_VertexGroupSelectPanel,
    MPM_OT_VertexGroupAdd,
    MPM_OT_VertexGroupRemove,
    MPM_OT_EditMesh_HideVerts,
    MPM_OT_EditMesh_ShowVerts,
    MPM_OT_EditMesh_DuplicateMirror,
    MPM_OT_EditMesh_GenterateBonesAlongSelectedEdge,
    MPM_OT_EditMesh_GenterateBonesAlongSelectedEdgeInternal,
    MPM_OT_EditMesh_AlignViewToEdgeNormalSideModal,
    MPM_OT_EditMesh_MirrorBy3DCursor,
    MPM_OT_EditMesh_GrowEdgeRingSelection,
    MPM_OT_EditMesh_CenteringEdgeLoop,
    MPM_OT_EditMesh_PinSelectedVertsModal,
    MPM_OT_EditMesh_Ghost,
)


def register():
    bpy.types.Scene.mpm_editmesh_vertcrease = bpy.props.FloatProperty(min=0, max=1, get=vert_crease_get, set=vert_crease_set)
    bpy.types.Scene.mpm_editmesh_vertbevel = bpy.props.FloatProperty(min=0, max=1, get=vert_bevel_weight_get, set=vert_bevel_weight_set)
    bpy.types.Scene.mpm_editmesh_edgecrease = bpy.props.FloatProperty(min=0, max=1, get=edge_crease_get, set=edge_crease_set)
    bpy.types.Scene.mpm_editmesh_edgebevel = bpy.props.FloatProperty(min=0, max=1, get=edge_bevel_weight_get, set=edge_bevel_weight_set)
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
