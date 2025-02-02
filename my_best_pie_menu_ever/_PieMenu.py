if "bpy" in locals():
    import importlib
    importlib.reload(_Util)
    importlib.reload(_UtilInput)
    importlib.reload(_UtilBlf)
    importlib.reload(_AddonPreferences)
    importlib.reload(_MenuMode)
    importlib.reload(_MenuUtility)
    importlib.reload(_MenuObject)
    importlib.reload(_MenuEditMesh)
    importlib.reload(_MenuWeightPaint)
    importlib.reload(_MenuTexturePaint)
    importlib.reload(_MenuSculpt)
    importlib.reload(_MenuSculptCurve)
    importlib.reload(_MenuPose)
    importlib.reload(_MenuUVEditor)
    importlib.reload(_MenuImageEditor)
    importlib.reload(_PanelSelectionHistory)
else:
    from . import _Util
    from . import _UtilInput
    from . import _UtilBlf
    from . import _AddonPreferences
    from . import _MenuMode
    from . import _MenuUtility
    from . import _MenuObject
    from . import _MenuEditMesh
    from . import _MenuWeightPaint
    from . import _MenuTexturePaint
    from . import _MenuSculpt
    from . import _MenuSculptCurve
    from . import _MenuPose
    from . import _MenuUVEditor
    from . import _MenuImageEditor
    from . import _PanelSelectionHistory
    from . import g
import bpy
import math
from mathutils import Vector

# --------------------------------------------------------------------------------
# ルートメニュー
# --------------------------------------------------------------------------------


class VIEW3D_MT_my_pie_menu(bpy.types.Menu):
    # bl_idname = "VIEW3D_PT_my_pie_menu"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_label = f"MyBestPieMenuEver v{g.ver[0]}.{g.ver[1]}.{g.ver[2]}"

    def draw(self, context):
        # 西、東、南、北、北西、北東、南西、南東
        pie = self.layout.menu_pie()
        # 最後に選択したモード
        _MenuMode.PieMenuDraw_ChangeModeLast(pie, context)
        pie.split()
        row = pie.row()
        _MenuMode.PieMenuDraw_ChangeMode(row, context)
        _MenuUtility.PieMenuDraw_Utility(row, context)
        PieMenuDraw_Primary(pie, context)


class MPM_OT_OpenPieMenuModal(bpy.types.Operator):
    bl_idname = "mpm.open_pie_menu"
    bl_label = "My Best Pie Menu Ever"

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in {"LEFTMOUSE", "NONE"} or g.is_force_cancelled_piemenu_modal:
            if getattr(context.area.spaces.active, "image", None):
                context.area.spaces.active.image.reload()
            if event.shift or g.is_request_reopen_piemenu:
                g.is_request_reopen_piemenu = False
                if self._init_mouse_pos:
                    context.window.cursor_warp(int(self._init_mouse_pos.x), int(self._init_mouse_pos.y))
                bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_my_pie_menu")
                context.window.cursor_warp(event.mouse_x, event.mouse_y)
                return {"RUNNING_MODAL"}
            self.release(context)
            return {"FINISHED"}
        elif event.type in {"RIGHTMOUSE", "ESC"}:
            self.release(context)
            return {"CANCELLED"}
        else:
            d = math.dist(self._init_mouse_pos, Vector((event.mouse_x, event.mouse_y)))
            if 900 < d:
                context.window.screen = context.window.screen
                self.release(context)
                return {"CANCELLED"}
            # context.area.header_text_set("Offset %.4f %.4f %.4f" % tuple(self.offset))
        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        g.is_force_cancelled_piemenu_modal = False
        self._init_mouse_pos = Vector((event.mouse_x, event.mouse_y))
        # print(self._init_mouse_pos)
        safe_margin_min = (500, 450)
        safe_margin_max_y = 250
        # 左下が0,0
        self._init_mouse_pos.x = max(self._init_mouse_pos.x, safe_margin_min[0])
        self._init_mouse_pos.y = _Util.clamp(self._init_mouse_pos.y, safe_margin_min[1], context.window.height - safe_margin_max_y)
        context.scene.mpm_prop.init()
        context.window_manager.modal_handler_add(self)
        self.label_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_label, (), "WINDOW", "POST_PIXEL")
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_my_pie_menu")
        return {"RUNNING_MODAL"}

    def release(self, context):
        if self.label_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self.label_handler, "WINDOW")
            self.label_handler = None
            context.area.tag_redraw()

    def draw_label(self):
        if g.is_force_cancelled_piemenu_modal:
            return
        _UtilBlf.draw_msg(0, "Holding Shift while clicking keeps this PIE open for sequential button presses!",
                          self._init_mouse_pos.x, self._init_mouse_pos.y - 70, "center")
# --------------------------------------------------------------------------------
# モード中プライマリ処理
# --------------------------------------------------------------------------------


def PieMenuDraw_Primary(pie, context):
    if context.space_data.type == "VIEW_3D":
        current_mode = context.mode
        if current_mode == 'OBJECT':
            _MenuObject.MenuPrimary(pie, context)
        elif current_mode == 'EDIT_MESH':
            _MenuEditMesh.MenuPrimary(pie, context)
        elif current_mode == 'POSE':
            _MenuPose.MenuPrimary(pie, context)
        elif current_mode == 'SCULPT':
            _MenuSculpt.MenuPrimary(pie, context)
        elif current_mode == 'SCULPT_CURVES':
            _MenuSculptCurve.MenuPrimary(pie, context)
        elif current_mode == 'PAINT_TEXTURE':
            _MenuTexturePaint.MenuPrimary(pie, context)
        elif current_mode == 'PAINT_VERTEX':
            Placeholder(pie, context, 'No Impl')
        elif current_mode == 'PAINT_WEIGHT':
            _MenuWeightPaint.MenuPrimary(pie, context)
        elif current_mode == 'PARTICLE_EDIT':
            Placeholder(pie, context, 'No Impl')
        elif current_mode == 'EDIT_ARMATURE':
            Placeholder(pie, context, 'No Impl')
        elif current_mode == 'GPENCIL_DRAW':
            Placeholder(pie, context, 'No Impl')
        elif current_mode == 'GPENCIL_EDIT':
            Placeholder(pie, context, 'No Impl')
        elif current_mode == 'GPENCIL_SCULPT':
            Placeholder(pie, context, 'No Impl')
        elif current_mode == 'GPENCIL_WEIGHT_PAINT':
            Placeholder(pie, context, 'No Impl')
    elif context.space_data.type == "IMAGE_EDITOR":
        if context.space_data.mode == "UV":
            _MenuUVEditor.MenuPrimary(pie, context)
        else:
            _MenuImageEditor.MenuPrimary(pie, context)


def Placeholder(pie, context, text):
    box = pie.split().box()
    box.label(text=text)

# --------------------------------------------------------------------------------
# プロパティ
# context.scene.mpm_prop.IsAutoEnableWireframeOnSculptMode
# c.prop(context.scene.mpm_prop, "UVMapPopoverEnum")
# c.prop_with_popover(context.scene.mpm_prop, "ColorPalettePopoverEnum", text="", panel="MPM_PT_BrushColorPalettePanel",)
# --------------------------------------------------------------------------------


last_mode = ""


def mode_change_handler(scene):
    global last_mode
    if last_mode == bpy.context.mode:
        return
    last_mode = bpy.context.mode
    if bpy.context.active_object and scene.mpm_prop.IsAutoEnableWireframeOnSculptMode:
        bpy.context.active_object.show_wire = bpy.context.mode == "SCULPT"


class MPM_Prop(bpy.types.PropertyGroup):
    def init(self):
        self.PrevModeNameTemp = bpy.context.mode
        self.ColorPalettePopoverEnum = "ColorPalette"
        if bpy.context.tool_settings.image_paint.palette is not None:
            self.ColorPalettePopoverEnum = bpy.context.tool_settings.image_paint.palette.name
        if self.IsAutoEnableWireframeOnSculptMode:
            for i in bpy.app.handlers.depsgraph_update_pre:
                if i.__name__ == mode_change_handler.__name__:
                    # print("atta", i)
                    break
            else:
                bpy.app.handlers.depsgraph_update_pre.append(mode_change_handler)

    # 直前のモード
    PrevModeName: bpy.props.StringProperty()
    PrevModeNameTemp: bpy.props.StringProperty()

    # ビューポートカメラ位置保存スタック
    ViewportCameraTransforms: bpy.props.CollectionProperty(type=_MenuUtility.MPM_Prop_ViewportCameraTransform)

    # スカルプトモードのワイヤーフレーム
    IsAutoEnableWireframeOnSculptMode: bpy.props.BoolProperty() = False

    # テクスチャペイントのカラーパレット
    def on_update_color_palette_popover_enum(self, context):
        items = [("ColorPalette", "ColorPalette", "")]
        for i in bpy.data.palettes:
            items.append((i.name, i.name, ""))
        return items
    ColorPalettePopoverEnum: bpy.props.EnumProperty(
        name="ColorPalette Enum",
        description="Select an option",
        items=on_update_color_palette_popover_enum
    )

    # UVMap洗濯用
    def on_items_UVMapEnum(self, context):
        if context.active_object is None or context.active_object.type != "MESH":
            return [("", "", "")]
        uv_layers = context.active_object.data.uv_layers
        items = []
        if uv_layers:
            for i in uv_layers:
                items.append((i.name, i.name, ""))
        return items

    def on_set_UVMapEnum(self, value):
        uv_layers = bpy.context.active_object.data.uv_layers
        uv_layers.active = uv_layers[value]
        uv_layers.active.active_render = True

    def on_get_UVMapEnum(self):
        obj = bpy.context.active_object
        if not obj or obj.type != "MESH":
            return 0
        return obj.data.uv_layers.active_index
    UVMapPopoverEnum: bpy.props.EnumProperty(
        name="Active UVMap",
        description="Select UVMap want to be active",
        items=on_items_UVMapEnum,
        get=on_get_UVMapEnum,
        set=on_set_UVMapEnum
    )


# --------------------------------------------------------------------------------
classes = (
    VIEW3D_MT_my_pie_menu,
    MPM_OT_OpenPieMenuModal,
    MPM_Prop,
)
modules = [
    _MenuMode,
    _MenuUtility,
    _MenuObject,
    _MenuEditMesh,
    _MenuWeightPaint,
    _MenuTexturePaint,
    _MenuPose,
    _MenuSculpt,
    _MenuSculptCurve,
    _MenuUVEditor,
    _MenuImageEditor,
    _PanelSelectionHistory,
]


def register():
    for m in modules:
        m.register()
    _Util.register_classes(classes)
    bpy.types.Scene.mpm_prop = bpy.props.PointerProperty(type=MPM_Prop)


def unregister():
    for m in modules:
        m.unregister()
    _Util.unregister_classes(classes)
    del bpy.types.Scene.mpm_prop
