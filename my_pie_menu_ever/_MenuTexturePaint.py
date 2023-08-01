import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util

# --------------------------------------------------------------------------------
# テクスチャペイントメニュー
# --------------------------------------------------------------------------------
# class MT_TexturePaint(Menu):
#     bl_idname = PREID + "_MT_TexturePaint"
#     bl_label = "TexturePaint Menu"
#     @classmethod
#     def poll(cls, context):
#         return context.mode == "PAINT_TEXTURE"
#     def draw(self, context):
#         layout = self.layout
#         row =layout.row(align=False)
#         row.operator("image.save_all_modified", text="Save All Images")
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

    row = col.row()
    box = row.box()
    rowinbox = box.row()
    col2 = rowinbox.column()
    col2.label(text = "Brushes")
    cnt = 0
    for i in bpy.data.brushes:
        if i.use_paint_image:
            is_use = context.tool_settings.image_paint.brush.name == i.name
            col2.operator(OT_TexturePaint_ChangeBrush.bl_idname, text=i.name, depress = is_use).brushName = i.name
            cnt += 1;
            if cnt == 10:
                 col2 = rowinbox.column()
            # print(dir(i))
    col2 = row.box().column()
    col2.label(text = "Stroke")
    for i in _Util.enum_values(context.tool_settings.image_paint.brush, 'stroke_method'):
        is_use = OT_TexturePaint_StrokeMethod.getCurrent() == i
        col2.operator(OT_TexturePaint_StrokeMethod.bl_idname, text=i, depress = is_use).methodName = i
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
    bl_label = "Change Display Type"
    bl_options = {'REGISTER', 'UNDO'}
    methodName: bpy.props.StringProperty()
    @classmethod
    def getCurrent(self):
        return bpy.context.tool_settings.image_paint.brush.stroke_method
    def execute(self, context):
        context.tool_settings.image_paint.brush.stroke_method = self.methodName
        return {'FINISHED'}
# class OT_TexturePaint_StrokeMethodList(bpy.types.Operator):
#     bl_idname = "op.texturepaint_strokemethodlist"
#     bl_label = "Change Display Type"
#     def items(self, context):
#         values = enum_values(context.tool_settings.image_paint.brush, 'stroke_method')
#         return [(value, value, "") for value in values]
#     item: bpy.props.EnumProperty(items = items, name = "description")
#     def execute(self, context):
#         show_enum_values(context.tool_settings.image_paint.brush, 'stroke_method')
#         context.tool_settings.image_paint.stroke_method = self.item
#         return {'FINISHED'}

# --------------------------------------------------------------------------------

classes = (
    # MT_TexturePaint,
    OT_TexturePaint_ChangeBrush,
    OT_TexturePaint_SymmetryX,
    OT_TexturePaint_StrokeMethod,
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)