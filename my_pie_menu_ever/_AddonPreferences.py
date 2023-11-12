import bpy
import rna_keymap_ui
from rna_prop_ui import PropertyPanel
from bpy.props import IntProperty, IntVectorProperty, StringProperty, BoolProperty
from . import _Util
from . import _MenuRoot

addon_keymaps = []
class MT_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    secondLanguage: StringProperty(name="Second Language", default="ja_JP")
    isDebug: BoolProperty(name="Debug Mode")
    imagePaintBrushExclude: StringProperty(name="Brush Exclude", default="", description="Specify by comma separated.")
    imagePaintBlendInclude: StringProperty(name="Blend Include", default="mix,screen,overlay,erase_alpha", description="Specify by comma separated.")
    imagePaintShiftBrushName: StringProperty(name="ShiftBrushName", default="Soften")
    image_paint_is_ctrl_behaviour_invert_or_erasealpha: BoolProperty()
    imagePaintLimitRowCount: IntProperty(name="Limit Row Count", default=13, min=5)
    sculptLimitRowCount: IntProperty(name="Limit Row Count", default=13, min=5)
    sculptBrushFilterByName: StringProperty(name="Filter by brush name")

    def __get_imagepaint_brush_names(self, context):
        return [(i.name, i.name.lower(), "") for i in bpy.data.brushes if i.use_paint_image]
    def __select_dropdown_imagepaint_filter(self, value):
        value = self.__get_imagepaint_brush_names(None)[value][1]
        if value in self.imagePaintBrushExclude: return
        if self.imagePaintBrushExclude:
            self.imagePaintBrushExclude += ', '
        self.imagePaintBrushExclude += value
    imagePaintBrushNameDropDown: bpy.props.EnumProperty(name="", items=__get_imagepaint_brush_names, set=__select_dropdown_imagepaint_filter)
    def __select_dropdown_imagepaint_shift_brush(self, value):
        value = self.__get_imagepaint_brush_names(None)[value][0]
        self.imagePaintShiftBrushName = value
    imagePaintShiftBrushNameDropDown: bpy.props.EnumProperty(name="", items=__get_imagepaint_brush_names, set=__select_dropdown_imagepaint_shift_brush)
    def __get_blend_names(self, context):
        return [(i.lower(), i.lower(), "") for i in _Util.enum_values(bpy.context.tool_settings.image_paint.brush, 'blend')]
    def __select_dropdown_blend_names(self, value):
        value = self.__get_blend_names(None)[value][1]
        if value in self.imagePaintBlendInclude: return
        if self.imagePaintBlendInclude: self.imagePaintBlendInclude += ', '
        self.imagePaintBlendInclude += value
    imagePaintBlendDropDown: bpy.props.EnumProperty(name="", items=__get_blend_names, set=__select_dropdown_blend_names)
    def __get_sculpt_brush_names(self, context):
        return [(i.name.lower(), i.name.lower(), "") for i in bpy.data.brushes if i.use_paint_sculpt]
    def __select_dropdown_sclupt_brush_filter(self, value):
        value = self.__get_sculpt_brush_names(None)[value][1]
        if value in self.sculptBrushFilterByName: return
        if self.sculptBrushFilterByName:
            self.sculptBrushFilterByName += ', '
        self.sculptBrushFilterByName += value
    sculptBrushNameDropDown: bpy.props.EnumProperty(name="", items=__get_sculpt_brush_names, set=__select_dropdown_sclupt_brush_filter)
    def draw(self, context):
        def sub_row(self, layout, prop1, prop2):
            row = layout.row()
            row.prop(self, prop1)
            row.scale_x = 0.2
            row.prop(self, prop2)
        global blends
        layout = self.layout
        box = layout.box().column(heading='Utility')
        box.prop(self, "secondLanguage")
        box.prop(self, "isDebug")

        box = layout.box()
        box.label(text='Image Paint')
        sub_row(self, box, "imagePaintBrushExclude", "imagePaintBrushNameDropDown")
        sub_row(self, box, "imagePaintBlendInclude", "imagePaintBlendDropDown")
        sub_row(self, box, "imagePaintShiftBrushName", "imagePaintShiftBrushNameDropDown")
        b = self.image_paint_is_ctrl_behaviour_invert_or_erasealpha
        box.prop(self, "image_paint_is_ctrl_behaviour_invert_or_erasealpha", text="ImagePaint: Ctrl+LMB - " + ("Invert" if not b else "EraseAlpha"))
        box.prop(self, "imagePaintLimitRowCount")
        
        box = layout.box()
        box.label(text='Sculpt')
        sub_row(self, box, "sculptBrushFilterByName", "sculptBrushNameDropDown")
        box.prop(self, "sculptLimitRowCount")

        box = layout.box()
        box.label(text="KeyConfig")
        kc = context.window_manager.keyconfigs.user
        km = kc.keymaps['3D View']
        for keymaps in addon_keymaps:
            box.context_pointer_set("keymap", keymaps[1])
            rna_keymap_ui.draw_kmi([], kc, km, keymaps[1], box, 0)

    def dict(self):
        return {
            "secondLanguage": self.secondLanguage,
            "isDebug": getattr(self, "isDebug", False),
            "imagePaintBrushExclude": self.imagePaintBrushExclude,
            "imagePaintBlendInclude": self.imagePaintBlendInclude,
            "imagePaintShiftBrushName": self.imagePaintShiftBrushName,
            "imagePaintLimitRowCount": self.imagePaintLimitRowCount,
            "image_paint_is_ctrl_behaviour_invert_or_erasealpha": self.image_paint_is_ctrl_behaviour_invert_or_erasealpha,
            "sculptLimitRowCount": self.sculptLimitRowCount,
            "sculptBrushFilterByName": self.sculptBrushFilterByName,
        }
    def dict_apply(self, dict):
        for key, value in dict.items(): 
            setattr(self, key, value)

class Accessor():
    @staticmethod
    def get_ref(): return bpy.context.preferences.addons[__package__].preferences
    @staticmethod
    def get_second_language(): return Accessor.get_ref().secondLanguage
    @staticmethod
    def get_image_paint_ctrl_behaviour(): return Accessor.get_ref().image_paint_is_ctrl_behaviour_invert_or_erasealpha
    @staticmethod
    def set_image_paint_ctrl_behaviour(v): Accessor.get_ref().image_paint_is_ctrl_behaviour_invert_or_erasealpha = v
    @staticmethod
    def get_image_paint_shift_brush_name(): return Accessor.get_ref().imagePaintShiftBrushName
    @staticmethod
    def get_image_paint_limit_row(): return Accessor.get_ref().imagePaintLimitRowCount
    @staticmethod
    def get_image_paint_brush_exclude(): return Accessor.get_ref().imagePaintBrushExclude
    @staticmethod
    def get_image_paint_blend_include(): return Accessor.get_ref().imagePaintBlendInclude
    @staticmethod
    def get_sculpt_limit_row_count(): return Accessor.get_ref().sculptLimitRowCount
    @staticmethod
    def get_sculpt_brush_filter_by_name(): return Accessor.get_ref().sculptBrushFilterByName
    @staticmethod
    def get_is_debug(): return Accessor.get_ref().isDebug

def registerKeyMap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS')
        kmi.properties.name = "VIEW3D_MT_my_pie_menu"
        addon_keymaps.append((km, kmi))
        
def unregisterKeyMap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

classes = (
    MT_AddonPreferences,
)
    
def register():
    _Util.register_classes(classes)
    registerKeyMap()
    
def unregister():
    _Util.unregister_classes(classes)
    unregisterKeyMap()
