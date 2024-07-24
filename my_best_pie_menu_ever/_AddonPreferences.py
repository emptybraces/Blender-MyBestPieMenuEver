import bpy
import rna_keymap_ui
from bpy.props import IntProperty, StringProperty, BoolProperty
from . import _Util
addon_keymaps = []


class MT_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    secondLanguage: StringProperty(name="Second Language", default="ja_JP",
                                   description="Set the second language for the language switch button")
    openFilePathList: StringProperty(name="Open File or Explorer Path List",
                                     description="Specify the absolute path you want to execute. You can also show multiple separated by comma.")
    imagePaintBrushExclude: StringProperty(
        name="Brush Exclude", default="", description="Enter the name of the brush you want to EXCLUDE, or select it from the drop-down list")
    imagePaintBlendInclude: StringProperty(name="Blend Include", default="mix,screen,overlay,erase_alpha",
                                           description="Enter the name of the brush you want to INCLUDE, or select it from the drop-down list")
    imagePaintShiftBrushName: StringProperty(name="ShiftBrushName", default="Soften",
                                             description="Enter the name of the brush you want to switch to while holding down the Shift key")
    image_paint_is_ctrl_behaviour_invert_or_erasealpha: BoolProperty(
        name="Ctrl+LMB Behaviour")
    imagePaintLimitRowCount: IntProperty(
        name="Limit Row Count", default=13, min=5, description="Specify the line count for displaying brushes")
    sculptLimitRowCount: IntProperty(name="Limit Row Count", default=13,
                                     min=5, description="Specify the line count for displaying brushes")
    sculptBrushFilterByName: StringProperty(
        name="Filter by brush name", description="Enter the name of the brush you want to display or select from the drop-down list")

    def __get_imagepaint_brush_names(self, context):
        return [(i.name, i.name.lower(), "") for i in bpy.data.brushes if i.use_paint_image]

    def __select_dropdown_imagepaint_filter(self, value):
        value = self.__get_imagepaint_brush_names(None)[value][1]
        if value in self.imagePaintBrushExclude:
            return
        if self.imagePaintBrushExclude:
            self.imagePaintBrushExclude += ', '
        self.imagePaintBrushExclude += value
    imagePaintBrushNameDropDown: bpy.props.EnumProperty(
        name="", items=__get_imagepaint_brush_names, set=__select_dropdown_imagepaint_filter)

    def __select_dropdown_imagepaint_shift_brush(self, value):
        value = self.__get_imagepaint_brush_names(None)[value][0]
        self.imagePaintShiftBrushName = value
    imagePaintShiftBrushNameDropDown: bpy.props.EnumProperty(
        name="", items=__get_imagepaint_brush_names, set=__select_dropdown_imagepaint_shift_brush)

    def __get_blend_names(self, context):
        return [(i.lower(), i.lower(), "") for i in _Util.enum_values(bpy.context.tool_settings.image_paint.brush, 'blend')]

    def __select_dropdown_blend_names(self, value):
        value = self.__get_blend_names(None)[value][1]
        if value in self.imagePaintBlendInclude:
            return
        if self.imagePaintBlendInclude:
            self.imagePaintBlendInclude += ', '
        self.imagePaintBlendInclude += value
    imagePaintBlendDropDown: bpy.props.EnumProperty(
        name="", items=__get_blend_names, set=__select_dropdown_blend_names)

    def __get_sculpt_brush_names(self, context):
        return [(i.name.lower(), i.name.lower(), "") for i in bpy.data.brushes if i.use_paint_sculpt]

    def __select_dropdown_sclupt_brush_filter(self, value):
        value = self.__get_sculpt_brush_names(None)[value][1]
        if value in self.sculptBrushFilterByName:
            return
        if self.sculptBrushFilterByName:
            self.sculptBrushFilterByName += ', '
        self.sculptBrushFilterByName += value
    sculptBrushNameDropDown: bpy.props.EnumProperty(
        name="", items=__get_sculpt_brush_names, set=__select_dropdown_sclupt_brush_filter)

    def draw(self, context):
        def sub_row(self, layout, prop1, prop2):
            row = layout.row()
            row.prop(self, prop1)
            row.scale_x = 0.2
            row.prop(self, prop2)
        global blends
        layout = self.layout
        layout.label(text="*Please Mouseover to read description.")
        box = layout.box().column(heading='Utility')
        box.prop(self, "secondLanguage")
        box.prop(self, "openFilePathList")

        box = layout.box()
        box.label(text='Image Paint')
        sub_row(self, box, "imagePaintBrushExclude",
                "imagePaintBrushNameDropDown")
        sub_row(self, box, "imagePaintBlendInclude", "imagePaintBlendDropDown")
        sub_row(self, box, "imagePaintShiftBrushName",
                "imagePaintShiftBrushNameDropDown")
        b = self.image_paint_is_ctrl_behaviour_invert_or_erasealpha
        row = box.row(align=True)
        row.label(text="Ctrl+LMB Behaviour:")
        row.prop(self, "image_paint_is_ctrl_behaviour_invert_or_erasealpha", text="")
        row.label(text="Invert" if not b else "EraseAlpha")

        box.prop(self, "imagePaintLimitRowCount")

        box = layout.box()
        box.label(text='Sculpt')
        sub_row(self, box, "sculptBrushFilterByName",
                "sculptBrushNameDropDown")
        box.prop(self, "sculptLimitRowCount")

        box = layout.box()
        box.label(text="KeyConfig")

        kc = bpy.context.window_manager.keyconfigs.user
        for km in kc.keymaps:
            for kmi in km.keymap_items:
                if "My Best Pie Menu Ever" in kmi.name:
                    box.context_pointer_set("keymap", kmi)
                    rna_keymap_ui.draw_kmi([], kc, km, kmi, box, 0)
                    break
        # box.operator(MPM_OT_RevertKeymap.bl_idname)

    def dict(self):
        return {
            "secondLanguage": self.secondLanguage,
            "openFilePathList": self.openFilePathList,
            # "isDebug": getattr(self, "isDebug", False),
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


class MPM_OT_RevertKeymap(bpy.types.Operator):
    bl_idname = "op.mpm_revert_keymap"
    bl_label = "Revert All Keymap"
    bl_options = {'REGISTER', 'UNDO'}
    # 戻し方が分からん・・・
    def execute(self, context):
        # register_keymap(True)
        kc = bpy.context.window_manager.keyconfigs.addon
        for km in kc.keymaps:
            for kmi in km.keymap_items:
                print(kmi.name)
                if "My Best Pie Menu Ever" is kmi.name:
                    kmi.type = "W"
                    kmi.value = "PRESS"
                    kmi.shift = False
                    kmi.ctrl = False
        return {"FINISHED"}


class Accessor():
    @staticmethod
    def get_ref(
    ): return bpy.context.preferences.addons[__package__].preferences if __package__ in bpy.context.preferences.addons else None
    @staticmethod
    def get_second_language(): return Accessor.get_ref().secondLanguage
    @staticmethod
    def get_image_paint_ctrl_behaviour(): return Accessor.get_ref(
    ).image_paint_is_ctrl_behaviour_invert_or_erasealpha
    @staticmethod
    def set_image_paint_ctrl_behaviour(v): Accessor.get_ref(
    ).image_paint_is_ctrl_behaviour_invert_or_erasealpha = v
    @staticmethod
    def get_image_paint_shift_brush_name(
    ): return Accessor.get_ref().imagePaintShiftBrushName
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
    def get_open_file_path_list(): return Accessor.get_ref().openFilePathList
    # @staticmethod
    # def get_is_debug(): return Accessor.get_ref().isDebug


def find_keymap(keymapName, itemName):
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.get(keymapName)
    kmi = km.keymap_items.get(itemName) if km is not None else None
    return (km, kmi)


def register_keymap(is_force):
    kmkmi = find_keymap(
        "3D View", "op.mpm_open_pie_menu") if not is_force else (None, None)
    if kmkmi[1] == None:
        kc = bpy.context.window_manager.keyconfigs.addon
        km = kc.keymaps.get("3D View")
        kmi = km.keymap_items.get("op.mpm_open_pie_menu")
        if not kmi:
            kmi = km.keymap_items.new("op.mpm_open_pie_menu", "W", "PRESS")
            # print("登録したよ")
        else:
            kmi.type = "W"
            kmi.value = "PRESS"
            kmi.shift = False
            kmi.ctrl = False
    else:
        # print("登録しないよ")
        pass


def unregister_keymap():
    kmkmi = find_keymap("3D View", "op.mpm_open_pie_menu")
    if kmkmi[1] is not None:
        kmkmi[0].keymap_items.remove(kmkmi[1])


classes = (
    MT_AddonPreferences,
    MPM_OT_RevertKeymap,
)


def register():
    _Util.register_classes(classes)
    register_keymap(False)


def unregister():
    _Util.unregister_classes(classes)
    unregister_keymap()
