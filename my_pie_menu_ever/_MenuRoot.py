if "bpy" in locals():
    import imp
    imp.reload(_Util)
    imp.reload(_AddonPreferences)
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
    from . import _MenuObject
    from . import _MenuEditMesh
    from . import _MenuWeightPaint
    from . import _MenuTexturePaint
    from . import _MenuSculpt
    from . import _MenuSculptCurve
    from . import _MenuPose
    from . import _PanelSelectionHistory
    from . import g
import copy
import bpy
from bpy.types import Panel, Menu, Operator
from rna_prop_ui import PropertyPanel
from bpy.app.translations import (
    pgettext_iface as iface_,
    pgettext_tip as tip_,
    contexts as i18n_contexts,
)
# --------------------------------------------------------------------------------
# ルートメニュー
# --------------------------------------------------------------------------------
class VIEW3D_MT_my_pie_menu(Menu):
    # bl_idname = "VIEW3D_PT_my_pie_menu"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_label = f"My Pie Menu v{g.ver[0]}.{g.ver[1]}"
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # 西、東、南、北、北西、北東、南西、南東
        PieMenuDraw_ObjectMode(pie, context)
        PieMenuDraw_Utility(pie, context)

        PieMenuDraw_Primary(pie, context);
        PieMenuDraw_Secondary(pie, context);

# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def PieMenuDraw_ObjectMode(pie, context):
    active = context.active_object
    object_mode = 'OBJECT' if active is None else context.mode
    active_type_is_mesh = active != None and active.type == 'MESH'
    active_type_is_armature = active != None and active.type == 'ARMATURE'
    act_mode_i18n_context = bpy.types.Object.bl_rna.properties["mode"].translation_context

    row = pie.split().row()
    box = row.box()
    _PanelSelectionHistory.PanelHistory(box, context)
    box = row.box()
    box.label(text='Mode');
    col = box.column(align = True)

    r = col.row()
    # print(object_mode)
    # print(bpy.types.Object.bl_rna.properties["mode"].enum_items[object_mode].name)
    r.active = object_mode != 'OBJECT'
    op = r.operator("object.mode_set", text=iface_('Object', act_mode_i18n_context), icon="OBJECT_DATA", depress=object_mode == 'OBJECT')
    op.mode = 'OBJECT'

    r = col.row()
    r.active = object_mode != 'EDIT_MESH'
    r.operator("object.mode_set", text=iface_('Edit', act_mode_i18n_context), icon="EDITMODE_HLT", depress=object_mode == 'EDIT_MESH').mode = 'EDIT'

    r = col.row()
    r.active = object_mode != 'SCULPT' and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_('Sculpt', act_mode_i18n_context), icon="SCULPTMODE_HLT", depress=object_mode == 'SCULPT')
    if active_type_is_mesh: op.mode = 'SCULPT'

    r = col.row()
    _Util.layout_operator(r, MPM_OT_PoseMode.bl_idname, text=iface_("Pose", act_mode_i18n_context), icon="POSE_HLT")

    r = col.row(align=True)
    r.active = object_mode != 'PAINT_WEIGHT' and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_('Weight Paint', act_mode_i18n_context), icon="WPAINT_HLT", depress=object_mode == 'PAINT_WEIGHT')
    if active_type_is_mesh: 
        op.mode = 'WEIGHT_PAINT'
        arm = _Util.get_armature(active)
        _Util.layout_operator(r, MPM_OT_WeightPaintModeWithArmature.bl_idname, "", icon="BONE_DATA")

    r = col.row()
    r.active = object_mode != 'PAINT_TEXTURE' and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_("Texture Paint", act_mode_i18n_context), icon="TPAINT_HLT", depress=object_mode == 'PAINT_TEXTURE')
    if active_type_is_mesh: op.mode = 'TEXTURE_PAINT'

class MPM_OT_WeightPaintModeWithArmature(bpy.types.Operator):
    bl_idname = "op.mpm_weight_paint_mode_with_armature"
    bl_label = "Changed Weight Paint Mode With Armature"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active != None and active.type == 'MESH' and _Util.get_armature(active) != None

    def execute(self, context):
        active = context.active_object
        _Util.get_armature(active).select_set(True)
        bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
        return {'FINISHED'}

class MPM_OT_PoseMode(bpy.types.Operator):
    bl_idname = "op.mpm_pose_mode"
    bl_label = "Changed to Pose Mode"
    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        if context.mode == "POSE":
            return False
        active = context.active_object
        return active != None and (active.type == "ARMATURE" or (active.type == 'MESH' and _Util.get_armature(active) != None))

    def execute(self, context):
        active = context.active_object
        if active.type == "MESH":
            bpy.ops.object.select_all(action='DESELECT')
            arm = _Util.get_armature(active)
            arm.select_set(True)
            context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="POSE")
        return {'FINISHED'}
# --------------------------------------------------------------------------------
# ユーティリティメニュー
# --------------------------------------------------------------------------------
def PieMenuDraw_Utility(pie, context):
    def _DrawPivot(layout):
        text = context.scene.tool_settings.transform_pivot_point
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
        layout.operator(MPM_OT_ChangePivot.bl_idname, text=text, icon=icon)
    def _DrawOrientation(layout):
        text = bpy.context.scene.transform_orientation_slots[0].type
        icon = "ORIENTATION_" + text
        layout.operator(MPM_OT_ChangeOrientations.bl_idname, text=text, icon=icon)
    
    box = pie.split().box()
    box.label(text = 'Utilities')
    row = box.row(align = True)
    row.operator("screen.userpref_show", icon='PREFERENCES', text="")
    row.operator("wm.console_toggle", icon='CONSOLE', text="")
    row.operator("import_scene.fbx", icon='IMPORT', text="")
    row.operator(MPM_OT_Utility_ChangeLanguage.bl_idname, text="", icon='FILE_FONT')

    row = box.row(align = True)
    box = row.box()
    box.label(text = 'Tool')
    c = box.column(align = True)
    # 行開始
    # from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
    # space_type, mode = ToolSelectPanelHelper._tool_key_from_context(context)
    # cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    # item, tool, _ = cls._tool_get_active(context, space_type, mode, with_icon=True)
    # if item != None:
    #     props = tool.operator_properties("view3d.cursor3d")
    #     col.prop(props, "use_depth")
    #     col.prop(props, "orientation")
    # 行開始
    r = c.row(align=True)
    _DrawPivot(r)
    _DrawOrientation(r)
    # 行開始
    # row = col.row(align=False)
    c = box.column(align = True)
    c.active = getattr(context.space_data, "overlay", None) != None
    _Util.layout_prop(c, context.space_data.overlay, "show_overlays")
    _Util.layout_prop(c, context.space_data.overlay, "show_bones", isActive=context.space_data.overlay.show_overlays)
    _Util.layout_prop(c, context.space_data.overlay, "show_wireframes", isActive=context.space_data.overlay.show_overlays)
    _Util.layout_prop(c, context.space_data.overlay, "show_annotation", isActive=context.space_data.overlay.show_overlays)
    # 行開始
    box = row.box()
    box.label(text = 'Object')
    c = box.column(align = True)
    c.active = context.object != None
    r = c.row(align = True)
    _Util.layout_prop(r, context.object, "show_in_front")
    armature = _Util.get_armature(context.object)
    _Util.OT_SetBoolToggle.operator(r, "", armature, "show_in_front", "BONE_DATA", isActive=armature!=None)

    _Util.layout_prop(c, context.object, "show_wire")
    _Util.layout_prop(c, context.object, "display_type")
    _Util.layout_operator(c, _MenuPose.MPM_OT_ClearTransform.bl_idname, isActive=_Util.is_armature_in_selected())
    _Util.layout_prop(c, context.scene, "sync_mode", text="sync_mode")

class MPM_OT_Utility_ChangeLanguage(bpy.types.Operator):
    bl_idname = "op.mpm_change_language"
    bl_label = "Change Language"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if bpy.context.preferences.view.language == "en_US":
            bpy.context.preferences.view.language = _AddonPreferences.Accessor.get_second_language()
        else:
            bpy.context.preferences.view.language = "en_US"
        return {'FINISHED'}
        
class MPM_OT_ChangePivot(bpy.types.Operator):
    bl_idname = "op.mpm_change_pivot"
    bl_label = "Change Pivot"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_pivot_pie")
        return {'FINISHED'}
    
class MPM_OT_ChangeOrientations(bpy.types.Operator):
    bl_idname = "op.mpm_change_orientations"
    bl_label = "Change Orientations"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_orientations_pie")
        return {'FINISHED'}
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

def PieMenuDraw_Secondary(pie, context):
    current_mode = context.mode
    if current_mode == 'OBJECT':                _MenuObject.MenuSecondary(pie, context)
    elif current_mode == 'EDIT_MESH':           _MenuEditMesh.MenuSecondary(pie, context)
    elif current_mode == 'POSE':                _MenuPose.MenuSecondary(pie, context)
    elif current_mode == 'SCULPT':              _MenuSculpt.MenuSecondary(pie, context)
    elif current_mode == 'SCULPT_CURVES':       _MenuSculptCurve.MenuSecondary(pie, context)
    elif current_mode == 'PAINT':               Placeholder(pie, context, 'Secondary')
    elif current_mode == 'PAINT_TEXTURE':       _MenuTexturePaint.MenuSecondary(pie, context)
    elif current_mode == 'PAINT_VERTEX':        Placeholder(pie, context, 'Secondary')
    elif current_mode == 'PAINT_WEIGHT':        _MenuWeightPaint.MenuSecondary(pie, context)
    elif current_mode == 'PARTICLE_EDIT':       Placeholder(pie, context, 'Secondary')
    elif current_mode == 'EDIT_ARMATURE':       Placeholder(pie, context, 'Secondary')
    elif current_mode == 'GPENCIL_DRAW':        Placeholder(pie, context, 'Secondary')
    elif current_mode == 'GPENCIL_EDIT':        Placeholder(pie, context, 'Secondary')
    elif current_mode == 'GPENCIL_SCULPT':      Placeholder(pie, context, 'Secondary')
    elif current_mode == 'GPENCIL_WEIGHT_PAINT':Placeholder(pie, context, 'Secondary')

def Placeholder(pie, context, text):
    box = pie.split().box()
    box.label(text = text)
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

classes = (
    VIEW3D_MT_my_pie_menu,
    MPM_OT_ChangePivot,
    MPM_OT_ChangeOrientations,
    MPM_OT_Utility_ChangeLanguage,
    MPM_OT_PoseMode,
    MPM_OT_WeightPaintModeWithArmature,
)
modules = [
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
    for m in modules:
        m.register()
def unregister():
    _Util.unregister_classes(classes)
    for m in modules:
        m.unregister()
