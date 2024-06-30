import bpy
from . import _Util
from . import _AddonPreferences
from . import _MenuPose
import mathutils
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d, region_2d_to_origin_3d
# --------------------------------------------------------------------------------
# ユーティリティメニュー
# --------------------------------------------------------------------------------
def PieMenuDraw_Utility(layout, context):
    box = layout.box()
    box.label(text = "Utility")
    row_parent = box.row()
    # -------------------------------
    row = row_parent.row(align = True)
    row.operator("screen.userpref_show", icon="PREFERENCES", text="")
    row.operator("wm.console_toggle", icon="CONSOLE", text="")
    row.operator("import_scene.fbx", icon="IMPORT", text="")
    row.operator("export_scene.fbx", icon="EXPORT", text="")
    row.operator(MPM_OT_Utility_ARPExport.bl_idname, icon="EXPORT", text="")

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
    box.label(text = "Tool")
    c = box.column(align = True)
    # 行開始
    r = c.row(align=True)
    r.prop(context.tool_settings, "transform_pivot_point", text="", icon_only=True)
    r.prop_with_popover(context.scene.transform_orientation_slots[0], "type", text="", panel="VIEW3D_PT_transform_orientations",)
    r = c.row(align=True)
    _Util.layout_operator(r, MPM_OT_Utility_PivotOrientationSet_Reset.bl_idname, text="Reset")
    _Util.layout_operator(r, MPM_OT_Utility_PivotOrientationSet_Cursor.bl_idname, text="Cursor")

    # 3Dカーソル
    r = c.row(align=True)
    r.label(text="3d_cursor", icon="CURSOR")
    _Util.layout_operator(r, "view3d.snap_cursor_to_center", text="", icon="TRANSFORM_ORIGINS")
    _Util.layout_operator(r, "view3d.snap_cursor_to_selected", text="", icon="SNAP_FACE_CENTER")
    _Util.layout_operator(r, MPM_OT_Utility_Move3DCursorOnViewPlane.bl_idname, text="", icon="MOUSE_MOVE")

    # オーバーレイ
    r = box.row(align=True)
    c = r.column(align=True)
    c.active = getattr(context.space_data, "overlay", None) != None
    r = c.row(align=True);
    _Util.layout_prop(r, context.space_data.overlay, "show_overlays", icon="OVERLAY")
    r = r.row(align=True)
    r.scale_x = 0.7
    _Util.layout_operator(r, MPM_OT_Utility_ViewportShadingSetSolid.bl_idname, text="S")
    _Util.layout_operator(r, MPM_OT_Utility_ViewportShadingSetMaterial.bl_idname, text="M")

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

    # 3Dカーソル
    r = c.row(align=True)
    r.label(text="VPCamera", icon="VIEW_CAMERA")
    _Util.layout_operator(r, MPM_OT_Utility_ViewportCameraTranformSave.bl_idname)
    _Util.layout_operator(r, MPM_OT_Utility_ViewportCameraTranformRestore.bl_idname)

    # オブジェクトメニュー
    c2 = row.column()
    box = c2.box()
    box.label(text = "Object")

    c = box.column(align = True)
    c.active = context.active_object != None
    r = c.row(align = True)
    _Util.layout_prop(r, context.active_object, "show_in_front")
    armature = _Util.get_armature(context.active_object)
    _Util.MPM_OT_SetBoolToggle.operator(r, "", armature, "show_in_front", "BONE_DATA", isActive=armature!=None)

    _Util.layout_prop(c, context.active_object, "show_wire")
    _Util.layout_prop(c, context.active_object, "display_type")

    c.separator()

    if armature != None:
        _Util.layout_prop(c, armature.data, "display_type", isActive=armature!=None)
    _Util.layout_operator(c, _MenuPose.MPM_OT_ClearTransform.bl_idname, isActive=_Util.is_armature_in_selected())

    c.separator()

    r = c.row(align=True)
    r.active = context.active_object is not None and 1 < len(context.selected_objects)
    r.label(text="Copy")
    _Util.layout_operator(r, MPM_OT_Utility_CopyPosition.bl_idname)
    _Util.layout_operator(r, MPM_OT_Utility_CopyRosition.bl_idname)
    _Util.layout_operator(r, MPM_OT_Utility_CopyScale.bl_idname)

    # Animation
    box = c2.box()
    box.label(text = "Animation")
    c = box.column(align = True)

    _Util.layout_prop(c, context.scene, "sync_mode", text="sync_mode")

# --------------------------------------------------------------------------------
class MPM_OT_Utility_CopyPRSBase():
    def execute(self, context):
        active_obj = context.active_object
        for obj in context.selected_objects:
            if obj != active_obj:
                if type(self) is MPM_OT_Utility_CopyPosition:
                    obj.location = active_obj.location
                elif type(self) is MPM_OT_Utility_CopyRosition:
                    obj.rotation_euler = active_obj.rotation_euler
                elif type(self) is MPM_OT_Utility_CopyScale:
                    obj.scale = active_obj.scale
        return {'FINISHED'}
class MPM_OT_Utility_CopyPosition(MPM_OT_Utility_CopyPRSBase, bpy.types.Operator):
    bl_idname = "op.mpm_copy_position"
    bl_label = "Position"
    bl_description = "Position copy from active_object to selections."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context): return super().execute(context)
class MPM_OT_Utility_CopyRosition(MPM_OT_Utility_CopyPRSBase, bpy.types.Operator):
    bl_idname = "op.mpm_copy_rosition"
    bl_label = "Rotation"
    bl_description = "Rotation copy from active_object to selections."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context): return super().execute(context)
class MPM_OT_Utility_CopyScale(MPM_OT_Utility_CopyPRSBase, bpy.types.Operator):
    bl_idname = "op.mpm_copy_scale"
    bl_label = "Scale"
    bl_description = "Scale copy from active_object to selections."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context): return super().execute(context)
# --------------------------------------------------------------------------------
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
# --------------------------------------------------------------------------------
class MPM_OT_Utility_PivotOrientationSet_Reset(bpy.types.Operator):
    bl_idname = "op.mpm_pivot_orientation_set_reset"
    bl_label = ""
    bl_description = "Pivit=Origin, Orientation=Global"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        context.scene.transform_orientation_slots[0].type = "GLOBAL"
        context.scene.tool_settings.transform_pivot_point = "INDIVIDUAL_ORIGINS"
        return {"FINISHED"}
class MPM_OT_Utility_PivotOrientationSet_Cursor(bpy.types.Operator):
    bl_idname = "op.mpm_pivot_orientation_set_cursor"
    bl_label = ""
    bl_description = "Pivit=Cursor, Orientation=Cursor"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        context.scene.transform_orientation_slots[0].type = "CURSOR"
        context.scene.tool_settings.transform_pivot_point = "CURSOR"
        return {"FINISHED"}
# --------------------------------------------------------------------------------
class MPM_OT_Utility_ViewportShadingSetSolid(bpy.types.Operator):
    bl_idname = "op.mpm_pivot_viewport_shading_set_solid"
    bl_label = ""
    bl_description = "Overlay=True, Shading=SOLID"
    bl_options = {"REGISTER", "UNDO"}
    args: bpy.props.StringProperty()
    def execute(self, context):
        context.space_data.overlay.show_overlays = True
        context.space_data.shading.type = "SOLID"
        return {"FINISHED"}
class MPM_OT_Utility_ViewportShadingSetMaterial(bpy.types.Operator):
    bl_idname = "op.mpm_pivot_viewport_shading_set_material"
    bl_label = ""
    bl_description = "Overlay=True, Shading=MATERIAL"
    bl_options = {"REGISTER", "UNDO"}
    args: bpy.props.StringProperty()
    def execute(self, context):
        context.space_data.overlay.show_overlays = False
        context.space_data.shading.type = "MATERIAL"
        return {"FINISHED"}
# --------------------------------------------------------------------------------
class MPM_OT_Utility_OpenFile(bpy.types.Operator):
    bl_idname = "op.mpm_open_file"
    bl_label = "Open Path"
    path: bpy.props.StringProperty()
    def execute(self, context):
        import subprocess
        subprocess.Popen(['start', self.path], shell=True)
        return {"FINISHED"}
        
# --------------------------------------------------------------------------------
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
class MPM_OT_Utility_Move3DCursorOnViewPlane(bpy.types.Operator):
    bl_idname = "op.mpm_move_3dcursor_on_view_plane"
    bl_label = ""
    bl_description = "Move 3DCursor on View Plane"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type == "MOUSEMOVE":
            # マウスが画面外に出た場合の処理
            region = context.region
            rv3d = context.space_data.region_3d
            ex = event.mouse_x
            ey = event.mouse_y
            rx = region.x
            ry = region.y
            rw = region.width
            rh = region.height
            if event.mouse_x < rx:
                context.window.cursor_warp(rx + rw, ey)
                self.warp_x -= 1
            elif rx + rw <= event.mouse_x:
                context.window.cursor_warp(rx, ey)
                self.warp_x += 1
            if event.mouse_y < ry:
                context.window.cursor_warp(ex, ry + rh)
                self.warp_y -= 1
            elif ry + rh-1 <= event.mouse_y:
                context.window.cursor_warp(ex, ry)
                self.warp_y += 1
            delta_vector = region_2d_to_location_3d(region, rv3d, (event.mouse_x + rw * self.warp_x, event.mouse_y + rh * self.warp_y), (0,0,0)) - self.start_mouse_location3d
            context.scene.cursor.location = self.start_cursor_location + delta_vector
        elif event.type in {"LEFTMOUSE", "RET"}:
            return {"FINISHED"}
        elif event.type in {"RIGHTMOUSE", "ESC"}:
            context.scene.cursor.location = self.start_cursor_location
            return {"CANCELLED"}
        return {"RUNNING_MODAL"}
    def invoke(self, context, event):
        if context.space_data.type == "VIEW_3D":
            self.warp_x = 0
            self.warp_y = 0
            self.start_cursor_location = context.scene.cursor.location.copy()
            region = context.region
            rv3d = context.space_data.region_3d
            self.start_mouse_location3d = region_2d_to_location_3d(region, rv3d, (event.mouse_x, event.mouse_y), (0,0,0))
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        else:
            self.report({"WARNING"}, "View3D not found, cannot run operator")
            return {"CANCELLED"}
# --------------------------------------------------------------------------------
saved_location = None
saved_rotation = None
saved_distance = None
class MPM_OT_Utility_ViewportCameraTranformSave(bpy.types.Operator):
    bl_idname = "op.mpm_viewport_camera_transform_save"
    bl_label = "Save"
    bl_description = "Save the current viewport camera position and rotation"
    def execute(self, context):
        global saved_location, saved_rotation, saved_distance
        area = next(area for area in context.screen.areas if area.type == 'VIEW_3D')
        space = next(space for space in area.spaces if space.type == 'VIEW_3D')
        saved_location = space.region_3d.view_location.copy()
        saved_rotation = space.region_3d.view_rotation.copy()
        saved_distance = space.region_3d.view_distance
        self.report({'INFO'}, f"Saved Location: {saved_location}, Rotation: {saved_rotation}, Distance: {saved_distance}")
        return {'FINISHED'}

class MPM_OT_Utility_ViewportCameraTranformRestore(bpy.types.Operator):
    bl_idname = "op.mpm_viewport_camera_transform_restore"
    bl_label = "Restore"
    bl_description = "Restore the saved viewport camera position and rotation"
    @classmethod
    def poll(cls, context):
        global saved_location, saved_rotation, saved_distance
        return saved_location is not None and saved_rotation is not None and saved_distance is not None
    def execute(self, context):
        global saved_location, saved_rotation
        area = next(area for area in context.screen.areas if area.type == 'VIEW_3D')
        space = next(space for space in area.spaces if space.type == 'VIEW_3D')
        space.region_3d.view_location = saved_location
        space.region_3d.view_rotation = saved_rotation
        space.region_3d.view_distance = saved_distance
        self.report({'INFO'}, f"Restored Location: {saved_location}, Rotation: {saved_rotation}, Distance: {saved_distance}")
        return {'FINISHED'}
# --------------------------------------------------------------------------------

classes = (
    MPM_OT_Utility_CopyPosition,
    MPM_OT_Utility_CopyRosition,
    MPM_OT_Utility_CopyScale,
    MPM_OT_Utility_ChangeLanguage,
    MPM_OT_Utility_PivotOrientationSet_Reset,
    MPM_OT_Utility_PivotOrientationSet_Cursor,
    MPM_OT_Utility_ViewportShadingSetSolid,
    MPM_OT_Utility_ViewportShadingSetMaterial,
    MPM_OT_Utility_ViewportCameraTranformSave,
    MPM_OT_Utility_ViewportCameraTranformRestore,
    MPM_OT_Utility_OpenFile,
    MPM_OT_Utility_ARPExport,
    MPM_OT_Utility_Move3DCursorOnViewPlane,
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)
