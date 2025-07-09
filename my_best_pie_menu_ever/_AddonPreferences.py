if "bpy" in locals():
    import importlib
    importlib.reload(_Util)
    importlib.reload(g)
else:
    from . import _Util
    from . import g
import bpy
import rna_keymap_ui
from bpy.props import IntProperty, StringProperty, BoolProperty, FloatVectorProperty
import colorsys
addon_keymaps = []


def on_update_weightPaintHideBone(self, context):
    from ._MenuWeightPaint import on_update_HideBoneOnPaint
    on_update_HideBoneOnPaint(self.weightPaintHideBone)


class MT_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    secondLanguage: StringProperty(name="Second Language", default="ja_JP", description="Set the second language for the language switch button")
    openFilePathList: StringProperty(name="Open File or Explorer Path List",
                                     description="Specify the absolute path you want to execute. You can also show multiple separated by comma.")
    imagePaintBrushFilterByName: StringProperty(name="ImagePaint Brush Filter", default="",
                                                description="Enter the name of the brush you want to display")
    imagePaintBlendFilterByName: StringProperty(name="ImagePaint Brush Blend Filter", default="",
                                                description="Enter the name of the brush you want to INCLUDE, or select it from the drop-down list")
    imagePaintShiftBrushName: StringProperty(name="Shift-key Brush", default="Blur",
                                             description="Enter the name of the brush you want to switch to while holding down the Shift key")
    image_paint_is_ctrl_behaviour_invert_or_erasealpha: BoolProperty(name="Ctrl+LMB Behaviour")
    imagePaintLimitRowCount: IntProperty(name="Limit Row Count", default=15, min=5, description="Specify the line count for displaying brushes")
    sculptLimitRowCount: IntProperty(name="Limit Row Count", default=15, min=5,
                                     description="Specify the line count for displaying brushes")
    sculptBrushFilterByName: StringProperty(name="Sculpt Brush Filter", description="Enter the name of the brush you want to display")
    weightPaintHideBone: BoolProperty(name="Weight Paint Hide Bone During Painting", description="", update=on_update_weightPaintHideBone)
    ghostColorFace: FloatVectorProperty(name="GhostColor: Face", subtype="COLOR", size=4,
                                        default=(*colorsys.hsv_to_rgb(0.65, 0.2, 0.5), 0.5), min=0.0, max=1.0, description="Colors used for Ghost display")
    ghostColorEdge: FloatVectorProperty(name="GhostColor: Edge", subtype="COLOR", size=4,
                                        default=(*colorsys.hsv_to_rgb(0.0, 0.0, 0.9), 0.5), min=0.0, max=1.0, description="Colors used for Ghost display")
    ghostColorVertex: FloatVectorProperty(name="GhostColor: Vert", subtype="COLOR", size=4,
                                          default=(*colorsys.hsv_to_rgb(0.0, 0.0, 0.9), 0.5), min=0.0, max=1.0, description="Colors used for Ghost display")

    def __get_imagepaint_brush_names(self, context):
        return [(i.name, i.name.lower(), "") for i in bpy.data.brushes if i.use_paint_image]

    # def __select_dropdown_imagepaint_filter(self, value):
    #     value = self.__get_imagepaint_brush_names(None)[value][1]
    #     if value in self.imagePaintBrushExclude:
    #         return
    #     if self.imagePaintBrushExclude:
    #         self.imagePaintBrushExclude += ', '
    #     self.imagePaintBrushExclude += value
    # imagePaintBrushNameDropDown: bpy.props.EnumProperty(
    #     name="", items=__get_imagepaint_brush_names, set=__select_dropdown_imagepaint_filter)

    def __select_dropdown_imagepaint_shift_brush(self, value):
        value = self.__get_imagepaint_brush_names(None)[value][0]
        self.imagePaintShiftBrushName = value
    imagePaintShiftBrushNameDropDown: bpy.props.EnumProperty(
        name="", items=__get_imagepaint_brush_names, set=__select_dropdown_imagepaint_shift_brush)

    def __get_blend_names(self, context):
        return [(i.lower(), i.lower(), "") for i in _Util.enum_identifier(bpy.types.Brush, "blend")]

    def __select_dropdown_blend_names(self, value):
        value = self.__get_blend_names(None)[value][1]
        if value in self.imagePaintBlendFilterByName:
            return
        if self.imagePaintBlendFilterByName:
            self.imagePaintBlendFilterByName += ', '
        self.imagePaintBlendFilterByName += value
    imagePaintBlendDropDown: bpy.props.EnumProperty(name="", items=__get_blend_names, set=__select_dropdown_blend_names)

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
            r = layout.row()
            r.prop(self, prop1)
            r.scale_x = 0.2
            r.prop(self, prop2)
        layout = self.layout
        layout.label(text="*Please Mouseover to read description.")
        c = layout.box().column(heading="Utility")
        c.prop(self, "secondLanguage")
        c.prop(self, "openFilePathList")

        c = layout.box().column(heading="EditMesh")
        c.prop(self, "ghostColorFace")
        c.prop(self, "ghostColorEdge")
        c.prop(self, "ghostColorVertex")

        c = layout.box().column(heading="Image Paint")
        c.prop(self, "imagePaintBrushFilterByName")
        sub_row(self, c, "imagePaintBlendFilterByName", "imagePaintBlendDropDown")
        c.prop(self, "imagePaintShiftBrushName")
        b = self.image_paint_is_ctrl_behaviour_invert_or_erasealpha
        r = c.row(align=True)
        r.label(text="Ctrl+LMB Behaviour:")
        r.prop(self, "image_paint_is_ctrl_behaviour_invert_or_erasealpha", text="")
        r.label(text="Invert" if not b else "EraseAlpha")
        c.prop(self, "imagePaintLimitRowCount")

        c = layout.box().column(heading="Sculpt")
        if g.is_v4_3_later():
            c.prop(self, "sculptBrushFilterByName")
        else:
            sub_row(self, c, "sculptBrushFilterByName", "sculptBrushNameDropDown")
        c.prop(self, "sculptLimitRowCount")

        c = layout.box().column(heading="Weight Paint")
        c.prop(self, "weightPaintHideBone")

        b = layout.box()
        b.label(text="Key Config")
        c = b.column()

        # 登録するときはaddonで、変更するときはuserだと上手くいく
        # では最初からuserで登録すればいいのではと思うのだが、userで登録するとキーリストの一番最後に登録される。
        # 'W'キーは既存のコマンドがあるので、最後に登録されると既存のコマンドが優先されてしまう。
        # 既存のコマンドより優先させるのは良くなさそうだが。
        # →newするときにheadオプションを使えば先頭に持ってこれるっぽい。https://docs.blender.org/api/current/bpy.types.KeyMapItems.html#bpy.types.KeyMapItems.new
        kc = bpy.context.window_manager.keyconfigs.user
        for km in kc.keymaps:
            if km.name in {"3D View", "Image"}:
                b = c.box()
                b.label(text=km.name)
                for kmi in km.keymap_items:
                    if "My Best Pie Menu Ever" in kmi.name:
                        c.context_pointer_set("keymap", kmi)
                        rna_keymap_ui.draw_kmi([], kc, km, kmi, c, 0)
                        break
        # box.operator(MPM_OT_RevertKeymap.bl_idname)

    def dict(self):
        return {
            "secondLanguage": self.secondLanguage,
            "openFilePathList": self.openFilePathList,
            # "isDebug": getattr(self, "isDebug", False),
            "imagePaintBrushFilterByName": self.imagePaintBrushFilterByName,
            "imagePaintBlendFilterByName": self.imagePaintBlendFilterByName,
            "imagePaintShiftBrushName": self.imagePaintShiftBrushName,
            "imagePaintLimitRowCount": self.imagePaintLimitRowCount,
            "image_paint_is_ctrl_behaviour_invert_or_erasealpha": self.image_paint_is_ctrl_behaviour_invert_or_erasealpha,
            "sculptLimitRowCount": self.sculptLimitRowCount,
            "sculptBrushFilterByName": self.sculptBrushFilterByName,
            "weightPaintHideBone": self.weightPaintHideBone,
            "ghostColorFace": tuple(self.ghostColorFace),  # 値コピーしないとバグるっぽい
            "ghostColorEdge": tuple(self.ghostColorEdge),  # 値コピーしないとバグるっぽい
            "ghostColorVertex": tuple(self.ghostColorVertex),  # 値コピーしないとバグるっぽい
        }

    def dict_apply(self, dict):
        for key, value in dict.items():
            setattr(self, key, value)


# class MPM_OT_RevertKeymap(bpy.types.Operator):
#     bl_idname = "mpm.revert_keymap"
#     bl_label = "Revert All Keymap"
#     bl_options = {'REGISTER', 'UNDO'}
#     # 戻し方が分からん・・・
#     def execute(self, context):
#         # register_keymap(True)
#         kc = bpy.context.window_manager.keyconfigs.addon
#         for km in kc.keymaps:
#             for kmi in km.keymap_items:
#                 print(kmi.name)
#                 if "My Best Pie Menu Ever" == kmi.name:
#                     kmi.type = "W"
#                     kmi.value = "PRESS"
#                     kmi.shift = False
#                     kmi.ctrl = False
#         return {"FINISHED"}


class Accessor():
    @staticmethod
    def get_ref(): return bpy.context.preferences.addons[__package__].preferences if __package__ in bpy.context.preferences.addons else None
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
    def get_image_paint_brush_filter_by_name(): return Accessor.get_ref().imagePaintBrushFilterByName
    @staticmethod
    def set_image_paint_brush_filter_by_name(v): Accessor.get_ref().imagePaintBrushFilterByName = v
    @staticmethod
    def get_image_paint_blend_filter_by_name(): return Accessor.get_ref().imagePaintBlendFilterByName
    @staticmethod
    def set_image_paint_blend_filter_by_name(v): Accessor.get_ref().imagePaintBlendFilterByName = v
    @staticmethod
    def get_sculpt_limit_row_count(): return Accessor.get_ref().sculptLimitRowCount
    @staticmethod
    def get_sculpt_brush_filter_by_name(): return Accessor.get_ref().sculptBrushFilterByName
    @staticmethod
    def set_sculpt_brush_filter_by_name(v): Accessor.get_ref().sculptBrushFilterByName = v
    @staticmethod
    def get_open_file_path_list(): return Accessor.get_ref().openFilePathList
    @staticmethod
    def get_weight_paint_hide_bone(): return Accessor.get_ref().weightPaintHideBone
    # @staticmethod
    # def get_is_debug(): return Accessor.get_ref().isDebug


classes = (
    MT_AddonPreferences,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
