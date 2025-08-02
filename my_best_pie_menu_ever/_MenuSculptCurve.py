if "bpy" in locals():
    import importlib
    for m in (
        _Util,
    ):
        importlib.reload(m)
else:
    import bpy
    from . import (
        _Util,
    )
# --------------------------------------------------------------------------------
# カーブスカルプトモードメニュー
# 'use_paint_antialiasing', 'use_paint_grease_pencil', 'use_paint_image', 'use_paint_sculpt', 'use_paint_sculpt_curves', 'use_paint_uv_sculpt', 'use_paint_vertex', 'use_paint_weight'
# --------------------------------------------------------------------------------


def draw(pie, context):
    box = pie.split().box()
    box.label(text='Sculpt Curves Primary')

    rowinbox = box.row()
    col2 = rowinbox.column()
    col2.label(text="Brushes")
    cnt = 0
    tool = context.tool_settings.curves_sculpt
    current_brush = tool.brush
    for i in bpy.data.brushes:
        if i.use_paint_sculpt_curves:
            is_use = current_brush.name == i.name
            op = _Util.MPM_OT_SetPointer.operator(col2, i.name.replace(" Curves", ""), tool, "brush", i)
            cnt += 1
            if cnt == 10:
                col2 = rowinbox.column()
    # col2 = row.box().column()
    # col2.label(text = "Stroke")
    # for i in _Util.enum_values(current_brush, 'stroke_method'):
    #     is_use = OT_TexturePaint_StrokeMethod.getCurrent() == i
    #     col2.operator(OT_TexturePaint_StrokeMethod.bl_idname, text=i, depress = is_use).methodName = i
# --------------------------------------------------------------------------------


def MenuSecondary(pie, context):
    box = pie.split().box()
    box.label(text='Sculpt Curves Secondary')
    pass

# --------------------------------------------------------------------------------


classes = (
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
