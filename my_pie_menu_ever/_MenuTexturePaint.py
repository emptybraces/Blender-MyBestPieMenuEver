import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util
from . import _AddonPreferences
key_ctrl_lmb_erasealpha = None
key_ctrl_lmb_invert = None
key_keydown_ctrl = None
key_keyup_ctrl = None
# --------------------------------------------------------------------------------
# ¥Æ¥¯¥¹¥Á¥ã¥Ú¥¤¥ó¥È¥á¥Ë¥å©`
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Texture Paint')

    row = box.row() # Brush, Stroke, Blend...

    box = row.box()
    box.label(text = "Brush")
    row2 = box.row()
    col2 = row2.column()
    cnt = 0
    limit_rows = _AddonPreferences.Accessor.GetImagePaintLimitRows()
    for i in bpy.data.brushes:
        if i.use_paint_image:
            is_use = context.tool_settings.image_paint.brush.name == i.name
            col2.operator(OT_TexPaint_ChangeBrush.bl_idname, text=i.name, depress=is_use).brushName = i.name
            cnt += 1;
            if cnt % limit_rows == 0: col2 = row2.column()
    # Strokes
    cnt = 0
    box = row.box()
    box.label(text = "Stroke")
    row2 = box.row()
    col2 = row2.column()
    for i in _Util.enum_values(context.tool_settings.image_paint.brush, 'stroke_method'):
        is_use = OT_TexPaint_StrokeMethod.getCurrent() == i
        col2.operator(OT_TexPaint_StrokeMethod.bl_idname, text=i, depress=is_use).methodName = i
        cnt += 1;
        if cnt % limit_rows == 0: col2 = row2.column()
    #Blends
    cnt = 0
    box = row.box()
    box.label(text = "Blend")
    row2 = box.row()
    col2 = row2.column()
    for i in _Util.enum_values(context.tool_settings.image_paint.brush, 'blend'):
        is_use = OT_TexPaint_Blend.getCurrent() == i
        col2.operator(OT_TexPaint_Blend.bl_idname, text=i, depress=is_use).methodName = i    
        cnt += 1;
        if cnt % limit_rows == 0: col2 = row2.column()

# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    box = pie.split().box()
    box.operator("image.save_all_modified") 

    row = box.row(align=True)
    row.label(text = "Press Ctrl Behaviour")
    ctrl_behaviour = _AddonPreferences.Accessor.GetImagePaintCtrlBehaviour()
    if ctrl_behaviour: # Erase Alpha mode
        _Util.layout_operator(row, OT_TexPaint_ToggleCtrlBehaviour.bl_idname, "Invert", depress=False)
        _Util.layout_operator(row, _Util.OT_Empty.bl_idname, "Erase Alpha", False, depress=True)
    else:
        _Util.layout_operator(row, _Util.OT_Empty.bl_idname, "Invert", False, depress=True)
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
class OT_TexPaint_ChangeBrush(bpy.types.Operator):
    bl_idname = "mpme.texpaint_change_brush"
    bl_label = "Change Brush"
    bl_options = {'REGISTER', 'UNDO'}
    brushName: bpy.props.StringProperty()
    def execute(self, context):
        context.tool_settings.image_paint.brush = bpy.data.brushes[self.brushName]
        return {'FINISHED'}
class OT_TexPaint_ToggleCtrlBehaviour(bpy.types.Operator):
    bl_idname = "mpme.texpaint_toggle_ctrl_behaviour"
    bl_label = "Toggle Ctrl Behaviour"
    bl_options = {'REGISTER', 'UNDO'}
    FIELD = "use_mesh_mirror_x"
    def execute(self, context):
        new_value = not _AddonPreferences.Accessor.GetImagePaintCtrlBehaviour()
        _AddonPreferences.Accessor.SetImagePaintCtrlBehaviour(new_value)
        global key_ctrl_lmb_erasealpha
        global key_keydown_ctrl
        global key_keyup_ctrl
        global key_ctrl_lmb_invert
        key_ctrl_lmb_erasealpha.active = new_value
        key_keydown_ctrl.active = new_value
        # key_keyup_ctrl.active = new_value
        key_ctrl_lmb_invert.active = not new_value
        return {'FINISHED'}
class OT_TexPaint_StrokeMethod(bpy.types.Operator):
    bl_idname = "mpme.texpaint_strokemethod"
    bl_label = "Change StrokeMethod"
    bl_options = {'REGISTER', 'UNDO'}
    methodName: bpy.props.StringProperty()
    @classmethod
    def getCurrent(self):
        return bpy.context.tool_settings.image_paint.brush.stroke_method
    def execute(self, context):
        context.tool_settings.image_paint.brush.stroke_method = self.methodName
        return {'FINISHED'}
class OT_TexPaint_Blend(bpy.types.Operator):
    bl_idname = "mpme.texpaint_blend"
    bl_label = "Change Blend"
    bl_options = {'REGISTER', 'UNDO'}
    methodName: bpy.props.StringProperty()
    @classmethod
    def getCurrent(self):
        return bpy.context.tool_settings.image_paint.brush.blend
    def execute(self, context):
        context.tool_settings.image_paint.brush.blend = self.methodName
        return {'FINISHED'}

# --------------------------------------------------------------------------------
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
            #name = _AddonPreferences.Accessor.GetImagePaintDefaultBrushName()
            if g_lastBrushName in bpy.data.brushes:
                context.tool_settings.image_paint.brush = bpy.data.brushes[g_lastBrushName]
            g_lastBrushName = ""
        context.window_manager.event_timer_remove(self._timer)
        return {'FINISHED'}
    def execute(self, context):
        global g_lastBrushName
        g_lastBrushName = context.tool_settings.image_paint.brush.name
        name = _AddonPreferences.Accessor.GetImagePaintShiftBrushName()
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
    OT_TexPaint_ChangeBrush,
    OT_TexPaint_StrokeMethod,
    OT_TexPaint_Blend,
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
    global key_keyup_ctrl
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    key_keydown_ctrl = km.keymap_items.new(OT_TexPaint_SwitchCtrlBehaviour.bl_idname, 'LEFT_CTRL','PRESS')
    key_keydown_ctrl.active = _AddonPreferences.Accessor.GetImagePaintCtrlBehaviour()
    addon_keymaps.append((km, key_keydown_ctrl))
    
    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    key_ctrl_lmb_erasealpha = km.keymap_items.new("paint.image_paint", 'LEFTMOUSE','PRESS', ctrl=True)
    key_ctrl_lmb_erasealpha.active = _AddonPreferences.Accessor.GetImagePaintCtrlBehaviour()
    addon_keymaps.append((km, key_ctrl_lmb_erasealpha))
    
    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    key_ctrl_lmb_invert = km.keymap_items.new("paint.image_paint", 'LEFTMOUSE','PRESS', ctrl=True)
    key_ctrl_lmb_invert.active = not _AddonPreferences.Accessor.GetImagePaintCtrlBehaviour()
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