import os
import bpy
import bmesh
from . import _Util
from . import _AddonPreferences
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
# --------------------------------------------------------------------------------
# スカルプトモードメニュー
# 'use_paint_antialiasing', 'use_paint_grease_pencil', 'use_paint_image', 'use_paint_sculpt', 'use_paint_sculpt_curves', 'use_paint_uv_sculpt', 'use_paint_vertex', 'use_paint_weight'
# --------------------------------------------------------------------------------


def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text="Sculpt Primary")

    c = box.column()
    _Util.layout_operator(c, MPM_OT_AutoWireframeEnable.bl_idname, depress=context.scene.mpm_prop.IsAutoEnableWireframeOnSculptMode)

    r = c.row(align=True)  # Brush, Stroke

    box = r.box()
    box.label(text="Tools & Brushes", icon="BRUSH_DATA")
    rr = box.row(align=True)
    cc = rr.column(align=True)
    cnt = 0
    tool = context.tool_settings.sculpt
    current_brush = tool.brush
    limit_rows = _AddonPreferences.Accessor.get_sculpt_limit_row_count()
    filter_names = _AddonPreferences.Accessor.get_sculpt_brush_filter_by_name().strip().split(",")
    # v4.2までブラシがアセットじゃない

    def _is_in_filter(brush):
        if len(filter_names) == 1 and filter_names[0] == "":
            return True
        for filter_name in filter_names:
            if filter_name.strip().lower() == brush.name.lower():
                return True
        return False
    if bpy.app.version < (4, 2, 9):
        tool_defs = []
        for item in ToolSelectPanelHelper._tools_flatten(VIEW3D_PT_tools_active.tools_from_context(context, context.mode)):
            if item and item.data_block:
                # print(dir(item))
                icon_value = ToolSelectPanelHelper._icon_value_from_icon_handle(item.icon)
                tool_defs.append((item.data_block, icon_value))
                # print(item.label, item.data_block, icon_value)
                # print(item)
                # row2.template_icon(icon_value=icon_value, scale=0.5)

        for i in bpy.data.brushes:
            if i.use_paint_sculpt and _is_in_filter(i):
                rrr = cc.row(align=False)
                icon_value = 0
                for t in tool_defs:
                    if t[0] == i.sculpt_tool:
                        rrr.template_icon(icon_value=t[1], scale=1)
                        icon_value = t[1]
                _Util.MPM_OT_SetPointer.operator(rrr, i.name, tool, "brush", i, depress=current_brush == i)
                # _Util.MPM_OT_SetPointer.operator(rr, i.name, tool, "brush", i, depress=current_brush == i, icon_value=icon_value)
                cnt += 1
                if cnt % limit_rows == 0:
                    cc = rr.column(align=True)
    # v4.3以降はブラシがアセット
    # libraryデータをロードすると全部一括ロードされる。
    # with bpy.data.libraries.load(bpy.data.libraries[0].filepath, assets_only=True) as (data_from, data_to):
        # data_to.brushes = data_from.brushes
    # 逐一選択されたブラシをロードしたいけど、libraryをロードせずにブラシ名を取得する方法が分からない
    else:
        active_tool = context.workspace.tools.from_space_view3d_mode(mode=bpy.context.mode)

        def _callback_operator_select_brush(context, layout, brush_name):
            def _select_brush(context, lib_type, lib_id, asset_id):
                bpy.ops.brush.asset_activate(
                    asset_library_type=lib_type,
                    asset_library_identifier=lib_id,
                    relative_asset_identifier=asset_id)
            is_depress = active_tool.use_brushes and current_brush.name == brush_name
            _Util.MPM_OT_CallbackOperator.operator(layout, brush_name, "_MenuSculpt.select_brush." + brush_name,
                                                   _select_brush, (context, "ESSENTIALS", "", "brushes\\essentials_brushes-mesh_sculpt.blend\\Brush\\" + brush_name), depress=is_depress)

        def _callback_operator_select_tool(context, layout, label_name, tool_id):
            def _select_tool(context, tool_name):
                bpy.ops.wm.tool_set_by_id(name=tool_name)
            is_depress = not active_tool.use_brushes and active_tool.idname == tool_id
            _Util.MPM_OT_CallbackOperator.operator(layout, label_name, "_MenuSculpt.select_tool." + tool_id,
                                                   _select_tool, (context, tool_id), depress=is_depress)
        # Tools
        for i in TOOL_INFO:
            if i[0] == "-":
                box = rr.box()
                box.label(text=i[1:])
                ccc = box.column(align=False)
                continue
            if _is_in_filter(i):
                _callback_operator_select_tool(context, ccc, ' '.join(word.capitalize() for word in i[8:].split('_')), i)
        # Essential
        for i in BRUSH_INFO:
            if i[0] == "-":
                box = rr.box()
                box.label(text=i[1:])
                ccc = box.column(align=False)
                continue
            if _is_in_filter(i):
                _callback_operator_select_brush(context, ccc, i)
        # Custom
        box = rr.box()
        box.label(text="User")
        rrr = box.row(align=True)
        ccc = rrr.column(align=False)
        for i in bpy.data.brushes:
            if i.use_paint_sculpt and i.name not in BRUSH_INFO and _is_in_filter(i):
                rrrr = ccc.row(align=False)
                _Util.MPM_OT_SetPointer.operator(rrrr, i.name, tool, "brush", i, depress=current_brush == i)
                cnt += 1
                if cnt % limit_rows == 0:
                    ccc = rrr.column(align=True)

    # Strokes
    cnt = 0
    box = r.box()
    box.label(text="Stroke", icon="STROKE")
    rr = box.row(align=True)
    cc = rr.column(align=True)
    for i in _Util.enum_values(current_brush, "stroke_method"):
        if bpy.app.version < (4, 2, 9):
            is_use = current_brush.stroke_method == i
            _Util.MPM_OT_SetString.operator(cc, i, current_brush, "stroke_method", i, isActive=i != current_brush, depress=is_use)
        else:
            is_use = active_tool.use_brushes and current_brush.stroke_method == i
            _Util.MPM_OT_SetString.operator(cc, i, current_brush, "stroke_method", i, isActive=active_tool.use_brushes, depress=is_use)
        cnt += 1
        if cnt % limit_rows == 0:
            cc = rr.column(align=True)
    # その他のブラシプロパティ

    # bpy.data.brushes["A_Folds_Brush_16b"].use_automasking_face_sets = False

    # Smoothブラシの強さ
    rr = c.row()
    smooth_brush = None
    if bpy.app.version < (4, 2, 9):
        for brush in bpy.data.brushes:
            if brush.use_paint_sculpt and brush.name.lower() == "smooth":
                smooth_brush = brush
                break
    else:
        blender_install_dir = os.path.dirname(bpy.app.binary_path)
        smooth_brush = bpy.data.brushes["Smooth", blender_install_dir + "\\4.3\\datafiles\\assets\\brushes\\essentials_brushes-mesh_sculpt.blend"]
    if smooth_brush:
        c = rr.column(align=True)
        r = c.row(align=True)
        if bpy.app.version < (4, 2, 9):
            r.label(icon="BRUSH_BLUR")
            _Util.layout_prop(r, smooth_brush, "strength", "Smooth Brush: Strength", icon="BRUSH_BLUR")
        else:
            _Util.layout_prop(r, smooth_brush, "strength", "Smooth Brush: Strength")
        r = r.row(align=True)
        r.scale_x = 0.8
        _Util.MPM_OT_SetSingle.operator(r, "50%", smooth_brush, "strength", max(0, smooth_brush.strength * 0.5))
        _Util.MPM_OT_SetSingle.operator(r, "75%", smooth_brush, "strength", max(0, smooth_brush.strength * 0.75))
        _Util.MPM_OT_SetSingle.operator(r, "150%", smooth_brush, "strength", min(1, smooth_brush.strength * 1.5))
        _Util.MPM_OT_SetSingle.operator(r, "200%", smooth_brush, "strength", min(1, smooth_brush.strength * 2))

    # Applyメニュー
    box = c.box()
    box.label(text="Apply", icon="CHECKMARK")
    # mask
    c = box.column(align=True)
    r = c.row(align=True)
    r.label(text=MPM_OT_MakeMaskWithSelectedVert.bl_label)
    _Util.layout_operator(r, MPM_OT_MakeMaskWithSelectedVert.bl_idname, "Selected").is_invert = True
    _Util.layout_operator(r, MPM_OT_MakeMaskWithSelectedVert.bl_idname, "Unselected").is_invert = False
    op = _Util.layout_operator(r, "paint.mask_flood_fill", "Clear")
    op.mode = "VALUE"
    op.value = 0
    # face set
    r = c.row(align=True)
    r.label(text=MPM_OT_MakeFaceSetWithSelectedVert.bl_label)
    _Util.layout_operator(r, MPM_OT_MakeFaceSetWithSelectedVert.bl_idname, "Selected").mode = "Selected"
    _Util.layout_operator(r, MPM_OT_MakeFaceSetWithSelectedVert.bl_idname, "Unselected").mode = "Unselected"
    _Util.layout_operator(r, MPM_OT_MakeFaceSetWithSelectedVert.bl_idname, "Clear").mode = "Clear"
# --------------------------------------------------------------------------------


class MPM_OT_MakeFaceSetWithSelectedVert(bpy.types.Operator):
    bl_idname = "mpm.make_faceset_with_selected_vert"
    bl_label = "Fill faceset with selected verts"
    bl_options = {"REGISTER", "UNDO"}
    mode: bpy.props.StringProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return any(v.select for v in context.object.data.vertices)

    def execute(self, context):
        data = context.object.data
        # クリア
        attr_data = data.attributes[".sculpt_face_set"].data
        for i in range(0, len(attr_data)):
            attr_data[i].value = 1
        if self.mode == "Selected":
            bpy.ops.sculpt.face_sets_create(mode="SELECTION")
        elif self.mode == "Unselected":
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="INVERT")
            bpy.ops.object.mode_set(mode="SCULPT")
            bpy.ops.sculpt.face_sets_create(mode="SELECTION")
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="INVERT")
            bpy.ops.object.mode_set(mode="SCULPT")
        return {"FINISHED"}


class MPM_OT_MakeMaskWithSelectedVert(bpy.types.Operator):
    bl_idname = "mpm.make_mask_with_selected_vert"
    bl_label = "Fill mask with selected verts"
    bl_options = {"REGISTER", "UNDO"}
    is_overwrite: bpy.props.BoolProperty(name="Overwrite", options={"HIDDEN"})
    is_invert: bpy.props.BoolProperty(name="Invert", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return any(v.select for v in context.object.data.vertices)

    def execute(self, context):
        data = context.object.data
        # クリア
        if not self.is_overwrite:
            bpy.ops.paint.mask_flood_fill(mode="VALUE", value=0)

        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(data)
        selected_verts = [v.index for v in bm.verts if v.select]
        if len(selected_verts) == 0:
            _Util.show_report_error(self, "Please select at least one vertex.")
            return {"CANCELLED"}

        mask_layer = bm.verts.layers.float.get(".sculpt_mask", None)
        if mask_layer is None:
            mask_layer = bm.verts.layers.float.new(".sculpt_mask")
        for v in bm.verts:
            if not self.is_invert and v.select:
                v[mask_layer] = 1.0
            elif self.is_invert and not v.select:
                v[mask_layer] = 1.0
        bmesh.update_edit_mesh(data)
        bpy.ops.object.mode_set(mode="SCULPT")
        return {"FINISHED"}


class MPM_OT_AutoWireframeEnable(bpy.types.Operator):
    bl_idname = "mpm.auto_wireframe_enable"
    bl_label = "Auto Show Wireframe"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from ._PieMenu import mode_change_handler
        context.scene.mpm_prop.IsAutoEnableWireframeOnSculptMode = not context.scene.mpm_prop.IsAutoEnableWireframeOnSculptMode
        context.active_object.show_wire = context.scene.mpm_prop.IsAutoEnableWireframeOnSculptMode
        indices = []
        for i, e in enumerate(bpy.app.handlers.depsgraph_update_pre):
            if e.__name__ == mode_change_handler.__name__:
                # print("atta", i)
                indices.append(i)
        for i in reversed(indices):
            # print("del", i)
            del bpy.app.handlers.depsgraph_update_pre[i]
        if context.scene.mpm_prop.IsAutoEnableWireframeOnSculptMode:
            bpy.app.handlers.depsgraph_update_pre.append(mode_change_handler)
        return {"FINISHED"}
# --------------------------------------------------------------------------------


classes = (
    MPM_OT_MakeMaskWithSelectedVert,
    MPM_OT_MakeFaceSetWithSelectedVert,
    MPM_OT_AutoWireframeEnable,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)


BRUSH_INFO = [
    "-Add & Subtract",
    "Blob",
    "Clay Strips",
    "Clay Thumb",
    "Crease Polish",
    "Crease Sharp",
    "Draw",
    "Draw Sharp",
    "Inflate/Deflate",
    "Layer",
    "-Contrast",
    "Fill/Deepen",
    "Flatten/Contrast",
    "Plateau",
    "Scrape Multiplane",
    "Scrape/Fill",
    "Smooth",
    "Trim",
    "-Transform",
    "Boundary",
    "Elastic Grab",
    "Elastic Snake Hook",
    "Grab",
    "Grab 2D",
    "Grab Silhouette",
    "Nudge",
    "Pinch/Magnify",
    "Pose",
    "Pull",
    "Relax Pinch",
    "Relax Slide",
    "Snake Hook",
    "Thumb",
    "Twist",
    "-Utilities",
    "Density",
    "Erase Multires Displacement",
    "Face Set Paint",
    "Mask",
    "Smear Multires Displacement",
    "-Paint",
    "Airbrush",
    "Blend Hard",
    "Blend Soft",
    "Blend Square",
    "Paint Blend",
    "Paint Hard",
    "Paint Hard Pressure",
    "Paint Soft",
    "Paint Soft Pressure",
    "Paint Square",
    "Sharpen",
    "Smear",
    "-Simulation",
    "Bend Boundary Cloth",
    "Bend/Twist Cloth",
    "Drag Cloth",
    "Expand/Contract Cloth",
    "Grab Cloth",
    "Grab Planar Cloth ",
    "Grab Random Cloth",
    "Inflate Cloth",
    "Pinch Folds Cloth",
    "Pinch Point Cloth",
    "Push Cloth",
    "Stretch/Move Cloth",
    "Twist Boundary Cloth",
]
TOOL_INFO = [
    "-Tools",
    "builtin.box_mask",
    "builtin.box_hide",
    "builtin.box_trim",
    "builtin.line_project",
    "builtin.mesh_filter",
    "builtin.cloth_filter",
    "builtin.color_filter",
    "builtin.face_set_edit",
    "builtin.mask_by_color",
    "builtin.move",
    "builtin.rotate",
    "builtin.scale",
    "builtin.trasform",
    "builtin.annotate",
]
