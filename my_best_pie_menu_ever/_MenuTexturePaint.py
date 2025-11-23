if "bpy" in locals():
    import importlib
    for m in (
        _Util,
        g,
        _AddonPreferences,
    ):
        importlib.reload(m)
else:
    import bpy
    from . import (
        _Util,
        g,
        _AddonPreferences,
    )
import os
import time
import mathutils
from bl_ui.properties_paint_common import UnifiedPaintPanel
key_ctrl_lmb_erasealpha = None
key_ctrl_lmb_invert = None
key_keydown_ctrl = None
# --------------------------------------------------------------------------------
# テクスチャペイントメニュー
# --------------------------------------------------------------------------------
g_is_filter_mode = False
g_is_filter_set_mode_enter = False
g_filter_mode_enter_lasttime = 0


def _switch_filter_mode():
    global g_is_filter_mode
    g_is_filter_mode = not g_is_filter_mode


def _switch_filter_setting_mode():
    global g_is_filter_set_mode_enter, g_filter_mode_enter_lasttime
    g_is_filter_set_mode_enter = not g_is_filter_set_mode_enter
    g_filter_mode_enter_lasttime = time.time()
    if g_is_filter_set_mode_enter:  # モードに入るときだけ警告を表示
        g.on_closed["warn_open_filter_set_texpaint"] = lambda: _Util.show_msgbox("Please hold down the shift key to click.", "Error", "ERROR")


def _select_essential_brush_operator(context, layout, brush_name, is_depress):
    def __select_brush(context, lib_type, lib_id, asset_id):
        bpy.ops.brush.asset_activate(
            asset_library_type=lib_type,
            asset_library_identifier=lib_id,
            relative_asset_identifier=asset_id)
    _Util.MPM_OT_CallbackOperator.operator(layout, brush_name, "_MenuTexturePaint.select_essential_brush." + brush_name,
                                           __select_brush, (context, "ESSENTIALS", "", os.path.join("brushes", "essentials_brushes-mesh_texture.blend", "Brush", brush_name)), depress=is_depress)
# def _select_custom_brush_operator(context, layout, brush, is_depress):
#     def __select_brush(context, lib_type, lib_id, asset_id):
#         bpy.ops.brush.asset_activate(
#             asset_library_type=lib_type,
#             asset_library_identifier=lib_id,
#             relative_asset_identifier=asset_id)
#     _Util.MPM_OT_CallbackOperator.operator(layout, brush.name, "_MenuTexturePaint.select_custom_brush." + brush.name,
#                                            __select_brush, (context, "ESSENTIALS", "", os.path.join("brushes", "essentials_brushes-mesh_texture.blend", "Brush", brush.name)), depress=is_depress)


def _blend_filter_operator(context, layout, label_name, tool_id, in_filter):
    def __set(context, tool_id, in_filter):
        filter = _AddonPreferences.get_data().imagePaintBlendFilterByName
        tool_id = tool_id.lower()
        if in_filter:
            filter = filter.replace(tool_id, "")
        else:
            filter += "," + tool_id
        _AddonPreferences.get_data().imagePaintBlendFilterByName = ",".join([i for i in map(str.strip, filter.lower().split(',')) if i])
        global g_filter_mode_enter_lasttime
        g_filter_mode_enter_lasttime = time.time()
    _Util.MPM_OT_CallbackOperator.operator(layout, label_name, __name__ + ".set_blend_filter." + tool_id,
                                           __set, (context, tool_id, in_filter), depress=in_filter)


def _register_filter_operator(context, layout, label_name, tool_id, in_filter):
    def __set(context, tool_id, in_filter):
        global g_filter_mode_enter_lasttime
        g_filter_mode_enter_lasttime = time.time()
        pref = _AddonPreferences.get_data()
        filter = pref.imagePaintBrushFilterByName
        tool_id = tool_id.lower()
        if in_filter:
            filter = filter.replace(tool_id, "")
        else:
            filter += "," + tool_id
        pref.imagePaintBrushFilterByName = (",".join([i for i in map(str.strip, filter.lower().split(',')) if i]))
    _Util.MPM_OT_CallbackOperator.operator(layout, label_name, __name__ + ".set_brush_filter." + tool_id,
                                           __set, (context, tool_id, in_filter), depress=in_filter)


def draw(pie, context):
    pref = _AddonPreferences.get_data()
    # フィルターモード
    global g_is_filter_mode, g_is_filter_set_mode_enter, g_filter_mode_enter_lasttime
    g_is_filter_set_mode_enter = g_is_filter_set_mode_enter and (time.time() - g_filter_mode_enter_lasttime) < 0.1
    g.on_closed.pop("warn_open_filter_set_texpaint", None)

    box = pie.split().box()
    box.label(text="TexturePaint Brush Filter Setting Mode" if g_is_filter_set_mode_enter else "TexturePaint Primary")
    c = box.column(align=True)
    # top
    layout_topbar = c.row(align=True)
    layout_topbar.alignment = "RIGHT"
    # Brushe
    r = c.row(align=True)
    layout_brushes = r.box()
    layout_brushes.label(text="Brushes(Filtered)" if g_is_filter_mode else "Brushes", icon="BRUSH_DATA")
    # Stroke
    layout_stroke = None
    c = r.column(align=True)
    if not g_is_filter_set_mode_enter:
        layout_stroke = c.box()
        layout_stroke.label(text="Stroke", icon="STROKE")
    # Blend
    blend_filter_names = [i for i in map(str.strip, _AddonPreferences.get_data().imagePaintBlendFilterByName.split(',')) if i]
    layout_blend = c.box()
    layout_blend.label(text="Blend(All)" if g_is_filter_set_mode_enter else "Blend(Filtered)" if g_is_filter_mode and blend_filter_names else "Blend(Default)")
    # Property
    if not g_is_filter_set_mode_enter:
        c = r.column(align=True)
        layout_property = c.box()
        layout_property.label(text="Property")
    # Apply
    if not g_is_filter_set_mode_enter:
        layout_apply = c.box()
        layout_apply.label(text="Apply", icon="CHECKMARK")

    # top
    if not g_is_filter_set_mode_enter:
        _Util.MPM_OT_CallbackOperator.operator(layout_topbar, "Disable Filter Mode" if g_is_filter_mode else "Enable Filter Mode", __name__ + ".g_is_filter_mode",
                                               _switch_filter_mode, None, "FILTER", depress=g_is_filter_mode)
    _Util.MPM_OT_CallbackOperator.operator(layout_topbar, "Exit Filter Setting" if g_is_filter_set_mode_enter else "Enter Filter Setting", __name__ + ".g_is_filter_mode_enter",
                                           _switch_filter_setting_mode, None, "TOOL_SETTINGS",  depress=g_is_filter_set_mode_enter)
    # Brush, Stroke, Blend...
    cnt = 0
    tool = context.tool_settings.image_paint
    current_brush = tool.brush
    brush_filter_names = [i for i in map(str.strip, pref.imagePaintBrushFilterByName.lower().split(',')) if i]
    r = layout_brushes.row(align=True)
    c = r.column(align=True)

    # v4.3以降はブラシがアセット
    active_tool = bpy.context.workspace.tools.from_space_view3d_mode(mode=bpy.context.mode)

    # Essential
    for brush_name in BRUSH_INFO:
        if g_is_filter_set_mode_enter or not g_is_filter_mode:
            if brush_name[0] == "-":
                c = r.box().column(align=True)
                c.label(text=brush_name[1:])
                continue
            if g_is_filter_set_mode_enter:
                _register_filter_operator(context, c, brush_name, brush_name, brush_name.lower() in brush_filter_names)
            else:
                _select_essential_brush_operator(context, c, brush_name, active_tool.use_brushes and current_brush.name == brush_name)
        # フィルターモード
        else:
            if brush_name.lower() not in brush_filter_names:
                continue  # 表示しない
            _select_essential_brush_operator(context, c, brush_name, active_tool.use_brushes and current_brush.name == brush_name)
            if (cnt := cnt+1) % pref.imagePaintLimitRowCount == 0:
                c = r.column(align=True)

    # Local/Custom
    # 任意のブラシのcontext.tool_settings.image_paint.brush_asset_referenceにアクセスする術がないため不可能
    # if g_is_filter_set_mode_enter or not g_is_filter_mode:
    #     box = r.box()
    #     box.label(text="User")
    #     r = box.row(align=True)
    #     c = r.column(align=False)
    #     for brush in [i for i in bpy.data.brushes if i.use_paint_image and i.name not in BRUSH_INFO]:
    #         if g_is_filter_set_mode_enter:
    #             _register_filter_operator(context, c, brush.name, brush.name, brush.name.lower() in brush_filter_names)
    #         else:
    #             _select_custom_brush_operator(context, c, brush.name, active_tool.use_brushes and current_brush.name == brush.name)
    #             if (cnt := cnt+1) % pref.imagePaintLimitRowCount == 0:
    #                 c = r.column(align=True)
    # # フィルターモード
    # else:
    #     for brush in [i for i in bpy.data.brushes if i.use_paint_image and i.name not in BRUSH_INFO]:
    #         if brush_name.lower() not in brush_filter_names:
    #             continue  # 表示しない
    #         _select_essential_brush_operator(context, c, brush.name, active_tool.use_brushes and current_brush.name == brush.name)
    #         if (cnt := cnt+1) % pref.imagePaintLimitRowCount == 0:
    #             c = r.column(align=True)

    # Strokes
    if layout_stroke:
        cnt = 0
        c = layout_stroke.column(align=True)
        for brush_name in _Util.enum_identifier(current_brush, "stroke_method"):
            is_use = current_brush.stroke_method == brush_name
            _Util.MPM_OT_SetterBase.operator(c, _Util.MPM_OT_SetString.bl_idname, brush_name,
                                             current_brush, "stroke_method", brush_name, depress=is_use)

    # Blends
    cnt = 0
    default_blends = ["mix", "screen", "overlay", "erase_alpha"]
    blend_filter_names = [i for i in map(str.strip, _AddonPreferences.get_data().imagePaintBlendFilterByName.split(',')) if i]
    r = layout_blend.row(align=True)
    c = r.column(align=True)
    if g_is_filter_set_mode_enter or not g_is_filter_mode:
        for blend in _Util.enum_identifier(current_brush, "blend"):
            if g_is_filter_set_mode_enter:
                _blend_filter_operator(context, c, blend, blend, blend.lower() in blend_filter_names)
                if (cnt := cnt+1) % 12 == 0:
                    c = r.column(align=True)
            else:
                # 全部は多いのでデフォルトのブレンドを表示
                if blend.lower() in default_blends:
                    _Util.MPM_OT_SetterBase.operator(c, _Util.MPM_OT_SetString.bl_idname, blend, current_brush,
                                                     "blend", blend, depress=current_brush.blend == blend)
    # フィルターモード
    else:
        for blend in _Util.enum_identifier(current_brush, "blend"):
            if blend_filter_names:
                if blend.lower() not in blend_filter_names:
                    continue  # 表示しない
            elif blend.lower() not in default_blends:
                continue
            _Util.MPM_OT_SetterBase.operator(c, _Util.MPM_OT_SetString.bl_idname, blend, current_brush,
                                             "blend", blend, depress=current_brush.blend == blend)
            if (cnt := cnt+1) % pref.imagePaintLimitRowCount == 0:
                c = r.column(align=True)

    if g_is_filter_set_mode_enter:
        return

    # brush proeprty
    c = layout_property.column(align=True)
    unified_paint_settings = getattr(context.tool_settings, "unified_paint_settings", None) \
        or getattr(tool, "unified_paint_settings", None)  # v5.0からunified_paint_settingsの場所が変わった

    # color
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_color else current_brush
    s = c.row().split(factor=0.1, align=True)
    r1 = s.row(align=True)
    s = s.row().split(factor=0.2, align=True)
    r2 = s.row(align=True)
    s = s.row().split(factor=0.2, align=True)
    r3 = s.row(align=True)
    r4 = s.row(align=True)
    # r4.alignment = "LEFT"
    r1.label(text="Color")
    UnifiedPaintPanel.prop_unified_color(r2, context, brush_property_target, "color", text="")
    UnifiedPaintPanel.prop_unified_color(r2, context, brush_property_target, "secondary_color", text="")
    _Util.MPM_OT_CallbackOperator.operator(r2, "", "_MenuTexturePaint.swap_color",
                                           _SwapBrushColor, (context, brush_property_target,), icon="ARROW_LEFTRIGHT")
    _Util.MPM_OT_CallbackOperator.operator(r3, "W", "_MenuTexturePaint.set_white",
                                           lambda x: setattr(x, "color", mathutils.Color((1.0, 1.0, 1.0))), (brush_property_target,))
    _Util.MPM_OT_CallbackOperator.operator(r3, "B", "_MenuTexturePaint.set_black",
                                           lambda x: setattr(x, "color", mathutils.Color((0.0, 0.0, 0.0))), (brush_property_target,))
    r4.prop_with_popover(context.scene.mpm_prop, "ColorPalettePopoverEnum", text="", panel="MPM_PT_BrushColorPalettePanel",)
    _Util.layout_prop(r4, unified_paint_settings, "use_unified_color")
    # size
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_size else current_brush
    s = c.row().split(factor=0.29, align=True)
    r1 = s.row(align=True)
    s = s.row().split(factor=0.56, align=True)
    r2 = s.row(align=True)
    r3 = s.row(align=True)
    # r3.alignment = "LEFT"
    _Util.layout_prop(r1, brush_property_target, "size")
    _Util.MPM_OT_SetInt.operator(r2, "50%", brush_property_target, "size", int(brush_property_target.size * 0.5))
    _Util.MPM_OT_SetInt.operator(r2, "80%", brush_property_target, "size", int(brush_property_target.size * 0.8))
    _Util.MPM_OT_SetInt.operator(r2, "150%", brush_property_target, "size", int(brush_property_target.size * 1.5))
    _Util.MPM_OT_SetInt.operator(r2, "200%", brush_property_target, "size", int(brush_property_target.size * 2.0))
    _Util.layout_prop(r3, unified_paint_settings, "use_unified_size")
    # strength
    brush_property_target = unified_paint_settings if unified_paint_settings.use_unified_strength else current_brush
    s = c.row().split(factor=0.29, align=True)
    r1 = s.row(align=True)
    s = s.row().split(factor=0.56, align=True)
    r2 = s.row(align=True)
    r3 = s.row(align=True)
    # r3.alignment = "LEFT"
    _Util.layout_prop(r1, brush_property_target, "strength")
    _Util.MPM_OT_SetSingle.operator(r2, "50%", brush_property_target, "strength", brush_property_target.strength / 2)
    _Util.MPM_OT_SetSingle.operator(r2, "200%", brush_property_target, "strength", brush_property_target.strength * 2)
    _Util.MPM_OT_SetSingle.operator(r2, "0.1", brush_property_target, "strength", 0.1)
    _Util.MPM_OT_SetSingle.operator(r2, "1.0", brush_property_target, "strength", 1.0)
    _Util.layout_prop(r3, unified_paint_settings, "use_unified_strength")

    # Etc
    r = c.row(align=True)
    # r.alignment = "LEFT"

    _Util.layout_prop(r, current_brush, "use_accumulate")
    _DrawBrushAngle(context, r)
    _DrawMirrorOption(context, r)
    _DrawBehaviourOfControlKey(c)

    # Applyメニュー
    c = layout_apply.column(align=True)
    r = c.row()
    r.alignment = "LEFT"
    r.operator("image.save_all_modified", text="Save All Image")
    r = c.row()
    r.alignment = "LEFT"
    r.operator(MPM_OT_TexPaint_RegisterShiftKeyBrushInfo.bl_idname)


def _DrawBehaviourOfControlKey(layout):
    s = layout.split(factor=0.2, align=True)
    r1 = s.row(align=True)
    r2 = s.row(align=True)
    r2.alignment = "LEFT"
    r1.label(text="Holding Ctrl Key")
    is_erace_alpha = _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    _Util.layout_operator(r2, MPM_OT_TexPaint_ToggleCtrlBehaviour.bl_idname, "SubColor", depress=not is_erace_alpha)
    _Util.layout_operator(r2, MPM_OT_TexPaint_ToggleCtrlBehaviour.bl_idname, "Erase Alpha", depress=is_erace_alpha)


def _DrawBrushAngle(context, layout):
    r = layout.row(align=True)
    r.label(text="Angle")
    from math import pi
    _Util.MPM_OT_SetterBase.operator(r, _Util.MPM_OT_SetSingle.bl_idname, "0", context.tool_settings.image_paint.brush.texture_slot, "angle", 0)
    _Util.MPM_OT_SetterBase.operator(r, _Util.MPM_OT_SetSingle.bl_idname, "180", context.tool_settings.image_paint.brush.texture_slot, "angle", pi)


def _DrawMirrorOption(context, layout):
    mrow, msub = _Util.layout_for_mirror(layout)
    _Util.MPM_OT_SetterBase.operator(msub, _Util.MPM_OT_SetBoolToggle.bl_idname, "X", context.object, "use_mesh_mirror_x")
    _Util.MPM_OT_SetterBase.operator(msub, _Util.MPM_OT_SetBoolToggle.bl_idname, "Y", context.object, "use_mesh_mirror_y")
    _Util.MPM_OT_SetterBase.operator(msub, _Util.MPM_OT_SetBoolToggle.bl_idname, "Z", context.object, "use_mesh_mirror_z")
# --------------------------------------------------------------------------------


def _SwapBrushColor(context, brush_property_target):
    color = brush_property_target.color.copy()
    brush_property_target.color = brush_property_target.secondary_color.copy()
    brush_property_target.secondary_color = color


class MPM_OT_TexPaint_ToggleCtrlBehaviour(bpy.types.Operator):
    bl_idname = "mpm.texpaint_toggle_ctrl_behaviour"
    bl_label = "Toggle Ctrl Behaviour"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        new_value = not _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
        _AddonPreferences.Accessor.set_image_paint_ctrl_behaviour(new_value)
        global key_ctrl_lmb_erasealpha
        global key_keydown_ctrl
        global key_ctrl_lmb_invert
        key_ctrl_lmb_erasealpha.active = new_value
        key_keydown_ctrl.active = new_value
        key_ctrl_lmb_invert.active = not new_value
        return {"FINISHED"}


g_lastBlend = ""


class MPM_OT_TexPaint_SwitchCtrlBehaviour(bpy.types.Operator):
    bl_idname = "mpm.texpaint_switch_ctrl_behaviour"
    bl_label = "Switch Ctrl Behaviour(MyBestPieMenuEver)"

    @classmethod
    def poll(cls, context):
        return context.tool_settings.image_paint.brush.stroke_method != "CURVE"

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.ctrl:
            return {"PASS_THROUGH"}
        global g_lastBlend
        if g_lastBlend != "":
            context.tool_settings.image_paint.brush.blend = g_lastBlend
            g_lastBlend = ""
        context.window_manager.event_timer_remove(self._timer)
        return {"FINISHED"}

    def execute(self, context):
        global g_lastBlend
        g_lastBlend = context.tool_settings.image_paint.brush.blend
        if g_lastBlend == "ERASE_ALPHA":
            g_lastBlend = "MIX"
        context.tool_settings.image_paint.brush.blend = "ERASE_ALPHA"
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


class MPM_OT_TexPaint_ChangeSoften(bpy.types.Operator):
    bl_idname = "mpm.texpaint_change_soften"
    bl_label = "Switch Shift Behaviour(MyBestPieMenuEver)"

    def execute(self, context):
        self.last_brush = context.tool_settings.image_paint.brush
        ref = context.tool_settings.image_paint.brush_asset_reference
        self.last_brush_info = (ref.asset_library_type, ref.asset_library_identifier, ref.relative_asset_identifier)
        info = _AddonPreferences.get_data().imagePaintShiftBrushInfo.split(",")
        result = bpy.ops.brush.asset_activate(
            asset_library_type=info[0],
            asset_library_identifier=info[1],
            relative_asset_identifier=info[2])
        if "FINISHED" in result:
            self.timer = context.window_manager.event_timer_add(0.1, window=context.window)
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        _Util.show_msgbox(f"Set a valid brush name in the preferences. Current: {self.last_brush_info}({result})", icon="ERROR")
        return {"CANCELLED"}

    def modal(self, context, event):
        # context.area.tag_redraw()
        if event.shift:
            return {"PASS_THROUGH"}
        if self.last_brush:
            bpy.ops.brush.asset_activate(
                asset_library_type=self.last_brush_info[0],
                asset_library_identifier=self.last_brush_info[1],
                relative_asset_identifier=self.last_brush_info[2])
        context.window_manager.event_timer_remove(self.timer)
        return {"FINISHED"}


class MPM_OT_TexPaint_RegisterShiftKeyBrushInfo(bpy.types.Operator):
    bl_idname = "mpm.texpaint_register_shiftkey_brush_info"
    bl_label = "Register Current Brush to Shift-key Brush"

    def execute(self, context):
        self.last_brush = context.tool_settings.image_paint.brush
        ref = context.tool_settings.image_paint.brush_asset_reference
        _AddonPreferences.get_data().imagePaintShiftBrushInfo = ",".join(
            [ref.asset_library_type, ref.asset_library_identifier, ref.relative_asset_identifier.replace("/", "\\")])
        return {"FINISHED"}


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
    MPM_OT_TexPaint_RegisterShiftKeyBrushInfo
)

addon_keymaps = []
msgbus_owner = "mpm.texture_paint"


def register():
    _Util.register_classes(classes)
    # Keymaps
    global key_ctrl_lmb_erasealpha
    global key_ctrl_lmb_invert
    global key_keydown_ctrl
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Image Paint", space_type="EMPTY")
    key_keydown_ctrl = km.keymap_items.new(MPM_OT_TexPaint_SwitchCtrlBehaviour.bl_idname, "LEFT_CTRL", "PRESS")
    key_keydown_ctrl.active = _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    addon_keymaps.append((km, key_keydown_ctrl))

    # ctrl押しながらクリックで必要
    km = wm.keyconfigs.addon.keymaps.new(name="Image Paint", space_type="EMPTY")
    key_ctrl_lmb_erasealpha = km.keymap_items.new("paint.image_paint", "LEFTMOUSE", "PRESS", ctrl=True)
    key_ctrl_lmb_erasealpha.active = _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    addon_keymaps.append((km, key_ctrl_lmb_erasealpha))

    # ctrl押しながらクリックで必要
    km = wm.keyconfigs.addon.keymaps.new(name="Image Paint", space_type="EMPTY")
    key_ctrl_lmb_invert = km.keymap_items.new("paint.image_paint", "LEFTMOUSE", "PRESS", ctrl=True)
    key_ctrl_lmb_invert.active = not _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    key_ctrl_lmb_invert.properties.mode = "INVERT"
    addon_keymaps.append((km, key_ctrl_lmb_invert))

    km = wm.keyconfigs.addon.keymaps.new(name="Image Paint", space_type="EMPTY")
    key_keydown_shift = km.keymap_items.new(MPM_OT_TexPaint_ChangeSoften.bl_idname, "LEFT_SHIFT", "PRESS")
    key_keydown_shift.active = True
    addon_keymaps.append((km, key_keydown_shift))

    # シフト押しながらクリックで必要
    km = wm.keyconfigs.addon.keymaps.new(name="Image Paint", space_type="EMPTY")
    key_shift_lmb = km.keymap_items.new("paint.image_paint", "LEFTMOUSE", "PRESS", shift=True)
    key_shift_lmb.active = True
    addon_keymaps.append((km, key_shift_lmb))


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
