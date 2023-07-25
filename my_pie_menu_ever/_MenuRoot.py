if "bpy" in locals():
    import imp
    imp.reload(_AddonPreferences)
    imp.reload(_MenuTexturePaint)
    imp.reload(_MenuPose)
    imp.reload(_Util)
else:
    from . import _AddonPreferences
    from . import _MenuTexturePaint
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
# HT – ヘッダー
# MT – メニュー
# OT – オペレーター
# PT – パネル
# UL – UIリスト
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
    # 行開始
    row = col.row(align=False)
    _DrawPivot(row)
    _DrawOrientation(row)
    # 行開始
    row = col.row(align=False)
    r = row.row()
    r.active = getattr(context.space_data, "overlay", None) != None
    # _Util.OT_InvertValue.operator(r, "Overlay", "show_overlays", context.space_data.overlay)
    _Util.layout_prop_noneable(r, context.space_data.overlay, "show_overlays")
    # _Util.OT_InvertValue.operator(r, "Bone", "show_bones", context.space_data.overlay)
    _Util.layout_prop_noneable(r, context.space_data.overlay, "show_bones")
    # r.active =  0 < len(context.selected_objects)
    # _Util.OT_InvertValue.operator(r, "Wireframe", "show_wire", context.object)
    # _Util.OT_InvertValue.operator(r, "Front", "show_in_front", context.object)
    # _Util.OT_InvertValue.operator(r.row(), "Wireframe", "show_wireframes", context.space_data.overlay)
    _Util.layout_prop_noneable(r, context.space_data.overlay, "show_wireframes")
    # 行開始
    row = col.row(align=False)
    r = row.row()
    r.active = context.object != None
    #_Util.OT_InvertValue.operator(r, "In Front", "show_in_front", context.object)
    _Util.layout_prop_noneable(r, context.object, "show_in_front")
    # _Util.OT_InvertValue.operator(r, bpy.app.translations.pgettext("Show in Front"), "show_in_front", context.object)
    _Util.layout_prop_noneable(r, context.object, "display_type", text="", expand=False)
class OT_Utility_ChangeLanguage(bpy.types.Operator):
    bl_idname = "op.changelanguage"
    bl_label = ""
    def execute(self, context):
        if bpy.context.preferences.view.language == "ja_JP":
            bpy.context.preferences.view.language = "en_US"
        elif bpy.context.preferences.view.language == "en_US":
            bpy.context.preferences.view.language = "ja_JP"
        return {'FINISHED'}
        
class OT_ChangePivot(bpy.types.Operator):
    bl_idname = "op.pivot"
    bl_label = "Change Pivot"
    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_pivot_pie")
        return {'FINISHED'}
    
class OT_ChangeOrientations(bpy.types.Operator):
    bl_idname = "op.orientations"
    bl_label = "Change Orientations"
    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_orientations_pie")
        return {'FINISHED'}
# --------------------------------------------------------------------------------
# モード中プライマリ処理
# --------------------------------------------------------------------------------
def PieMenu_Primary(pie, context):
    current_mode = bpy.context.mode
    print(current_mode)
    if current_mode == 'OBJECT': pass
    elif current_mode == 'EDIT_MESH': pass
    elif current_mode == 'POSE': _MenuPose.MenuPrimary(pie, context)
    elif current_mode == 'SCULPT': pass
    elif current_mode == 'PAINT': pass
    elif current_mode == 'PAINT_TEXTURE': _MenuTexturePaint.MenuPrimary(pie, context)
    elif current_mode == 'PAINT_VERTEX': pass
    elif current_mode == 'PAINT_WEIGHT': pass
    elif current_mode == 'PARTICLE_EDIT': pass
    elif current_mode == 'ARMATURE': pass
    elif current_mode == 'GPENCIL_DRAW': pass
    elif current_mode == 'GPENCIL_EDIT': pass
    elif current_mode == 'GPENCIL_SCULPT': pass
    elif current_mode == 'GPENCIL_WEIGHT_PAINT': pass
def PieMenu_Secondary(pie, context):
    current_mode = bpy.context.mode
    print(current_mode, context.active_object.mode)
    if current_mode == 'OBJECT': pass
    elif current_mode == 'EDIT_MESH': pass
    elif current_mode == 'POSE': _MenuPose.MenuSecondary(pie, context)
    elif current_mode == 'SCULPT': pass
    elif current_mode == 'PAINT': pass
    elif current_mode == 'PAINT_TEXTURE': _MenuTexturePaint.MenuSecondary(pie, context)
    elif current_mode == 'PAINT_VERTEX': pass
    elif current_mode == 'PAINT_WEIGHT': pass
    elif current_mode == 'PARTICLE_EDIT': pass
    elif current_mode == 'ARMATURE': pass
    elif current_mode == 'GPENCIL_DRAW': pass
    elif current_mode == 'GPENCIL_EDIT': pass
    elif current_mode == 'GPENCIL_SCULPT': pass
    elif current_mode == 'GPENCIL_WEIGHT_PAINT': pass

# --------------------------------------------------------------------------------

classes = (
    MT_Root,
    OT_ChangePivot,
    OT_ChangeOrientations,
    OT_Utility_ChangeLanguage,
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    _MenuTexturePaint.register()
    _MenuPose.register()
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    _MenuTexturePaint.unregister()
    _MenuPose.unregister()
