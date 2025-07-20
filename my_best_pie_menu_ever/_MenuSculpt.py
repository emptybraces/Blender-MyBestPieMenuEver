import os
import time
import bpy
import importlib
import bmesh
from bpy.app.translations import pgettext_iface as iface_
from . import (
    g,
    _Util,
    _AddonPreferences,
)
for m in (
    g,
    _Util,
    _AddonPreferences,
):
    importlib.reload(m)

# --------------------------------------------------------------------------------
# スカルプトモードメニュー
# --------------------------------------------------------------------------------
g_is_filter_mode = False
g_is_filter_set_mode_enter = False
g_filter_mode_enter_lasttime = 0


def draw(pie, context):
    # フィルターモード
    global g_is_filter_mode, g_is_filter_set_mode_enter, g_filter_mode_enter_lasttime
    g_is_filter_set_mode_enter = g_is_filter_set_mode_enter and (time.time() - g_filter_mode_enter_lasttime) < 0.1
    g.on_closed.pop("warn_open_filter_set_sculpt", None)

    box = pie.split().box()
    box.label(text="Sculpt Brush Filter Setting Mode" if g_is_filter_set_mode_enter else "Sculpt Primary")
    c = box.column(align=True)
    # 上部メニュー
    layout_start_upper = c.row(align=True)
    layout_start_upper.alignment = "RIGHT"
    layout_start_upper.scale_x = 1.1
    # ブラシメニュー
    r = c.row(align=True)
    layout_start_brush = r.row(align=True)
    box = layout_start_brush.box()
    box.label(text="Tools & Brushes(Filtered)" if g_is_filter_mode else "Tools & Brushes", icon="BRUSH_DATA")
    layout_start_brush_list = box.row(align=True)
    # ブラシストローク
    layout_start_brush_stroke = r.box()
    # スムーズブラシ
    layout_start_smooth_brush = c.row(align=True)
    # ユーティリティ
    r = c.row()
    box = r.box()
    box.label(text="Utility")
    layout_start_utility = box.column(align=True)
    # 適用メニュー
    box = r.box()
    box.label(text="Apply", icon="CHECKMARK")
    layout_start_apply = box.column(align=True)

    def __switch_filter_mode():
        global g_is_filter_mode
        g_is_filter_mode = not g_is_filter_mode

    def __switch_filter_setting_mode():
        global g_is_filter_set_mode_enter, g_filter_mode_enter_lasttime
        g_is_filter_set_mode_enter = not g_is_filter_set_mode_enter
        g_filter_mode_enter_lasttime = time.time()
        if g_is_filter_set_mode_enter:  # モードに入るときだけ警告を表示
            g.on_closed["warn_open_filter_set_sculpt"] = lambda: _Util.show_msgbox("Please hold down the shift key to click.", "Error", "ERROR")
    if not g_is_filter_set_mode_enter:
        _Util.MPM_OT_CallbackOperator.operator(layout_start_upper, "Disable Filter Mode" if g_is_filter_mode else "Enable Filter Mode", __name__ + ".g_is_filter_mode",
                                               __switch_filter_mode, None, "FILTER", depress=g_is_filter_mode)
    _Util.MPM_OT_CallbackOperator.operator(layout_start_upper, "Exit Filter Setting" if g_is_filter_set_mode_enter else "Enter Filter Setting", __name__ + ".g_is_filter_mode_enter",
                                           __switch_filter_setting_mode, None, "TOOL_SETTINGS",  depress=g_is_filter_set_mode_enter)
    # ブラシ
    cnt = 0
    tool = context.tool_settings.sculpt
    current_brush = tool.brush
    pref = _AddonPreferences.get_data()
    filter_names = pref.sculptBrushFilterByName.strip().split(",")
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
        _Util.MPM_OT_CallbackOperator.operator(layout, iface_(brush_name), "_MenuSculpt.select_brush." + brush_name,
                                               _select_brush, (context, "ESSENTIALS", "", os.path.join("brushes", "essentials_brushes-mesh_sculpt.blend", "Brush", brush_name)), depress=is_depress)

    def _callback_operator_select_tool(context, layout, label_name, tool_id):
        def _select_tool(context, tool_name):
            bpy.ops.wm.tool_set_by_id(name=tool_name)
        is_depress = not active_tool.use_brushes and active_tool.idname == tool_id
        _Util.MPM_OT_CallbackOperator.operator(layout, iface_(label_name), "_MenuSculpt.select_tool." + tool_id,
                                               _select_tool, (context, tool_id), depress=is_depress)

    def _brush_filter_operator(context, layout, label_name, tool_id, in_filter):
        def _set(context, tool_id, in_filter):
            filter = _AddonPreferences.get_data().sculptBrushFilterByName
            tool_id = tool_id.lower()
            if in_filter:
                filter = filter.replace(tool_id, "")
            else:
                filter += "," + tool_id
            _AddonPreferences.get_data().sculptBrushFilterByName = ",".join(s.strip() for s in filter.split(",") if 0 < len(s.strip()))
            global g_filter_mode_enter_lasttime
            g_filter_mode_enter_lasttime = time.time()
        _Util.MPM_OT_CallbackOperator.operator(layout, label_name, __name__ + ".set_brush_filter." + tool_id,
                                               _set, (context, tool_id, in_filter), depress=in_filter)
    # Tools
    rr = layout_start_brush_list
    if g_is_filter_set_mode_enter or not g_is_filter_mode:
        for i in TOOL_INFO:
            if i[0] == "-":
                cc = rr.box().column(align=True)
                cc.label(text=i[1:])
                continue
            if g_is_filter_set_mode_enter:
                _brush_filter_operator(context, cc, ' '.join(word.capitalize() for word in i[8:].split('_')), i, _is_in_filter(i))
            else:
                _callback_operator_select_tool(context, cc, ' '.join(word.capitalize() for word in i[8:].split('_')), i)
    # フィルターモード
    else:
        cnt = 0
        cc = rr.column(align=True)
        for i in TOOL_INFO:
            if not _is_in_filter(i):
                continue  # 表示しない
            _callback_operator_select_tool(context, cc, ' '.join(word.capitalize() for word in i[8:].split('_')), i)
            if (cnt := cnt+1) % pref.sculptLimitRowCount == 0:
                cc = rr.column(align=True)
    # Essential
    if g_is_filter_set_mode_enter or not g_is_filter_mode:
        for i in BRUSH_INFO:
            if i[0] == "-":
                if "Utilities" not in i:
                    box = rr.box()
                cc = box.column(align=True)
                cc.label(text=i[1:])
                continue
            if g_is_filter_set_mode_enter:
                _brush_filter_operator(context, cc, i, i, _is_in_filter(i))
            else:
                _callback_operator_select_brush(context, cc, i)
    # フィルターモード
    else:
        cnt = 0
        cc = rr.column(align=True)
        for i in BRUSH_INFO:
            if not _is_in_filter(i):
                continue  # 表示しない
            _callback_operator_select_brush(context, cc, i)
            if (cnt := cnt+1) % pref.sculptLimitRowCount == 0:
                cc = rr.column(align=True)
    # Local/Custom
    # 任意のブラシのcontext.tool_settings.image_paint.brush_asset_referenceにアクセスする術がないため不可能
    # if g_is_filter_set_mode_enter or not g_is_filter_mode:
    #     box = rr.box()
    #     box.label(text="User")
    #     rrr = box.row(align=True)
    #     cc = rrr.column(align=False)
    #     for i in [i for i in bpy.data.brushes if i.use_paint_sculpt and i.name not in BRUSH_INFO]:
    #         if g_is_filter_set_mode_enter:
    #             _brush_filter_operator(context, cc, i.name, i.name, _is_in_filter(i.name))
    #         else:
    #             _Util.MPM_OT_SetPointer.operator(cc, i.name, tool, "brush", i, depress=current_brush == i)
    #         if (cnt := cnt+1) % pref.sculptLimitRowCount == 0:
    #             cc = rrr.column(align=True)
    # # フィルターモード
    # else:
    #     for i in [i for i in bpy.data.brushes if i.use_paint_sculpt and i.name not in BRUSH_INFO]:
    #         if not _is_in_filter(i.name):
    #             continue  # 表示しない
    #         _Util.MPM_OT_SetPointer.operator(cc, i.name, tool, "brush", i, depress=current_brush == i)
    #         if (cnt := cnt+1) % pref.sculptLimitRowCount == 0:
    #             cc = rrr.column(align=True)

    if g_is_filter_set_mode_enter:
        return
    # Strokes
    cnt = 0
    layout_start_brush_stroke.label(text="Stroke", icon="STROKE")
    rr = layout_start_brush_stroke.row(align=True)
    cc = rr.column(align=True)
    for i in _Util.enum_identifier(current_brush, "stroke_method"):
        is_use = active_tool.use_brushes and current_brush.stroke_method == i
        _Util.MPM_OT_SetString.operator(cc, i, current_brush, "stroke_method", i, isActive=active_tool.use_brushes, depress=is_use)
        if (cnt := cnt+1) % pref.sculptLimitRowCount == 0:
            cc = rr.column(align=True)

    # Smoothブラシの強さ
    unified_paint_settings = context.tool_settings.unified_paint_settings
    smooth_brush = bpy.data.brushes.get("Smooth")
    if smooth_brush == None:
        path = os.path.join(bpy.utils.system_resource("DATAFILES"), "assets", "brushes", "essentials_brushes-mesh_sculpt.blend")
        with bpy.data.libraries.load(path, link=True, assets_only=True) as (data_from, data_to):
            for i in data_from.brushes:
                if i == "Smooth":
                    data_to.brushes = [i]  # これでひとつだけロードしたことになる
                    break
        smooth_brush = bpy.data.brushes.get("Smooth")
    if smooth_brush != None:
        r = layout_start_smooth_brush
        r.enabled = not unified_paint_settings.use_unified_strength
        r.alignment = "LEFT"
        _Util.layout_prop(r, smooth_brush, "strength", "Smooth Strength")
        _Util.MPM_OT_SetSingle.operator(r, "50%", smooth_brush, "strength", max(0, smooth_brush.strength * 0.5))
        _Util.MPM_OT_SetSingle.operator(r, "75%", smooth_brush, "strength", max(0, smooth_brush.strength * 0.75))
        _Util.MPM_OT_SetSingle.operator(r, "150%", smooth_brush, "strength", min(1, smooth_brush.strength * 1.5))
        _Util.MPM_OT_SetSingle.operator(r, "200%", smooth_brush, "strength", min(1, smooth_brush.strength * 2))
    # Utilityメニュー
    r = layout_start_utility.row()
    r.alignment = "LEFT"
    # 共通のサイズ、強度
    _Util.layout_prop(r, unified_paint_settings, "use_unified_size")
    _Util.layout_prop(r, unified_paint_settings, "use_unified_strength")
    # オートワイヤーフレーム
    _Util.layout_operator(r, MPM_OT_Sculpt_AutoWireframeEnable.bl_idname, depress=context.scene.mpm_prop.IsAutoEnableWireframeOnSculptMode)

    # Applyメニュー
    # mask
    r = layout_start_apply.row(align=True)
    r.label(text=MPM_OT_Sculpt_MakeMaskWithSelectedVert.bl_label)
    _Util.layout_operator(r, MPM_OT_Sculpt_MakeMaskWithSelectedVert.bl_idname, "Selection").is_invert = True
    _Util.layout_operator(r, MPM_OT_Sculpt_MakeMaskWithSelectedVert.bl_idname, "Invert").is_invert = False
    op = _Util.layout_operator(r, "paint.mask_flood_fill", "Clear")
    op.mode = "VALUE"
    op.value = 0
    # face set
    r = layout_start_apply.row(align=True)
    r.label(text=MPM_OT_Sculpt_MakeFaceSetWithSelectedVert.bl_label)
    _Util.layout_operator(r, MPM_OT_Sculpt_MakeFaceSetWithSelectedVert.bl_idname, "Selection").mode = "Selected"
    _Util.layout_operator(r, MPM_OT_Sculpt_MakeFaceSetWithSelectedVert.bl_idname, "Invert").mode = "Unselected"
    _Util.layout_operator(r, MPM_OT_Sculpt_MakeFaceSetWithSelectedVert.bl_idname, "Clear").mode = "Clear"

# --------------------------------------------------------------------------------


class MPM_OT_Sculpt_MakeFaceSetWithSelectedVert(bpy.types.Operator):
    bl_idname = "mpm.sculpt_make_faceset_with_selected_vert"
    bl_label = "Faceset with selected verts"
    bl_options = {"REGISTER", "UNDO"}
    mode: bpy.props.StringProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return any(v.select for v in context.object.data.vertices)

    def execute(self, context):
        data = context.object.data
        # 最初にクリア
        bm = bmesh.new()
        bm.from_mesh(data)
        layer = bm.faces.layers.int.get('.sculpt_face_set')
        for i in bm.faces:
            i[layer] = 1
        bm.to_mesh(data)
        bm.free()
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


class MPM_OT_Sculpt_MakeMaskWithSelectedVert(bpy.types.Operator):
    bl_idname = "mpm.sculpt_make_mask_with_selected_vert"
    bl_label = "Mask with selected verts"
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


class MPM_OT_Sculpt_AutoWireframeEnable(bpy.types.Operator):
    bl_idname = "mpm.sculpt_auto_wireframe_enable"
    bl_label = "Auto Enable Wireframe"
    bl_description = "Automatically enables Wireframe display when entering Sculpt mode"
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
    MPM_OT_Sculpt_MakeMaskWithSelectedVert,
    MPM_OT_Sculpt_MakeFaceSetWithSelectedVert,
    MPM_OT_Sculpt_AutoWireframeEnable,
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
    "-Utilities",
    "Density",
    "Erase Multires Displacement",
    "Face Set Paint",
    "Mask",
    "Smear Multires Displacement",
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
