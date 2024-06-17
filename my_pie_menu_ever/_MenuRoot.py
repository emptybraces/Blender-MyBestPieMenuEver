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
        PieMenuDraw_ObjectMode(row, context)
        PieMenuDraw_Utility(row, context)
        PieMenuDraw_Primary(pie, context);
class MPM_OT_OpenPieMenu(bpy.types.Operator):
    bl_idname = "op.mpm_open_pie_menu"
    bl_label = ""
    def modal(self, context, event):
        if event.type in {"LEFTMOUSE", "NONE"}:
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
            self._initial_mouse = Vector((event.mouse_x, event.mouse_y))
            context.window_manager.modal_handler_add(self)
            bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_my_pie_menu")
            return {"RUNNING_MODAL"}
        else:
            return {"CANCELLED"}

# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def PieMenuDraw_ObjectMode(layout, context):
    active = context.active_object
    object_mode = "OBJECT" if active is None else context.mode
    active_type_is_mesh = active != None and active.type == "MESH"
    active_type_is_armature = active != None and active.type == "ARMATURE"
    act_mode_i18n_context = bpy.types.Object.bl_rna.properties["mode"].translation_context

    #_PanelSelectionHistory.PanelHistory(box, context)

    box = layout.box()
    box.label(text="Mode");
    col = box.column(align = True)

    # Object
    r = col.row()
    # print(object_mode)
    # print(bpy.types.Object.bl_rna.properties["mode"].enum_items[object_mode].name)
    r.active = object_mode != "OBJECT"
    op = r.operator("object.mode_set", text=iface_("Object", act_mode_i18n_context), icon="OBJECT_DATA", depress=object_mode == "OBJECT")
    op.mode = "OBJECT"

    # Edit
    r = col.row(align=True)
    r.active = object_mode != "EDIT_MESH" and active_type_is_mesh or active_type_is_armature
    depress_comp = "EDIT_MESH" if active_type_is_mesh else "EDIT_ARMATURE"
    op = r.operator("object.mode_set", text=iface_("Edit", act_mode_i18n_context), icon="EDITMODE_HLT", depress=object_mode == depress_comp)
    if active_type_is_mesh or active_type_is_armature: op.mode = "EDIT"
    if active_type_is_mesh: 
        arm = _Util.get_armature(active)
        _Util.layout_operator(r, MPM_OT_ChangeModeWithArmature.bl_idname, "", icon="BONE_DATA").mode = "EDIT"

    # Sculpt
    r = col.row()
    r.active = object_mode != "SCULPT" and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_("Sculpt", act_mode_i18n_context), icon="SCULPTMODE_HLT", depress=object_mode == "SCULPT")
    if active_type_is_mesh: op.mode = "SCULPT"

    # Pose
    r = col.row()
    _Util.layout_operator(r, MPM_OT_PoseMode.bl_idname, text=iface_("Pose", act_mode_i18n_context), icon="POSE_HLT")

    # Weight Paint
    r = col.row(align=True)
    r.active = object_mode != "PAINT_WEIGHT" and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_("Weight Paint", act_mode_i18n_context), icon="WPAINT_HLT", depress=object_mode == "PAINT_WEIGHT")
    if active_type_is_mesh: 
        op.mode = "WEIGHT_PAINT"
        arm = _Util.get_armature(active)
        _Util.layout_operator(r, MPM_OT_ChangeModeWithArmature.bl_idname, "", icon="BONE_DATA").mode = "WEIGHT_PAINT"

    # Texture Paint
    r = col.row()
    r.active = object_mode != "PAINT_TEXTURE" and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_("Texture Paint", act_mode_i18n_context), icon="TPAINT_HLT", depress=object_mode == "PAINT_TEXTURE")
    if active_type_is_mesh: op.mode = "TEXTURE_PAINT"

class MPM_OT_ChangeModeWithArmature(bpy.types.Operator):
    bl_idname = "op.mpm_change_mode_with_armature"
    bl_label = "Changed Mode With Armature"
    bl_options = {"REGISTER", "UNDO"}
    mode: bpy.props.StringProperty()
    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active != None and active.type == 'MESH' and _Util.get_armature(active) != None
    def execute(self, context):
        active = context.active_object
        if self.mode == "WEIGHT_PAINT":
            _Util.get_armature(active).select_set(True)
        elif self.mode == "EDIT":
            _Util.select_active(_Util.get_armature(active))
        bpy.ops.object.mode_set(mode=self.mode)
        return {"FINISHED"}

class MPM_OT_PoseMode(bpy.types.Operator):
    bl_idname = "op.mpm_pose_mode"
    bl_label = "Changed to Pose Mode"
    bl_options = {"REGISTER", "UNDO"}
    @classmethod
    def poll(cls, context):
        if context.mode == "POSE":
            return False
        active = context.active_object
        return active != None and (active.type == "ARMATURE" or (active.type == 'MESH' and _Util.get_armature(active) != None))

    def execute(self, context):
        active = context.active_object
        if active.type == "MESH":
            # bpy.ops.object.select_all(action='DESELECT')
            arm = _Util.get_armature(active)
            arm.select_set(True)
            context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="POSE")
        return {"FINISHED"}
# --------------------------------------------------------------------------------
# ユーティリティメニュー
# --------------------------------------------------------------------------------
def PieMenuDraw_Utility(layout, context):
    box = layout.box()
    box.label(text = 'Utilities')
    row_parent = box.row()
    # -------------------------------
    row = row_parent.row(align = True)
    row.operator("screen.userpref_show", icon='PREFERENCES', text="")
    row.operator("wm.console_toggle", icon='CONSOLE', text="")
    row.operator("import_scene.fbx", icon='IMPORT', text="")
    row.operator("export_scene.fbx", icon='EXPORT', text="")
    row.operator(MPM_OT_Utility_ARPExport.bl_idname, icon='EXPORT', text="")

    row.operator(MPM_OT_Utility_ChangeLanguage.bl_idname, text="", icon="FILE_FONT")
    row = row_parent.row(align = True)
    file_path_list = _AddonPreferences.Accessor.get_open_file_path_list().strip()
    if file_path_list:
        for path in file_path_list.split(','):
            op = _Util.layout_operator(row, MPM_OT_Utility_OpenFile.bl_idname, text="", icon="FILE_FOLDER")
            op.path = path
    # -------------------------------
    row = box.row(align = True)
    box = row.box()
    # ツールメニュー
    box.label(text = 'Tool')
    c = box.column(align = True)
    # 行開始
    r = c.row(align=True)
    r.prop(context.tool_settings, "transform_pivot_point", text="", icon_only=True)
    r.prop_with_popover(context.scene.transform_orientation_slots[0], "type", text="", panel="VIEW3D_PT_transform_orientations",)
    r = c.row(align=True)
    _Util.layout_operator(r, MPM_OT_Utility_PivotOrientationSet.bl_idname, text="Reset").args = "GLOBAL,INDIVIDUAL_ORIGINS"
    _Util.layout_operator(r, MPM_OT_Utility_PivotOrientationSet.bl_idname, text="Cursor").args = "CURSOR,CURSOR"

    r = c.row(align=True)
    r.label(text="3d_cursor", icon="CURSOR")
    _Util.layout_operator(r, "view3d.snap_cursor_to_center", text="", icon="OBJECT_ORIGIN")
    _Util.layout_operator(r, "view3d.snap_cursor_to_selected", text="", icon="GROUP_VERTEX")

    # オーバーレイ
    r = box.row(align=True)
    c = r.column(align=True)
    c.active = getattr(context.space_data, "overlay", None) != None
    r = c.row(align=True);
    _Util.layout_prop(r, context.space_data.overlay, "show_overlays", icon="OVERLAY")
    r = r.row(align=True)
    r.scale_x = 0.7
    _Util.layout_operator(r, MPM_OT_Utility_ViewportSet.bl_idname, text="1").args = "True,SOLID"
    _Util.layout_operator(r, MPM_OT_Utility_ViewportSet.bl_idname, text="2").args = "False,MATERIAL"

    # 
    _Util.layout_prop(c, context.space_data.overlay, "show_bones", isActive=context.space_data.overlay.show_overlays, icon="BONE_DATA")
    _Util.layout_prop(c, context.space_data.overlay, "show_wireframes", isActive=context.space_data.overlay.show_overlays, icon="SHADING_WIRE")
    _Util.layout_prop(c, context.space_data.overlay, "show_annotation", isActive=context.space_data.overlay.show_overlays)
    # 透過
    view = context.space_data
    shading = view.shading if view.type == 'VIEW_3D' else context.scene.display.shading
    r = c.row()
    _Util.layout_prop(r, shading, "show_xray", text="")
    r = r.row()
    _Util.layout_prop(r, shading, "xray_alpha", text="X-Ray", isActive=shading.show_xray)


    # オブジェクトメニュー
    box = row.box()
    box.label(text = 'Object')
    c = box.column(align = True)
    c.active = context.active_object != None
    r = c.row(align = True)
    _Util.layout_prop(r, context.active_object, "show_in_front")
    armature = _Util.get_armature(context.active_object)
    _Util.MPM_OT_SetBoolToggle.operator(r, "", armature, "show_in_front", "BONE_DATA", isActive=armature!=None)

    _Util.layout_prop(c, context.active_object, "show_wire")
    _Util.layout_prop(c, context.active_object, "display_type")
    if armature != None:
        _Util.layout_prop(c, armature.data, "display_type", isActive=armature!=None)
    _Util.layout_operator(c, _MenuPose.MPM_OT_ClearTransform.bl_idname, isActive=_Util.is_armature_in_selected())
    _Util.layout_prop(c, context.scene, "sync_mode", text="sync_mode")


class MPM_OT_Utility_ChangeLanguage(bpy.types.Operator):
    bl_idname = "op.mpm_change_language"
    bl_label = "Change Language"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        if bpy.context.preferences.view.language == "en_US":
            bpy.context.preferences.view.language = _AddonPreferences.Accessor.get_second_language()
        else:
            bpy.context.preferences.view.language = "en_US"
        return {"FINISHED"}
        
class MPM_OT_Utility_PivotOrientationSet(bpy.types.Operator):
    bl_idname = "op.mpm_pivot_orientation_set"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    args: bpy.props.StringProperty()
    def execute(self, context):
        ori, pivot = self.args.replace(" ", "").split(",")
        context.scene.transform_orientation_slots[0].type = ori
        context.scene.tool_settings.transform_pivot_point = pivot
        return {"FINISHED"}
class MPM_OT_Utility_ViewportSet(bpy.types.Operator):
    bl_idname = "op.mpm_pivot_viewport_set"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    args: bpy.props.StringProperty()
    def execute(self, context):
        overlay, solid = self.args.replace(" ", "").split(",")
        context.space_data.overlay.show_overlays = overlay == "True"
        context.space_data.shading.type = solid
        return {"FINISHED"}
class MPM_OT_Utility_OpenFile(bpy.types.Operator):
    bl_idname = "op.mpm_open_file"
    bl_label = "Open Path"
    path: bpy.props.StringProperty()
    def execute(self, context):
        import subprocess
        subprocess.Popen(['start', self.path], shell=True)
        return {"FINISHED"}
        
class MPM_OT_Utility_ARPExport(bpy.types.Operator):
    bl_idname = "op.arp_export"
    bl_label = "Export with ARP"
    @classmethod
    def poll(cls, context):
        active = context.active_object
        return context.mode == "OBJECT" and active != None and _Util.get_armature(active) != None
        
    def execute(self, context):
        active_arm = _Util.get_armature(context.active_object)
        if active_arm is None:
            _Util.show_msgbox("Invalid selection!", icon="ERROR")
        else:
            sels = []
            for obj in context.selectable_objects:
                if obj.type == "MESH" and active_arm == _Util.get_armature(obj):
                    sels.append(obj)
            if 0 < len(sels):
                bpy.ops.object.select_all(action='DESELECT')
                for obj in sels:
                    obj.select_set(True)
                active_arm.select_set(True)
                context.view_layer.objects.active = active_arm
                bpy.ops.id.arp_export_fbx_panel('INVOKE_DEFAULT')
        return {"FINISHED"}
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
# --------------------------------------------------------------------------------

classes = (
    VIEW3D_MT_my_pie_menu,
    MPM_OT_Utility_ChangeLanguage,
    MPM_OT_Utility_PivotOrientationSet,
    MPM_OT_Utility_ViewportSet,
    MPM_OT_PoseMode,
    MPM_OT_ChangeModeWithArmature,
    MPM_OT_Utility_OpenFile,
    MPM_OT_Utility_ARPExport,
    MPM_OT_OpenPieMenu,
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
