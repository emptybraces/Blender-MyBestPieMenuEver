if "bpy" in locals():
    import imp
    imp.reload(_AddonPreferences)
    imp.reload(_MenuObject)
    imp.reload(_MenuEditMesh)
    imp.reload(_MenuWeightPaint)
    imp.reload(_MenuTexturePaint)
    imp.reload(_MenuSculptCurve)
    imp.reload(_MenuPose)
    imp.reload(_Util)
else:
    from . import _AddonPreferences
    from . import _MenuObject
    from . import _MenuEditMesh
    from . import _MenuWeightPaint
    from . import _MenuTexturePaint
    from . import _MenuSculptCurve
    from . import _MenuPose
    from . import _Util
import copy
import bpy
from bpy.types import Panel, Menu, Operator
from rna_prop_ui import PropertyPanel
from bpy.app.translations import (
    pgettext_iface as iface_,
    pgettext_tip as tip_,
    contexts as i18n_contexts,
)
PREID = "MYPIEMENUEVER"

# --------------------------------------------------------------------------------
# ルートメニュー
# --------------------------------------------------------------------------------
class MT_Root(Menu):
    bl_idname = PREID + "_MT_Root"
    bl_label = ""
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 西、東、南、北、北西、北東、南西、南東
        PieMenu_ObjectMode(pie, context)
        PieMenu_Utility(pie, context)

        PieMenu_Primary(pie, context);
        PieMenu_Secondary(pie, context);

# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def PieMenu_ObjectMode(pie, context):
    active = context.active_object
    object_mode = 'OBJECT' if active is None else active.mode
    active_type_is_mesh = active != None and active.type == 'MESH'
    active_type_is_armature = active != None and active.type == 'ARMATURE'
    act_mode_i18n_context = bpy.types.Object.bl_rna.properties["mode"].translation_context

    box = pie.split().box()
    box.label(text='Mode');
    col = box.column()
    row = col.row(align=False)

    r = row.row()
    # print(object_mode)
    # print(bpy.types.Object.bl_rna.properties["mode"].enum_items[object_mode].name)
    r.active = object_mode != 'OBJECT'
    r.operator("object.mode_set", text=iface_('Object', act_mode_i18n_context), icon="OBJECT_DATA", depress=object_mode == 'OBJECT').mode = 'OBJECT'

    r = row.row()
    r.active = object_mode != 'EDIT'
    r.operator("object.mode_set", text=iface_('Edit', act_mode_i18n_context), icon="EDITMODE_HLT", depress=object_mode == 'EDIT').mode = 'EDIT'

    r = row.row()
    r.active = object_mode != 'SCULPT' and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_('Sculpt', act_mode_i18n_context), icon="SCULPTMODE_HLT", depress=object_mode == 'SCULPT')
    if active_type_is_mesh: op.mode = 'SCULPT'

    r = row.row()
    r.active = object_mode != 'POSE' and active_type_is_armature
    op = r.operator("object.mode_set", text=iface_("Pose", act_mode_i18n_context), icon='POSE_HLT', depress=object_mode == 'POSE')
    if active_type_is_armature: op.mode = 'POSE'

    row = col.row(align=False)
    r = row.row()
    r.active = object_mode != 'WEIGHT_PAINT' and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_('Weight Paint', act_mode_i18n_context), icon="WPAINT_HLT", depress=object_mode == 'WEIGHT_PAINT')
    if active_type_is_mesh: op.mode = 'WEIGHT_PAINT'

    r = row.row()
    r.active = object_mode != 'TEXTURE_PAINT' and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_("Texture Paint", act_mode_i18n_context), icon="TPAINT_HLT", depress=object_mode == 'TEXTURE_PAINT')
    if active_type_is_mesh: op.mode = 'TEXTURE_PAINT'

# --------------------------------------------------------------------------------
# ユーティリティメニュー
# --------------------------------------------------------------------------------
def PieMenu_Utility(pie, context):
    def _DrawPivot(layout):
        text = bpy.context.scene.tool_settings.transform_pivot_point
        if text == 'ACTIVE_ELEMENT':
            text = "Active"
            icon = "PIVOT_ACTIVE"
        elif text == 'BOUNDING_BOX_CENTER':
            text = "BoundingBox"
            icon = "PIVOT_BOUNDBOX"
        elif text == 'CURSOR':
            text = "Cursor"
            icon = "PIVOT_CURSOR"
        elif text == 'INDIVIDUAL_ORIGINS':
            text = "Origin"
            icon = "PIVOT_INDIVIDUAL"
        elif text == 'MEDIAN_POINT':
            text = "Median"
            icon = "PIVOT_MEDIAN"
        layout.operator(OT_ChangePivot.bl_idname, text=text, icon=icon)
    def _DrawOrientation(layout):
        text = bpy.context.scene.transform_orientation_slots[0].type
        icon = "ORIENTATION_" + text
        layout.operator(OT_ChangeOrientations.bl_idname, text=text, icon=icon)
    box = pie.split().box()
    box.label(text = 'Utilities')
    col = box.column()
    # 行開始
    col.operator(OT_Utility_ChangeLanguage.bl_idname, text="Change Language")
    # from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
    # space_type, mode = ToolSelectPanelHelper._tool_key_from_context(context)
    # cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    # item, tool, _ = cls._tool_get_active(context, space_type, mode, with_icon=True)
    # if item != None:
    #     props = tool.operator_properties("view3d.cursor3d")
    #     col.prop(props, "use_depth")
    #     col.prop(props, "orientation")
    # 行開始
    row = col.row(align=False)
    _DrawPivot(row)
    _DrawOrientation(row)
    # 行開始
    row = col.row(align=False)
    r = row.row()
    r.active = getattr(context.space_data, "overlay", None) != None
    _Util.layout_prop(r, context.space_data.overlay, "show_overlays")
    _Util.layout_prop(r, context.space_data.overlay, "show_bones")
    _Util.layout_prop(r, context.space_data.overlay, "show_wireframes")
    # 行開始
    row = col.row(align=False)
    r = row.row()
    r.active = context.object != None
    _Util.layout_prop(r, context.object, "show_in_front")
    _Util.layout_prop(r, context.object, "show_wire")
    _Util.layout_prop(r, context.object, "display_type", text="", expand=False)
class OT_Utility_ChangeLanguage(bpy.types.Operator):
    bl_idname = "op.changelanguage"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if bpy.context.preferences.view.language == "en_US":
            bpy.context.preferences.view.language = _AddonPreferences.Accessor.GetSecondLanguage()
        else:
            bpy.context.preferences.view.language = "en_US"
        return {'FINISHED'}
        
class OT_ChangePivot(bpy.types.Operator):
    bl_idname = "op.pivot"
    bl_label = "Change Pivot"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_pivot_pie")
        return {'FINISHED'}
    
class OT_ChangeOrientations(bpy.types.Operator):
    bl_idname = "op.orientations"
    bl_label = "Change Orientations"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_orientations_pie")
        return {'FINISHED'}
# --------------------------------------------------------------------------------
# モード中プライマリ処理
# --------------------------------------------------------------------------------
def PieMenu_Primary(pie, context):
    current_mode = bpy.context.mode
    
    if current_mode == 'OBJECT':                _MenuObject.MenuPrimary(pie, context)
    elif current_mode == 'EDIT_MESH':           _MenuEditMesh.MenuPrimary(pie, context)
    elif current_mode == 'POSE':                _MenuPose.MenuPrimary(pie, context)
    elif current_mode == 'SCULPT':              Placeholder(pie, context, 'Primary')
    elif current_mode == 'SCULPT_CURVES':       _MenuSculptCurve.MenuPrimary(pie, context)
    elif current_mode == 'PAINT':               Placeholder(pie, context, 'Primary')
    elif current_mode == 'PAINT_TEXTURE':       _MenuTexturePaint.MenuPrimary(pie, context)
    elif current_mode == 'PAINT_VERTEX':        Placeholder(pie, context, 'Primary')
    elif current_mode == 'PAINT_WEIGHT':        _MenuWeightPaint.MenuPrimary(pie, context)
    elif current_mode == 'PARTICLE_EDIT':       Placeholder(pie, context, 'Primary')
    elif current_mode == 'ARMATURE':            Placeholder(pie, context, 'Primary')
    elif current_mode == 'GPENCIL_DRAW':        Placeholder(pie, context, 'Primary')
    elif current_mode == 'GPENCIL_EDIT':        Placeholder(pie, context, 'Primary')
    elif current_mode == 'GPENCIL_SCULPT':      Placeholder(pie, context, 'Primary')
    elif current_mode == 'GPENCIL_WEIGHT_PAINT':Placeholder(pie, context, 'Primary')
def PieMenu_Secondary(pie, context):
    current_mode = bpy.context.mode
    if current_mode == 'OBJECT':                _MenuObject.MenuSecondary(pie, context)
    elif current_mode == 'EDIT_MESH':           _MenuEditMesh.MenuSecondary(pie, context)
    elif current_mode == 'POSE':                _MenuPose.MenuSecondary(pie, context)
    elif current_mode == 'SCULPT':              Placeholder(pie, context, 'Secondary')
    elif current_mode == 'SCULPT_CURVES':       _MenuSculptCurve.MenuSecondary(pie, context)
    elif current_mode == 'PAINT':               Placeholder(pie, context, 'Secondary')
    elif current_mode == 'PAINT_TEXTURE':       _MenuTexturePaint.MenuSecondary(pie, context)
    elif current_mode == 'PAINT_VERTEX':        Placeholder(pie, context, 'Secondary')
    elif current_mode == 'PAINT_WEIGHT':        _MenuWeightPaint.MenuSecondary(pie, context)
    elif current_mode == 'PARTICLE_EDIT':       Placeholder(pie, context, 'Secondary')
    elif current_mode == 'ARMATURE':            Placeholder(pie, context, 'Secondary')
    elif current_mode == 'GPENCIL_DRAW':        Placeholder(pie, context, 'Secondary')
    elif current_mode == 'GPENCIL_EDIT':        Placeholder(pie, context, 'Secondary')
    elif current_mode == 'GPENCIL_SCULPT':      Placeholder(pie, context, 'Secondary')
    elif current_mode == 'GPENCIL_WEIGHT_PAINT':Placeholder(pie, context, 'Secondary')
def Placeholder(pie, context, text):
    box = pie.split().box()
    box.label(text = text)
# --------------------------------------------------------------------------------

classes = (
    MT_Root,
    OT_ChangePivot,
    OT_ChangeOrientations,
    OT_Utility_ChangeLanguage,
)
modules = (
    _MenuObject,
    _MenuEditMesh,
    _MenuWeightPaint,
    _MenuTexturePaint,
    _MenuPose,
    _MenuSculptCurve,
)
def register():
    _Util.register_classes(classes)
    for m in modules:
        m.register()
def unregister():
    _Util.unregister_classes(classes)
    for m in modules:
        m.unregister()
