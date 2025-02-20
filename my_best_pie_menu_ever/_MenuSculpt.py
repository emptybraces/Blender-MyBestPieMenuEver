if "bpy" in locals():
    import importlib
    importlib.reload(_Util)
    importlib.reload(_AddonPreferences)
    importlib.reload(g)
else:
    from . import _Util
    from . import _AddonPreferences
    from . import g
import os
import time
import bpy
import bmesh
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
# --------------------------------------------------------------------------------
# スカルプトモードメニュー
# --------------------------------------------------------------------------------
g_is_filter_mode = False
g_is_filter_set_mode_enter = False
g_filter_mode_enter_lasttime = 0


def MenuPrimary(pie, context):
    if not g.is_v4_3_later():
        return MenuPrimary_v4_2(pie, context)
    # フィルターモード
    global g_is_filter_mode, g_is_filter_set_mode_enter, g_filter_mode_enter_lasttime
    g_is_filter_set_mode_enter = g_is_filter_set_mode_enter and (time.time() - g_filter_mode_enter_lasttime) < 0.1
    g.on_closed.pop("warn_open_filter_set_sculpt", None)

    box = pie.split().box()
    box.label(text="Sculpt Brush Filter Setting Mode" if g_is_filter_set_mode_enter else "Sculpt Primary")

    # 上部メニュー
    c = box.column(align=True)
    if not g_is_filter_set_mode_enter:
        _Util.layout_operator(c, MPM_OT_AutoWireframeEnable.bl_idname, depress=context.scene.mpm_prop.IsAutoEnableWireframeOnSculptMode)

    def __switch_filter_mode():
        global g_is_filter_mode
        g_is_filter_mode = not g_is_filter_mode

    def __switch_filter_setting_mode():
        global g_is_filter_set_mode_enter, g_filter_mode_enter_lasttime
        g_is_filter_set_mode_enter = not g_is_filter_set_mode_enter
        g_filter_mode_enter_lasttime = time.time()
        if g_is_filter_set_mode_enter:  # モードに入るときだけ警告を表示
            g.on_closed["warn_open_filter_set_sculpt"] = lambda: _Util.show_msgbox("Please hold down the shift key to click.", "Error", "ERROR")
    r = c.row(align=True)
    r.alignment = "RIGHT"
    _Util.MPM_OT_CallbackOperator.operator(r, "Disable Filter Mode" if g_is_filter_mode else "Enable Filter Mode", __name__ + ".g_is_filter_mode",
                                           __switch_filter_mode, None, "FILTER", depress=g_is_filter_mode)
    _Util.MPM_OT_CallbackOperator.operator(r, "Exit Filter Setting" if g_is_filter_set_mode_enter else "Enter Filter Setting", __name__ + ".g_is_filter_mode_enter",
                                           __switch_filter_setting_mode, None, "TOOL_SETTINGS",  depress=g_is_filter_set_mode_enter)
    # ブラシ
    cnt = 0
    tool = context.tool_settings.sculpt
    current_brush = tool.brush
    limit_rows = _AddonPreferences.Accessor.get_sculpt_limit_row_count()
    filter_names = _AddonPreferences.Accessor.get_sculpt_brush_filter_by_name().strip().split(",")
    r = c.row(align=True)
    box = r.box()
    box.label(text="Tools & Brushes(Filtered)" if g_is_filter_mode else "Tools & Brushes", icon="BRUSH_DATA")
    rr = box.row(align=True)
    rr.scale_x = 0.9
    cc = rr.column(align=True)
    # v4.3以降はブラシがアセット
    # libraryデータをロードすると全部一括ロードされる。
    # with bpy.data.libraries.load(bpy.data.libraries[0].filepath, assets_only=True) as (data_from, data_to):
    # data_to.brushes = data_from.brushes
    # 逐一選択されたブラシをロードしたいけど、libraryをロードせずにブラシ名を取得する方法が分からない
    active_tool = context.workspace.tools.from_space_view3d_mode(mode=bpy.context.mode)

    def _is_in_filter(id):
        for filter_name in filter_names:
            if filter_name.strip().lower() == id.lower():
                return True
        return False

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

    def _filter_operator(context, layout, label_name, tool_id):
        def _set(context, tool_id):
            filter = _AddonPreferences.Accessor.get_sculpt_brush_filter_by_name()
            tool_id = tool_id.lower()
            if _is_in_filter(tool_id):
                filter = filter.replace(tool_id, "")
            else:
                filter += "," + tool_id
            _AddonPreferences.Accessor.set_sculpt_brush_filter_by_name(",".join(s.strip() for s in filter.split(",") if 0 < len(s.strip())))
            global g_filter_mode_enter_lasttime
            g_filter_mode_enter_lasttime = time.time()
        _Util.MPM_OT_CallbackOperator.operator(layout, label_name, __name__ + ".set_filter." + tool_id,
                                               _set, (context, tool_id), depress=_is_in_filter(tool_id))
    # Tools
    for i in TOOL_INFO:
        if g_is_filter_set_mode_enter or not g_is_filter_mode:
            if i[0] == "-":
                box = rr.box()
                box.label(text=i[1:])
                cc = box.column(align=False)
                continue
            if g_is_filter_set_mode_enter:
                _filter_operator(context, cc, ' '.join(word.capitalize() for word in i[8:].split('_')), i)
            else:
                _callback_operator_select_tool(context, cc, ' '.join(word.capitalize() for word in i[8:].split('_')), i)
        # フィルターモード
        else:
            if not _is_in_filter(i):
                continue  # 表示しない
            _callback_operator_select_tool(context, cc, ' '.join(word.capitalize() for word in i[8:].split('_')), i)
            if (cnt := cnt+1) % limit_rows == 0:
                cc = rr.column(align=True)
    # Essential
    for i in BRUSH_INFO:
        if g_is_filter_set_mode_enter or not g_is_filter_mode:
            if i[0] == "-":
                box = rr.box()
                box.label(text=i[1:])
                cc = box.column(align=False)
                continue
            if g_is_filter_set_mode_enter:
                _filter_operator(context, cc, i, i)
            else:
                _callback_operator_select_brush(context, cc, i)
        # フィルターモード
        else:
            if not _is_in_filter(i):
                continue  # 表示しない
            _callback_operator_select_brush(context, cc, i)
            if (cnt := cnt+1) % limit_rows == 0:
                cc = rr.column(align=True)
    # Custom
    if g_is_filter_set_mode_enter or not g_is_filter_mode:
        box = rr.box()
        box.label(text="User")
        rrr = box.row(align=True)
        cc = rrr.column(align=False)
        for i in [i for i in bpy.data.brushes if i.use_paint_sculpt and i.name not in BRUSH_INFO]:
            if g_is_filter_set_mode_enter:
                _filter_operator(context, cc, i.name, i.name)
            else:
                _Util.MPM_OT_SetPointer.operator(cc, i.name, tool, "brush", i, depress=current_brush == i)
            if (cnt := cnt+1) % limit_rows == 0:
                cc = rrr.column(align=True)
    # フィルターモード
    else:
        for i in [i for i in bpy.data.brushes if i.use_paint_sculpt and i.name not in BRUSH_INFO]:
            if not _is_in_filter(i.name):
                continue  # 表示しない
            _Util.MPM_OT_SetPointer.operator(cc, i.name, tool, "brush", i, depress=current_brush == i)
            if (cnt := cnt+1) % limit_rows == 0:
                cc = rrr.column(align=True)

    if g_is_filter_set_mode_enter:
        return
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
        if (cnt := cnt+1) % limit_rows == 0:
            cc = rr.column(align=True)
    # その他のブラシプロパティ
    # Smoothブラシの強さ
    rr = c.row()
    if bpy.data.brushes.get("Smooth") == None:
        blender_install_dir = os.path.dirname(bpy.app.binary_path)
        with bpy.data.libraries.load(blender_install_dir + "\\4.3\\datafiles\\assets\\brushes\\essentials_brushes-mesh_sculpt.blend", link=True, assets_only=True) as (data_from, data_to):
            for i in data_from.brushes:
                if i == "Smooth":
                    data_to.brushes = [i]  # これでひとつだけロードしたことになる
                    break
    else:
        smooth_brush = bpy.data.brushes["Smooth"]
        c = rr.column(align=True)
        r = c.row(align=True)
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


def MenuPrimary_v4_2(pie, context):
    if not g.is_v4_3_later():
        return MenuPrimary_v4_2()
    box = pie.split().box()
    box.label(text="Sculpt Primary")

    c = box.column(align=True)
    _Util.layout_operator(c, MPM_OT_AutoWireframeEnable.bl_idname, depress=context.scene.mpm_prop.IsAutoEnableWireframeOnSculptMode)
    # ブラシ
    r = c.row(align=True)
    box = r.box()
    box.label(text="Tools & Brushes", icon="BRUSH_DATA")
    rr = box.row(align=True)
    rr.scale_x = 0.9
    cc = rr.column(align=True)
    cnt = 0
    tool = context.tool_settings.sculpt
    current_brush = tool.brush
    limit_rows = _AddonPreferences.Accessor.get_sculpt_limit_row_count()
    filter_names = _AddonPreferences.Accessor.get_sculpt_brush_filter_by_name().strip().split(",")

    def _is_in_filter(brush):
        if len(filter_names) == 1 and filter_names[0] == "":
            return True
        for filter_name in filter_names:
            if filter_name.strip().lower() == brush.name.lower():
                return True
        return False
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
            if (cnt := cnt+1) % limit_rows == 0:
                cc = rr.column(align=True)

    # Strokes
    cnt = 0
    box = r.box()
    box.label(text="Stroke", icon="STROKE")
    rr = box.row(align=True)
    cc = rr.column(align=True)
    for i in _Util.enum_values(current_brush, "stroke_method"):
        is_use = current_brush.stroke_method == i
        _Util.MPM_OT_SetString.operator(cc, i, current_brush, "stroke_method", i, isActive=i != current_brush, depress=is_use)
        if (cnt := cnt+1) % limit_rows == 0:
            cc = rr.column(align=True)
    # Smoothブラシの強さ
    rr = c.row()
    smooth_brush = None
    if smooth_brush == None:
        for brush in bpy.data.brushes:
            if brush.use_paint_sculpt and brush.name.lower() == "smooth":
                smooth_brush = brush
                break
    if smooth_brush:
        c = rr.column(align=True)
        r = c.row(align=True)
        r.label(icon="BRUSH_BLUR")
        _Util.layout_prop(r, smooth_brush, "strength", "Smooth Brush: Strength", icon="BRUSH_BLUR")
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
