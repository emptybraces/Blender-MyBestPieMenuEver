if "bpy" in locals():
    import importlib
    importlib.reload(_Util)
    importlib.reload(_AddonPreferences)
else:
    from . import _Util
    from . import _AddonPreferences
    
import bpy
import mathutils
from bl_ui.properties_paint_common import UnifiedPaintPanel, brush_basic_texpaint_settings
key_ctrl_lmb_erasealpha = None
key_ctrl_lmb_invert = None
key_keydown_ctrl = None
# --------------------------------------------------------------------------------
# テクスチャペイントメニュー
# --------------------------------------------------------------------------------


def MenuPrimary(pie, context):
    cnt = 0
    b = pie.split().box()
    b.label(text='TexturePaint Primary')

    # Brush, Stroke, Blend...
    r = b.row(align=True)
    bb = r.box()
    bb.label(text="Brush")
    limit_rows = _AddonPreferences.Accessor.get_image_paint_limit_row()
    brush_exclude_list = [item.strip() for item in _AddonPreferences.Accessor.get_image_paint_brush_exclude().lower().split(',')]
    tool = context.tool_settings.image_paint
    current_brush = tool.brush

    rr = bb.row(align=True)
    # v4.2までブラシがアセットじゃない
    if bpy.app.version < (4, 2, 9):
        bb = rr.box()
        bb.label(text="Essentials")
        cc = bb.column(align=False)
        for i in bpy.data.brushes:
            if i.use_paint_image and i.name.lower() not in brush_exclude_list:
                is_use = current_brush.name == i.name
                _Util.MPM_OT_SetPointer.operator(cc, i.name, tool, "brush", i, depress=is_use, icon_value=cc.icon(i))
                cnt += 1
                if cnt % limit_rows == 0:
                    cc = rr.column(align=True)
    # v4.3以降はブラシがアセット
    else:
        active_tool = bpy.context.workspace.tools.from_space_view3d_mode(mode=bpy.context.mode)

        def _callback_operator_select_brush(context, layout, brush_name):
            def _select_brush(context, lib_type, lib_id, asset_id):
                bpy.ops.brush.asset_activate(
                    asset_library_type=lib_type,
                    asset_library_identifier=lib_id,
                    relative_asset_identifier=asset_id)
            is_depress = active_tool.use_brushes and current_brush.name == brush_name
            _Util.MPM_OT_CallbackOperator.operator(layout, brush_name, "_MenuTexturePaint.select_brush." + brush_name,
                                                   _select_brush, (context, "ESSENTIALS", "", "brushes\\essentials_brushes-mesh_texture.blend\\Brush\\" + brush_name), depress=is_depress)

        def _callback_operator_select_tool(context, layout, label_name, tool_id):
            def _select_tool(context, tool_name):
                bpy.ops.wm.tool_set_by_id(name=tool_name)
            is_depress = not active_tool.use_brushes and active_tool.idname == tool_id
            _Util.MPM_OT_CallbackOperator.operator(layout, label_name, "_MenuTexturePaint.select_tool." + tool_id,
                                                   _select_tool, (context, tool_id), depress=is_depress)
        # Essential
        for i in BRUSH_INFO:
            if i[0] == "-":
                bb = rr.box()
                bb.label(text=i[1:])
                cc = bb.column(align=False)
                continue
            if i.lower() not in brush_exclude_list:
                _callback_operator_select_brush(context, cc, i)
        # Custom
        bb = rr.box()
        bb.label(text="User")
        rrr = bb.row(align=True)
        cc = rrr.column(align=False)
        for i in bpy.data.brushes:
            if i.use_paint_image and i.name not in BRUSH_INFO and i.name.lower() not in brush_exclude_list:
                _Util.MPM_OT_SetPointer.operator(cc, i.name, tool, "brush", i, depress=current_brush == i)
                cnt += 1
                if cnt % limit_rows == 0:
                    cc = rrr.column(align=True)

    cc = rr.column()
    # Strokes
    cnt = 0
    bb = cc.box()
    bb.label(text="Stroke")
    rrr = bb.row(align=True)
    ccc = rrr.column(align=True)
    for i in _Util.enum_values(current_brush, 'stroke_method'):
        is_use = current_brush.stroke_method == i
        _Util.MPM_OT_SetterBase.operator(ccc, _Util.MPM_OT_SetString.bl_idname, i,
                                         current_brush, "stroke_method", i, depress=is_use)
        cnt += 1
        if cnt % limit_rows == 0:
            ccc = rrr.column(align=True)

    # Blends
    blend_include_list = [item.strip() for item in _AddonPreferences.Accessor.get_image_paint_blend_include().lower().split(',')]
    cnt = 0
    bb = cc.box()
    bb.label(text="Blend")
    rrr = bb.row(align=True)
    ccc = rrr.column(align=True)
    for i in _Util.enum_values(current_brush, 'blend'):
        if i.lower() in blend_include_list:
            is_use = current_brush.blend == i
            # c2.operator(OT_TexPaint_Blend.bl_idname, text=i, depress=is_use).methodName = i
            _Util.MPM_OT_SetterBase.operator(ccc, _Util.MPM_OT_SetString.bl_idname, i,
                                             current_brush, "blend", i, depress=is_use)
            # current_brush.blend = self.methodName
            cnt += 1
            if cnt % limit_rows == 0:
                ccc = rrr.column(align=True)

    # brush proeprty
    cc = rr.column(align=True)
    bb = cc.box()
    bb.label(text="Property")
    ccc = bb.column(align=True)
    unified_paint_settings = context.tool_settings.unified_paint_settings
    # color
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_color else current_brush
    rrr = ccc.row(align=True)
    rrr.label(text="Color")
    rrrr = rrr.row(align=True)
    rrrr.scale_x = 0.5
    UnifiedPaintPanel.prop_unified_color(rrrr, context, brush_property_target, "color", text="")
    UnifiedPaintPanel.prop_unified_color(rrrr, context, brush_property_target, "secondary_color", text="")

    _Util.MPM_OT_CallbackOperator.operator(rrr, "", "_MenuTexturePaint.swap_color",
                                           SwapBrushColor, (context, brush_property_target,), icon="ARROW_LEFTRIGHT")
    _Util.MPM_OT_CallbackOperator.operator(rrr, "WHITE", "_MenuTexturePaint.set_white",
                                           lambda x: setattr(x, "color", mathutils.Color((1.0, 1.0, 1.0))), (brush_property_target,))
    _Util.MPM_OT_CallbackOperator.operator(rrr, "BLACK", "_MenuTexturePaint.set_black",
                                           lambda x: setattr(x, "color", mathutils.Color((0.0, 0.0, 0.0))), (brush_property_target,))
    rrr.prop_with_popover(context.scene.mpm_prop, "ColorPalettePopoverEnum", text="", panel="MPM_PT_BrushColorPalettePanel",)
    _Util.layout_prop(rrr, unified_paint_settings, "use_unified_color")

    # size
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_size else current_brush
    rrr = ccc.row()
    _Util.layout_prop(rrr, brush_property_target, "size")
    rrrr = rrr.row(align=True)
    _Util.MPM_OT_SetInt.operator(rrrr, "50%", brush_property_target, "size", int(brush_property_target.size * 0.5))
    _Util.MPM_OT_SetInt.operator(rrrr, "80%", brush_property_target, "size", int(brush_property_target.size * 0.8))
    _Util.MPM_OT_SetInt.operator(rrrr, "150%", brush_property_target, "size", int(brush_property_target.size * 1.5))
    _Util.MPM_OT_SetInt.operator(rrrr, "200%", brush_property_target, "size", int(brush_property_target.size * 2.0))
    _Util.layout_prop(rrrr, unified_paint_settings, "use_unified_size")
    # strength
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_strength else current_brush
    rrr = ccc.row()
    _Util.layout_prop(rrr, brush_property_target, "strength")
    rrrr = rrr.row(align=True)
    _Util.MPM_OT_SetSingle.operator(rrrr, "50%", brush_property_target, "strength", brush_property_target.strength / 2)
    _Util.MPM_OT_SetSingle.operator(rrrr, "200%", brush_property_target, "strength", brush_property_target.strength * 2)
    _Util.MPM_OT_SetSingle.operator(rrrr, "0.1", brush_property_target, "strength", 0.1)
    _Util.MPM_OT_SetSingle.operator(rrrr, "1.0", brush_property_target, "strength", 1.0)
    _Util.layout_prop(rrrr, unified_paint_settings, "use_unified_strength")

    # Etc
    rrr = ccc.row()
    _Util.layout_prop(rrr, current_brush, "use_accumulate")

    DrawBrushAngle(context, rrr)
    DrawMirrorOption(context, rrr)
    DrawBehaviourOfControlKey(ccc)
    
    # Applyメニュー
    bb = ccc.box()
    bb.label(text="Apply", icon="CHECKMARK")
    bb.operator("image.save_all_modified", text="Save All Image")


def DrawBehaviourOfControlKey(layout):
    row = layout.row(align=True)
    row.label(text="Holding Ctrl Key is")
    is_erace_alpha = _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    _Util.layout_operator(row, MPM_OT_TexPaint_ToggleCtrlBehaviour.bl_idname, "SubColor", is_erace_alpha, depress=not is_erace_alpha)
    _Util.layout_operator(row, MPM_OT_TexPaint_ToggleCtrlBehaviour.bl_idname, "Erase Alpha", not is_erace_alpha, depress=is_erace_alpha)


def DrawBrushAngle(context, layout):
    row = layout.row(align=True)
    row.label(text="Angle")
    from math import pi
    _Util.MPM_OT_SetterBase.operator(row, _Util.MPM_OT_SetSingle.bl_idname, "0", context.tool_settings.image_paint.brush.texture_slot, "angle", 0)
    _Util.MPM_OT_SetterBase.operator(row, _Util.MPM_OT_SetSingle.bl_idname, "180", context.tool_settings.image_paint.brush.texture_slot, "angle", pi)


def DrawMirrorOption(context, layout):
    mrow, msub = _Util.layout_for_mirror(layout)
    # _Util.layout_prop(msub, context.object, "use_mesh_mirror_x", text="X", toggle=True)
    # _Util.layout_prop(msub, context.object, "use_mesh_mirror_y", text="Y", toggle=True)
    # _Util.layout_prop(msub, context.object, "use_mesh_mirror_z", text="Z", toggle=True)
    _Util.MPM_OT_SetterBase.operator(msub, _Util.MPM_OT_SetBoolToggle.bl_idname, "X", context.object, "use_mesh_mirror_x")
    _Util.MPM_OT_SetterBase.operator(msub, _Util.MPM_OT_SetBoolToggle.bl_idname, "Y", context.object, "use_mesh_mirror_y")
    _Util.MPM_OT_SetterBase.operator(msub, _Util.MPM_OT_SetBoolToggle.bl_idname, "Z", context.object, "use_mesh_mirror_z")
# --------------------------------------------------------------------------------


def SwapBrushColor(context, brush_property_target):
    color = brush_property_target.color.copy()
    brush_property_target.color = brush_property_target.secondary_color.copy()
    brush_property_target.secondary_color = color


class MPM_OT_TexPaint_SwapColor(bpy.types.Operator):
    bl_idname = "mpm.texpaint_swap_color"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        brush = context.tool_settings.image_paint.brush
        color = brush.color.copy()
        brush.color = brush.secondary_color.copy()
        brush.secondary_color = color
        return {'FINISHED'}


class MPM_OT_TexPaint_SetBlack(bpy.types.Operator):
    bl_idname = "mpm.texpaint_set_black"
    bl_label = "Set Black"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.tool_settings.image_paint.brush.color = mathutils.Color((0.0, 0.0, 0.0))
        return {'FINISHED'}


class MPM_OT_TexPaint_SetWhite(bpy.types.Operator):
    bl_idname = "mpm.texpaint_set_white"
    bl_label = "Set White"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.tool_settings.image_paint.brush.color = mathutils.Color((1.0, 1.0, 1.0))
        return {'FINISHED'}


class MPM_OT_TexPaint_ToggleCtrlBehaviour(bpy.types.Operator):
    bl_idname = "mpm.texpaint_toggle_ctrl_behaviour"
    bl_label = "Toggle Ctrl Behaviour"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        new_value = not _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
        _AddonPreferences.Accessor.set_image_paint_ctrl_behaviour(new_value)
        global key_ctrl_lmb_erasealpha
        global key_keydown_ctrl
        global key_ctrl_lmb_invert
        key_ctrl_lmb_erasealpha.active = new_value
        key_keydown_ctrl.active = new_value
        key_ctrl_lmb_invert.active = not new_value
        return {'FINISHED'}


g_lastBlend = ""
g_lastBrushName = ""


class MPM_OT_TexPaint_SwitchCtrlBehaviour(bpy.types.Operator):
    bl_idname = "mpm.texpaint_switch_ctrl_behaviour"
    bl_label = "Switch Ctrl Behaviour"

    @classmethod
    def poll(cls, context):
        return context.tool_settings.image_paint.brush.stroke_method != "CURVE"

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.ctrl:
            return {'PASS_THROUGH'}
        global g_lastBlend
        if g_lastBlend != "":
            context.tool_settings.image_paint.brush.blend = g_lastBlend
            g_lastBlend = ""
        context.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}

    def execute(self, context):
        global g_lastBlend
        g_lastBlend = context.tool_settings.image_paint.brush.blend
        if g_lastBlend == 'ERASE_ALPHA':
            g_lastBlend = 'MIX'
        context.tool_settings.image_paint.brush.blend = 'ERASE_ALPHA'
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class MPM_OT_TexPaint_ChangeSoften(bpy.types.Operator):
    bl_idname = "mpm.texpaint_change_soften"
    bl_label = "Change Soften"

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.shift:
            return {'PASS_THROUGH'}
        global g_lastBrushName
        if g_lastBrushName != "":
            if g_lastBrushName in bpy.data.brushes:
                context.tool_settings.image_paint.brush = bpy.data.brushes[g_lastBrushName]
            g_lastBrushName = ""
        context.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}

    def execute(self, context):
        global g_lastBrushName
        g_lastBrushName = context.tool_settings.image_paint.brush.name
        name = _AddonPreferences.Accessor.get_image_paint_shift_brush_name()
        if name in bpy.data.brushes:
            context.tool_settings.image_paint.brush = bpy.data.brushes[name]
            self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            _Util.show_msgbox("Set a valid brush name in the preferences.", icon='ERROR')
            return {'CANCELLED'}
# --------------------------------------------------------------------------------


class MPM_PT_BrushColorPalettePanel(bpy.types.Panel):
    bl_label = ""
    bl_space_type = "VIEW_3D"
    bl_region_type = "HEADER"

    def draw(self, context):
        layout = self.layout
        settings = context.tool_settings.image_paint
        layout.template_ID(settings, "palette", new="palette.new")
        if settings.palette:
            layout.template_palette(settings, "palette", color=True)
# --------------------------------------------------------------------------------


classes = (
    MPM_OT_TexPaint_ToggleCtrlBehaviour,
    MPM_OT_TexPaint_SwitchCtrlBehaviour,
    MPM_OT_TexPaint_ChangeSoften,
    MPM_PT_BrushColorPalettePanel,
)

addon_keymaps = []


def register():
    _Util.register_classes(classes)
    # Keymaps
    global key_ctrl_lmb_erasealpha
    global key_ctrl_lmb_invert
    global key_keydown_ctrl
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    key_keydown_ctrl = km.keymap_items.new(MPM_OT_TexPaint_SwitchCtrlBehaviour.bl_idname, 'LEFT_CTRL', 'PRESS')
    key_keydown_ctrl.active = _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    addon_keymaps.append((km, key_keydown_ctrl))

    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    key_ctrl_lmb_erasealpha = km.keymap_items.new("paint.image_paint", 'LEFTMOUSE', 'PRESS', ctrl=True)
    key_ctrl_lmb_erasealpha.active = _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    addon_keymaps.append((km, key_ctrl_lmb_erasealpha))

    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    key_ctrl_lmb_invert = km.keymap_items.new("paint.image_paint", 'LEFTMOUSE', 'PRESS', ctrl=True)
    key_ctrl_lmb_invert.active = not _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    key_ctrl_lmb_invert.properties.mode = 'INVERT'
    addon_keymaps.append((km, key_ctrl_lmb_invert))

    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    kmi = km.keymap_items.new(MPM_OT_TexPaint_ChangeSoften.bl_idname, 'LEFT_SHIFT', 'PRESS')
    addon_keymaps.append((km, kmi))

    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    kmi = km.keymap_items.new("paint.image_paint", 'LEFTMOUSE', 'PRESS', shift=True)
    kmi.properties.mode = 'SMOOTH'
    addon_keymaps.append((km, kmi))


def unregister():
    _Util.unregister_classes(classes)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    del addon_keymaps[:]


BRUSH_INFO = [
    "-Essentials",
    "Paint Soft",
    "Paint Soft Pressure",
    "Paint Hard",
    "Paint Hard Pressure",
    "Airbrush",
    "Erase Soft",
    "Erase Hard",
    "Erase Hard Pressure",
    "Blur",
    "Smear",
    "Fill",
    "Clone",
    "Mask",
]
