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

    row = box.row(align=True) # Brush, Stroke, Blend...

    box = row.box()
    box.label(text = "Brush")
    row2 = box.row()
    col2 = row2.column()
    cnt = 0
    tool = context.tool_settings.sculpt
    current_brush = tool.brush
    limit_rows = _AddonPreferences.Accessor.get_sculpt_limit_row_count()
    filters = _AddonPreferences.Accessor.get_sculpt_brush_filter_by_name().strip()
    if filters:
        for filter_name in filters.split(','):
            for brush_data in bpy.data.brushes:
                if brush_data.use_paint_sculpt and filter_name.strip().lower() == brush_data.name.lower():
                    op = _Util.OT_SetPointer.operator(col2, brush_data.name, tool, "brush", brush_data, depress=current_brush == brush_data)
                    cnt += 1
                    if cnt % limit_rows == 0: col2 = row2.column()
    else:
        for i in bpy.data.brushes:
            if i.use_paint_sculpt:
                op = _Util.OT_SetPointer.operator(col2, i.name, tool, "brush", i, depress=current_brush == i)
                cnt += 1;
                if cnt % limit_rows == 0: col2 = row2.column()
    # Strokes
    cnt = 0
    box = row.box()
    box.label(text = "Stroke")
    row2 = box.row()
    col2 = row2.column()
    for i in _Util.enum_values(tool.brush, 'stroke_method'):
        is_use = tool.brush.stroke_method == i
        _Util.OT_SetString.operator(col2, i, tool.brush, "stroke_method", i, depress=is_use)
        cnt += 1;
        if cnt % limit_rows == 0: col2 = row2.column()
# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    box = pie.split().box()
    box.label(text = 'Sculpt Secondary')
    pass

# --------------------------------------------------------------------------------

classes = (
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)