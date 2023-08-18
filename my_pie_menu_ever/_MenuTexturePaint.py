import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util

# --------------------------------------------------------------------------------
# テクスチャペイントメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Texture Paint')
    col = box.column()
    row = col.row()
    mrow, msub = _Util.layout_for_mirror(row)
    _Util.layout_prop(msub, context.object, "use_mesh_mirror_x", text="X", toggle=True)
    _Util.layout_prop(msub, context.object, "use_mesh_mirror_y", text="Y", toggle=True)
    _Util.layout_prop(msub, context.object, "use_mesh_mirror_z", text="Z", toggle=True)
    # _Util.OT_SetterBase.operator(_Util.OT_SetBoolToggle.bl_idname, msub, "X", context.object, "use_mesh_mirror_x")
    # _Util.OT_SetterBase.operator(_Util.OT_SetBoolToggle.bl_idname, msub, "Y", context.object, "use_mesh_mirror_y")
    # _Util.OT_SetterBase.operator(_Util.OT_SetBoolToggle.bl_idname, msub, "Z", context.object, "use_mesh_mirror_z")
    row.operator("image.save_all_modified", text="Save All Images") 

    row = col.row() # Brush, Stroke, Blend...
    box = row.box()
    box.label(text = "Brush")

    row2 = box.row()
    col2 = row2.column()
    cnt = 0
    for i in bpy.data.brushes:
        if i.use_paint_image:
            is_use = context.tool_settings.image_paint.brush.name == i.name
            col2.operator(OT_TexturePaint_ChangeBrush.bl_idname, text=i.name, depress = is_use).brushName = i.name
            cnt += 1;
            if cnt % 12 == 0: col2 = row2.column()

    # Strokes
    cnt = 0
    box = row.box()
    box.label(text = "Stroke")
    row2 = box.row()
    col2 = row2.column()
    for i in _Util.enum_values(context.tool_settings.image_paint.brush, 'stroke_method'):
        is_use = OT_TexturePaint_StrokeMethod.getCurrent() == i
        col2.operator(OT_TexturePaint_StrokeMethod.bl_idname, text=i, depress = is_use).methodName = i

    #Blends
    cnt = 0
    box = row.box()
    box.label(text = "Blend")
    row2 = box.row()
    col2 = row2.column()
    for i in _Util.enum_values(context.tool_settings.image_paint.brush, 'blend'):
        is_use = OT_TexturePaint_Blend.getCurrent() == i
        col2.operator(OT_TexturePaint_Blend.bl_idname, text=i, depress = is_use).methodName = i    
        cnt += 1;
        if cnt % 12 == 0: col2 = row2.column()
# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    pass
# --------------------------------------------------------------------------------
class OT_TexturePaint_ChangeBrush(bpy.types.Operator):
    bl_idname = "op.texturepaint_changebrush"
    bl_label = "Change Brush"
    bl_options = {'REGISTER', 'UNDO'}
    brushName: bpy.props.StringProperty()
    def execute(self, context):
        context.tool_settings.image_paint.brush = bpy.data.brushes[self.brushName]
        return {'FINISHED'}
class OT_TexturePaint_SymmetryX(bpy.types.Operator):
    bl_idname = "op.texturepaint_symmetryx"
    bl_label = "Toggle SymmetryX"
    bl_options = {'REGISTER', 'UNDO'}
    FIELD = "use_mesh_mirror_x"
    @classmethod
    def isState(self):
        return getattr(context.object, self.FIELD)
    def execute(self, context):
        setattr(context.object, self.FIELD, not self.isState())
        return {'FINISHED'}
class OT_TexturePaint_StrokeMethod(bpy.types.Operator):
    bl_idname = "op.texturepaint_strokemethod"
    bl_label = "Change StrokeMethod"
    bl_options = {'REGISTER', 'UNDO'}
    methodName: bpy.props.StringProperty()
    @classmethod
    def getCurrent(self):
        return bpy.context.tool_settings.image_paint.brush.stroke_method
    def execute(self, context):
        context.tool_settings.image_paint.brush.stroke_method = self.methodName
        return {'FINISHED'}
class OT_TexturePaint_Blend(bpy.types.Operator):
    bl_idname = "op.texturepaint_blend"
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
class OT_ShiftEraser(bpy.types.Operator):
    bl_idname = "paint.shift_eraser"
    bl_label = "Shift Eraser"
    def execute(self, context):
        global g_lastBlend
        g_lastBlend = context.tool_settings.image_paint.brush.blend
        if g_lastBlend == 'ERASE_ALPHA': g_lastBlend = 'MIX'
        context.tool_settings.image_paint.brush.blend = 'ERASE_ALPHA'
        return {'FINISHED'}
class OT_ShiftEraserUp(bpy.types.Operator):
    bl_idname = "paint.shift_eraser_up"
    bl_label = "Shift Eraser Up"
    def execute(self, context):
        global g_lastBlend
        context.tool_settings.image_paint.brush.blend = g_lastBlend
        return {'FINISHED'}
# --------------------------------------------------------------------------------

classes = (
    OT_TexturePaint_ChangeBrush,
    OT_TexturePaint_SymmetryX,
    OT_TexturePaint_StrokeMethod,
    OT_TexturePaint_Blend,
    OT_ShiftEraser,
    OT_ShiftEraserUp,
)

addon_keymaps = []
def register():
    _Util.register_classes(classes)
    # Keymaps
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    kmi = km.keymap_items.new("paint.shift_eraser", 'LEFT_SHIFT','PRESS')
    addon_keymaps.append(km)
    
    km2 = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    kmi2 = km2.keymap_items.new("paint.image_paint", 'LEFTMOUSE','PRESS', shift=True)
    addon_keymaps.append(km2)
    
    km3 = wm.keyconfigs.addon.keymaps.new(name='Image Paint', space_type='EMPTY')
    kmi3 = km3.keymap_items.new("paint.shift_eraser_up", 'LEFT_SHIFT','RELEASE', shift=True)
def unregister():
    _Util.unregister_classes(classes)
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]