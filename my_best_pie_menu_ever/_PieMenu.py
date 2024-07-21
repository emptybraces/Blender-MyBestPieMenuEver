if "bpy" in locals():
    import imp
    imp.reload(_Util)
    imp.reload(_AddonPreferences)
    imp.reload(_MenuMode)
    imp.reload(_MenuUtility)
    imp.reload(_MenuObject)
    imp.reload(_MenuEditMesh)
    imp.reload(_MenuWeightPaint)
    imp.reload(_MenuTexturePaint)
    imp.reload(_MenuSculpt)
    imp.reload(_MenuSculptCurve)
    imp.reload(_MenuPose)
    imp.reload(_PanelSelectionHistory)
else:
    from . import _Util    
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
    from . import _PanelSelectionHistory
    from . import g
import bpy
from bpy.types import Panel, Menu, Operator
from rna_prop_ui import PropertyPanel
import math
from mathutils import Vector

# --------------------------------------------------------------------------------
# ルートメニュー
# --------------------------------------------------------------------------------
class VIEW3D_MT_my_pie_menu(bpy.types.Menu):
    # bl_idname = "VIEW3D_PT_my_pie_menu"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_label = f"My Pie Menu v{g.ver[0]}.{g.ver[1]}.{g.ver[2]}"
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 西、東、南、北、北西、北東、南西、南東
        pie.split()
        pie.split()
        row = pie.row()
        _MenuMode.PieMenuDraw_ModeChange(row, context)
        _MenuUtility.PieMenuDraw_Utility(row, context)
        PieMenuDraw_Primary(pie, context);
class MPM_OT_OpenPieMenu(bpy.types.Operator):
    bl_idname = "op.mpm_open_pie_menu"
    bl_label = ""
    def modal(self, context, event):
        # print(event.type)
        if event.type in {"LEFTMOUSE", "NONE"} or g.is_force_cancelled_piemenu:
            return {"FINISHED"}
        elif event.type in {"RIGHTMOUSE", "ESC"}:
            return {"CANCELLED"}
        else:
            d = math.dist(self._initial_mouse, Vector((event.mouse_x, event.mouse_y)))
            if 700 < d:
                context.window.screen = context.window.screen
                return {"FINISHED"}
            # context.area.header_text_set("Offset %.4f %.4f %.4f" % tuple(self.offset))
        return {'RUNNING_MODAL'}
    def invoke(self, context, event):
        if context.space_data.type == "VIEW_3D":
            g.is_force_cancelled_piemenu = False
            self._initial_mouse = Vector((event.mouse_x, event.mouse_y))
            context.scene.mpm_prop.init()
            context.window_manager.modal_handler_add(self)
            bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_my_pie_menu")
            return {"RUNNING_MODAL"}
        else:
            return {"CANCELLED"}

# --------------------------------------------------------------------------------
# モード中プライマリ処理
# --------------------------------------------------------------------------------
def PieMenuDraw_Primary(pie, context):
    current_mode = context.mode
    if current_mode == 'OBJECT':                _MenuObject.MenuPrimary(pie, context)
    elif current_mode == 'EDIT_MESH':           _MenuEditMesh.MenuPrimary(pie, context)
    elif current_mode == 'POSE':                _MenuPose.MenuPrimary(pie, context)
    elif current_mode == 'SCULPT':              _MenuSculpt.MenuPrimary(pie, context)
    elif current_mode == 'SCULPT_CURVES':       _MenuSculptCurve.MenuPrimary(pie, context)
    elif current_mode == 'PAINT_TEXTURE':       _MenuTexturePaint.MenuPrimary(pie, context)
    elif current_mode == 'PAINT_VERTEX':        Placeholder(pie, context, 'Primary')
    elif current_mode == 'PAINT_WEIGHT':        _MenuWeightPaint.MenuPrimary(pie, context)
    elif current_mode == 'PARTICLE_EDIT':       Placeholder(pie, context, 'Primary')
    elif current_mode == 'EDIT_ARMATURE':       Placeholder(pie, context, 'Primary')
    elif current_mode == 'GPENCIL_DRAW':        Placeholder(pie, context, 'Primary')
    elif current_mode == 'GPENCIL_EDIT':        Placeholder(pie, context, 'Primary')
    elif current_mode == 'GPENCIL_SCULPT':      Placeholder(pie, context, 'Primary')
    elif current_mode == 'GPENCIL_WEIGHT_PAINT':Placeholder(pie, context, 'Primary')
def Placeholder(pie, context, text):
    box = pie.split().box()
    box.label(text = text)

#def PieMenuDraw_Secondary(pie, context):
#    current_mode = context.mode
#    if current_mode == 'OBJECT':                _MenuObject.MenuSecondary(pie, context)
#    elif current_mode == 'EDIT_MESH':           _MenuEditMesh.MenuSecondary(pie, context)
#    elif current_mode == 'POSE':                _MenuPose.MenuSecondary(pie, context)
#    elif current_mode == 'SCULPT':              _MenuSculpt.MenuSecondary(pie, context)
#    elif current_mode == 'SCULPT_CURVES':       _MenuSculptCurve.MenuSecondary(pie, context)
#    elif current_mode == 'PAINT':               Placeholder(pie, context, 'Secondary')
#    elif current_mode == 'PAINT_TEXTURE':       _MenuTexturePaint.MenuSecondary(pie, context)
#    elif current_mode == 'PAINT_VERTEX':        Placeholder(pie, context, 'Secondary')
#    elif current_mode == 'PAINT_WEIGHT':        _MenuWeightPaint.MenuSecondary(pie, context)
#    elif current_mode == 'PARTICLE_EDIT':       Placeholder(pie, context, 'Secondary')
#    elif current_mode == 'EDIT_ARMATURE':       Placeholder(pie, context, 'Secondary')
#    elif current_mode == 'GPENCIL_DRAW':        Placeholder(pie, context, 'Secondary')
#    elif current_mode == 'GPENCIL_EDIT':        Placeholder(pie, context, 'Secondary')
#    elif current_mode == 'GPENCIL_SCULPT':      Placeholder(pie, context, 'Secondary')
#    elif current_mode == 'GPENCIL_WEIGHT_PAINT':Placeholder(pie, context, 'Secondary')

# --------------------------------------------------------------------------------
# プロパティ
# --------------------------------------------------------------------------------
class MPM_Prop_ViewportCameraTransform(bpy.types.PropertyGroup):
    pos: bpy.props.FloatVectorProperty()
    rot: bpy.props.FloatVectorProperty(size=4)
    distance: bpy.props.FloatProperty()
class MPM_Prop(bpy.types.PropertyGroup):
    def init(self):
        self.ColorPalettePopoverEnum = "ColorPalette"
        if bpy.context.tool_settings.image_paint.palette is not None:
            self.ColorPalettePopoverEnum = bpy.context.tool_settings.image_paint.palette.name
    # ビューポートカメラ位置保存スタック
    ViewportCameraTransforms: bpy.props.CollectionProperty(type=MPM_Prop_ViewportCameraTransform)
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
# --------------------------------------------------------------------------------

classes = (
    VIEW3D_MT_my_pie_menu,
    MPM_OT_OpenPieMenu,
    MPM_Prop_ViewportCameraTransform,
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
    _PanelSelectionHistory,
]
def register():
    _Util.register_classes(classes)
    bpy.types.Scene.mpm_prop = bpy.props.PointerProperty(type=MPM_Prop)
    for m in modules:
        m.register()
def unregister():
    _Util.unregister_classes(classes)
    del bpy.types.Scene.mpm_prop
    for m in modules:
        m.unregister()
