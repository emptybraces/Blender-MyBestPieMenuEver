import bpy
import mathutils
from bpy.types import Panel, Menu, Operator
from bl_ui.properties_paint_common import UnifiedPaintPanel, brush_basic_texpaint_settings
from . import _Util
from . import _AddonPreferences
key_ctrl_lmb_erasealpha = None
key_ctrl_lmb_invert = None
key_keydown_ctrl = None
# --------------------------------------------------------------------------------
# テクスチャペイントメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Texture Paint')

    row = box.row(align=True) # Brush, Stroke, Blend...

    # Brushes
    box = row.box()
    box.label(text = "Brush")
    row2 = box.row()
    col2 = row2.column()
    cnt = 0
    limit_rows = _AddonPreferences.Accessor.get_image_paint_limit_row()
    brush_exclude_list = [item.strip() for item in _AddonPreferences.Accessor.get_image_paint_brush_exclude().lower().split(',')]
    for i in bpy.data.brushes:
        if i.use_paint_image and i.name.lower() not in brush_exclude_list:
            is_use = context.tool_settings.image_paint.brush.name == i.name
            _Util.OT_SetPointer.operator(col2, i.name, context.tool_settings.image_paint, "brush", i, depress=is_use)
            cnt += 1;
            if cnt % limit_rows == 0: col2 = row2.column()

    #Color picker
    box = row.box()
    box.label(text = "Color")
    row2 = box.row(align=True)
    row2.scale_x = 0.3
    UnifiedPaintPanel.prop_unified_color(row2, context, context.tool_settings.image_paint.brush, "color", text="")
    UnifiedPaintPanel.prop_unified_color(row2, context, context.tool_settings.image_paint.brush, "secondary_color", text="")
    _Util.layout_operator(box, OT_TexPaint_SwapColor.bl_idname)
    _Util.layout_operator(box, OT_TexPaint_SetWhite.bl_idname)
    _Util.layout_operator(box, OT_TexPaint_SetBlack.bl_idname)

    # Strokes
    cnt = 0
    box = row.box()
    box.label(text = "Stroke")
    row2 = box.row()
    col2 = row2.column()
    for i in _Util.enum_values(context.tool_settings.image_paint.brush, 'stroke_method'):
        is_use = context.tool_settings.image_paint.brush.stroke_method == i
        _Util.OT_SetterBase.operator(col2, _Util.OT_SetString.bl_idname, i, context.tool_settings.image_paint.brush, "stroke_method", i, depress=is_use)
        cnt += 1;
        if cnt % limit_rows == 0: col2 = row2.column()
    #Blends
    blend_include_list = [item.strip() for item in _AddonPreferences.Accessor.get_image_paint_blend_include().lower().split(',')]
    cnt = 0
    box = row.box()
    box.label(text = "Blend")
    row2 = box.row()
    col2 = row2.column()
    for i in _Util.enum_values(context.tool_settings.image_paint.brush, 'blend'):
        if i.lower() in blend_include_list:
            is_use = context.tool_settings.image_paint.brush.blend == i
            # col2.operator(OT_TexPaint_Blend.bl_idname, text=i, depress=is_use).methodName = i  
            _Util.OT_SetterBase.operator(col2, _Util.OT_SetString.bl_idname, i, context.tool_settings.image_paint.brush, "blend", i, depress=is_use)
            # context.tool_settings.image_paint.brush.blend = self.methodName  
            cnt += 1;
            if cnt % limit_rows == 0: col2 = row2.column()
# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    box = pie.split().box()
    box.operator("image.save_all_modified", text="Save All Image") 

    row = box.row(align=True)
    row.label(text = "Hold Ctrl Behaviour")
    ctrl_behaviour = _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    if ctrl_behaviour: # Erase Alpha mode
        _Util.layout_operator(row, OT_TexPaint_ToggleCtrlBehaviour.bl_idname, "SubColor", depress=False)
        _Util.layout_operator(row, _Util.OT_Empty.bl_idname, "Erase Alpha", False, depress=True)
    else:
        _Util.layout_operator(row, _Util.OT_Empty.bl_idname, "SubColor", False, depress=True)
        _Util.layout_operator(row, OT_TexPaint_ToggleCtrlBehaviour.bl_idname, "Erase Alpha", depress=False)

    row = box.row(align=True)
    row.label(text = "Angle")
    from math import pi
    _Util.OT_SetterBase.operator(row, _Util.OT_SetSingle.bl_idname, "0", context.tool_settings.image_paint.brush.texture_slot, "angle", 0)
    _Util.OT_SetterBase.operator(row, _Util.OT_SetSingle.bl_idname, "180", context.tool_settings.image_paint.brush.texture_slot, "angle", pi)

    mrow, msub = _Util.layout_for_mirror(row)
    # _Util.layout_prop(msub, context.object, "use_mesh_mirror_x", text="X", toggle=True)
    # _Util.layout_prop(msub, context.object, "use_mesh_mirror_y", text="Y", toggle=True)
    # _Util.layout_prop(msub, context.object, "use_mesh_mirror_z", text="Z", toggle=True)
    _Util.OT_SetterBase.operator(msub, _Util.OT_SetBoolToggle.bl_idname, "X", context.object, "use_mesh_mirror_x")
    _Util.OT_SetterBase.operator(msub, _Util.OT_SetBoolToggle.bl_idname, "Y", context.object, "use_mesh_mirror_y")
    _Util.OT_SetterBase.operator(msub, _Util.OT_SetBoolToggle.bl_idname, "Z", context.object, "use_mesh_mirror_z")

# --------------------------------------------------------------------------------
class OT_TexPaint_SwapColor(bpy.types.Operator):
    bl_idname = "mpme.texpaint_swap_color"
    bl_label = "Swap Color"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        brush = context.tool_settings.image_paint.brush
        color = brush.color.copy()
        brush.color = brush.secondary_color.copy()
        brush.secondary_color = color
        return {'FINISHED'}
class OT_TexPaint_SetBlack(bpy.types.Operator):
    bl_idname = "mpme.texpaint_set_black"
    bl_label = "Set Black"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        context.tool_settings.image_paint.brush.color = mathutils.Color((0.0,0.0,0.0))
        return {'FINISHED'}
class OT_TexPaint_SetWhite(bpy.types.Operator):
    bl_idname = "mpme.texpaint_set_white"
    bl_label = "Set White"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        context.tool_settings.image_paint.brush.color = mathutils.Color((1.0,1.0,1.0))
        return {'FINISHED'}
class OT_TexPaint_ToggleCtrlBehaviour(bpy.types.Operator):
    bl_idname = "mpme.texpaint_toggle_ctrl_behaviour"
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
class OT_TexPaint_SwitchCtrlBehaviour(bpy.types.Operator):
    bl_idname = "mpme.texpaint_switch_ctrl_behaviour"
    bl_label = "Switch Ctrl Behaviour"
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
        if g_lastBlend == 'ERASE_ALPHA': g_lastBlend = 'MIX'
        context.tool_settings.image_paint.brush.blend = 'ERASE_ALPHA'
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
class OT_TexPaint_ChangeSoften(bpy.types.Operator):
    bl_idname = "mpme.texpaint_change_soften"
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

classes = (
    OT_TexPaint_SwapColor,
    OT_TexPaint_SetBlack,
    OT_TexPaint_SetWhite,
    OT_TexPaint_ToggleCtrlBehaviour,
    OT_TexPaint_SwitchCtrlBehaviour,
    OT_TexPaint_ChangeSoften,
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
    key_keydown_ctrl = km.keymap_items.new(OT_TexPaint_SwitchCtrlBehaviour.bl_idname, 'LEFT_CTRL','PRESS')
    key_keydown_ctrl.active = _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    addon_keymaps.append((km, key_keydown_ctrl))
    
    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    key_ctrl_lmb_erasealpha = km.keymap_items.new("paint.image_paint", 'LEFTMOUSE','PRESS', ctrl=True)
    key_ctrl_lmb_erasealpha.active = _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    addon_keymaps.append((km, key_ctrl_lmb_erasealpha))
    
    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    key_ctrl_lmb_invert = km.keymap_items.new("paint.image_paint", 'LEFTMOUSE','PRESS', ctrl=True)
    key_ctrl_lmb_invert.active = not _AddonPreferences.Accessor.get_image_paint_ctrl_behaviour()
    key_ctrl_lmb_invert.properties.mode = 'INVERT'
    addon_keymaps.append((km, key_ctrl_lmb_invert))

    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    kmi = km.keymap_items.new(OT_TexPaint_ChangeSoften.bl_idname, 'LEFT_SHIFT', 'PRESS')
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