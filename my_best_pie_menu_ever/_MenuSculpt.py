import bpy
from . import _Util
from . import _AddonPreferences
import bmesh
# --------------------------------------------------------------------------------
# スカルプトモードメニュー
# 'use_paint_antialiasing', 'use_paint_grease_pencil', 'use_paint_image', 'use_paint_sculpt', 'use_paint_sculpt_curves', 'use_paint_uv_sculpt', 'use_paint_vertex', 'use_paint_weight'
# --------------------------------------------------------------------------------


def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text="Sculpt Primary")

    c = box.column()
    _Util.layout_operator(c, MPM_OT_AutoWireframeEnable.bl_idname, depress=context.scene.mpm_prop.IsAutoEnableWireframeOnSculptMode)

    row = c.row(align=True)  # Brush, Stroke

    box = row.box()
    box.label(text="Brush", icon="BRUSH_DATA")
    row2 = box.row(align=True)
    col2 = row2.column(align=True)
    cnt = 0
    tool = context.tool_settings.sculpt
    current_brush = tool.brush
    limit_rows = _AddonPreferences.Accessor.get_sculpt_limit_row_count()
    filters = _AddonPreferences.Accessor.get_sculpt_brush_filter_by_name().strip()
    if filters:
        for filter_name in filters.split(","):
            for brush_data in bpy.data.brushes:
                if brush_data.use_paint_sculpt and filter_name.strip().lower() == brush_data.name.lower():
                    op = _Util.MPM_OT_SetPointer.operator(col2, brush_data.name, tool, "brush", brush_data, depress=current_brush == brush_data)
                    cnt += 1
                    if cnt % limit_rows == 0:
                        col2 = row2.column(align=True)
    else:
        for i in bpy.data.brushes:
            if i.use_paint_sculpt:
                op = _Util.MPM_OT_SetPointer.operator(col2, i.name, tool, "brush", i, depress=current_brush == i)
                cnt += 1
                if cnt % limit_rows == 0:
                    col2 = row2.column(align=True)
    # Strokes
    cnt = 0
    box = row.box()
    box.label(text="Stroke", icon="STROKE")
    row2 = box.row(align=True)
    col2 = row2.column(align=True)
    for i in _Util.enum_values(tool.brush, "stroke_method"):
        is_use = tool.brush.stroke_method == i
        _Util.MPM_OT_SetString.operator(col2, i, tool.brush, "stroke_method", i, depress=is_use)
        cnt += 1
        if cnt % limit_rows == 0:
            col2 = row2.column(align=True)

    # Smoothブラシの強さ
    rr = c.row()
    smooth_brush = None
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
        _Util.MPM_OT_SetSingle.operator(r, "50%", brush, "strength", max(0, brush.strength * 0.5))
        _Util.MPM_OT_SetSingle.operator(r, "75%", brush, "strength", max(0, brush.strength * 0.75))
        _Util.MPM_OT_SetSingle.operator(r, "150%", brush, "strength", min(1, brush.strength * 1.5))
        _Util.MPM_OT_SetSingle.operator(r, "200%", brush, "strength", min(1, brush.strength * 2))

    # Applyメニュー
    box = c.box()
    box.label(text="Apply", icon="MODIFIER")
    # mask
    c = box.column(align=True)
    r = c.row(align=True)
    r.label(text=MPM_OT_MakeMaskWithSelectedVert.bl_label)
    _Util.layout_operator(r, MPM_OT_MakeMaskWithSelectedVert.bl_idname, "Selected").is_invert = True
    _Util.layout_operator(r, MPM_OT_MakeMaskWithSelectedVert.bl_idname, "Unselected").is_invert = False
    op = _Util.layout_operator(r, "paint.mask_flood_fill", "Clear")
    op.mode = "VALUE"
    op.value = 0
# --------------------------------------------------------------------------------


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
        for i,e in enumerate(bpy.app.handlers.depsgraph_update_pre):
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
    MPM_OT_AutoWireframeEnable,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
