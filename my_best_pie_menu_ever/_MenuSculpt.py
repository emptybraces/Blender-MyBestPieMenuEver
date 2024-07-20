import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util
from . import _AddonPreferences
# --------------------------------------------------------------------------------
# スカルプトモードメニュー
# 'use_paint_antialiasing', 'use_paint_grease_pencil', 'use_paint_image', 'use_paint_sculpt', 'use_paint_sculpt_curves', 'use_paint_uv_sculpt', 'use_paint_vertex', 'use_paint_weight'
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Sculpt Primary')

    c = box.column()

    row = c.row(align=True) # Brush, Stroke

    box = row.box()
    box.label(text = "Brush")
    row2 = box.row(align=True)
    col2 = row2.column(align=True)
    cnt = 0
    tool = context.tool_settings.sculpt
    current_brush = tool.brush
    limit_rows = _AddonPreferences.Accessor.get_sculpt_limit_row_count()
    filters = _AddonPreferences.Accessor.get_sculpt_brush_filter_by_name().strip()
    if filters:
        for filter_name in filters.split(','):
            for brush_data in bpy.data.brushes:
                if brush_data.use_paint_sculpt and filter_name.strip().lower() == brush_data.name.lower():
                    op = _Util.MPM_OT_SetPointer.operator(col2, brush_data.name, tool, "brush", brush_data, depress=current_brush == brush_data)
                    cnt += 1
                    if cnt % limit_rows == 0: col2 = row2.column(align=True)
    else:
        for i in bpy.data.brushes:
            if i.use_paint_sculpt:
                op = _Util.MPM_OT_SetPointer.operator(col2, i.name, tool, "brush", i, depress=current_brush == i)
                cnt += 1;
                if cnt % limit_rows == 0: col2 = row2.column(align=True)
    # Strokes
    cnt = 0
    box = row.box()
    box.label(text = "Stroke")
    row2 = box.row(align=True)
    col2 = row2.column(align=True)
    for i in _Util.enum_values(tool.brush, 'stroke_method'):
        is_use = tool.brush.stroke_method == i
        _Util.MPM_OT_SetString.operator(col2, i, tool.brush, "stroke_method", i, depress=is_use)
        cnt += 1
        if cnt % limit_rows == 0: col2 = row2.column(align=True)

    # Smoothブラシの強さ
    smooth_brush = None
    for brush in bpy.data.brushes:
        if brush.use_paint_sculpt and brush.name.lower() == "smooth":
            smooth_brush = brush
            break
    if smooth_brush:
        r = c.row(align=False)
        _Util.layout_prop(r, smooth_brush, "strength", "Smooth Brush: Strength")
        r = r.row(align=True)
        r.scale_x = 0.8
        _Util.MPM_OT_SetSingle.operator(r, "50%", brush, "strength", max(0, brush.strength * 0.5))
        _Util.MPM_OT_SetSingle.operator(r, "75%", brush, "strength", max(0, brush.strength * 0.75))
        _Util.MPM_OT_SetSingle.operator(r, "150%", brush, "strength", min(1, brush.strength * 1.5))
        _Util.MPM_OT_SetSingle.operator(r, "200%", brush, "strength", min(1, brush.strength * 2))
# --------------------------------------------------------------------------------

classes = (
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)