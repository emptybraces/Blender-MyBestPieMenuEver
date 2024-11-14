import os
import subprocess
import bpy
from . import _Util
from . import _AddonPreferences
from ._MenuPose import MPM_OT_ClearTransform
from . import g
import mathutils
import bmesh
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d, region_2d_to_origin_3d
# --------------------------------------------------------------------------------
# ユーティリティメニュー
# --------------------------------------------------------------------------------


def PieMenuDraw_Utility(layout, context):
    box = layout.box()
    box.label(text="Utility")
    row_parent = box.row()
    # -------------------------------
    row = row_parent.row(align=True)
    row.operator("screen.userpref_show", icon="PREFERENCES", text="")
    row.operator("wm.console_toggle", icon="CONSOLE", text="")
    row.operator("import_scene.fbx", icon="IMPORT", text="")
    row.operator("export_scene.fbx", icon="EXPORT", text="")
    row.operator(MPM_OT_Utility_ARPExportPanel.bl_idname, icon="EXPORT", text="")

    row.operator(MPM_OT_Utility_ChangeLanguage.bl_idname, text="", icon="FILE_FONT")

    row.operator(MPM_OT_Utility_OpenDirectory.bl_idname, text="", icon="FOLDER_REDIRECT")
    row = row_parent.row(align=True)
    file_path_list = _AddonPreferences.Accessor.get_open_file_path_list().strip()
    if file_path_list:
        for path in file_path_list.split(','):
            op = _Util.layout_operator(row, MPM_OT_Utility_OpenFile.bl_idname, text="", icon="FILE_FOLDER")
            op.path = path

    if context.space_data.type == "VIEW_3D":
        DrawView3D(box, context)
    elif context.space_data.type == "IMAGE_EDITOR":
        DrawImageEditor(box, context)


def DrawView3D(layout, context):
    row = layout.row(align=True)
    box = row.box()
    # ツールメニュー
    box.label(text="Tool")
    c = box.column(align=True)
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
    _Util.layout_operator(r, MPM_OT_Utility_Snap3DCursorToSelectedEx.bl_idname, text="", icon="EMPTY_AXIS")
    _Util.layout_operator(r, MPM_OT_Utility_Snap3DCursorOnViewPlane.bl_idname, text="", icon="MOUSE_MOVE")

    # オーバーレイ
    overlay = context.space_data.overlay
    r = box.row(align=True)
    c = r.column(align=True)
    c.active = getattr(context.space_data, "overlay", None) != None
    r = c.row(align=True)
    _Util.layout_prop(r, overlay, "show_overlays")
    r = r.row(align=True)
    r.scale_x = 0.7
    _Util.layout_operator(r, MPM_OT_Utility_ViewportShadingSetSolid.bl_idname, text="S")
    _Util.layout_operator(r, MPM_OT_Utility_ViewportShadingSetMaterial.bl_idname, text="M")

    #
    _Util.layout_prop(c, overlay, "show_bones", isActive=overlay.show_overlays)
    _Util.layout_prop(c, overlay, "show_wireframes", isActive=overlay.show_overlays)
    _Util.layout_prop(c, overlay, "show_annotation", isActive=overlay.show_overlays)
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
    _Util.layout_operator(r, MPM_OT_Utility_ViewportCameraTransformSave.bl_idname)
    _Util.layout_operator(r, MPM_OT_Utility_ViewportCameraTransformRestorePanel.bl_idname)

    # オブジェクトメニュー
    c2 = row.column()
    box = c2.box()
    box.label(text="Object")

    c = box.column(align=True)
    c.active = context.active_object != None
    r = c.row(align=True)
    _Util.layout_prop(r, context.active_object, "show_in_front")
    armature = _Util.get_armature(context.active_object)
    _Util.MPM_OT_SetBoolToggle.operator(r, "", armature, "show_in_front", "BONE_DATA", isActive=armature != None)

    _Util.layout_prop(c, context.active_object, "show_wire")
    _Util.layout_prop(c, context.active_object, "display_type")

    c.separator()

    if armature != None:
        _Util.layout_prop(c, armature.data, "display_type", isActive=armature != None)
    _Util.layout_operator(c, MPM_OT_ClearTransform.bl_idname, isActive=_Util.is_armature_in_selected())

    c.separator()

    r = c.row(align=True)
    r.active = context.active_object is not None and 1 < len(context.selected_objects)
    r.label(text="Copy")
    _Util.layout_operator(r, MPM_OT_Utility_CopyPosition.bl_idname)
    _Util.layout_operator(r, MPM_OT_Utility_CopyRosition.bl_idname)
    _Util.layout_operator(r, MPM_OT_Utility_CopyScale.bl_idname)

    # UV
    c.prop(context.scene.mpm_prop, "UVMapPopoverEnum")

    # Animation
    box = c2.box()
    box.label(text="Animation")
    c = box.column(align=True)

    _Util.layout_prop(c, context.scene, "sync_mode", text="sync_mode")


def DrawImageEditor(layout, context):
    row = layout.row(align=True)
    # ツールメニュー
    box = row.box()
    box.label(text="Tool")
    c = box.column(align=True)

    # ピボット
    r = c.row(align=True)
    # r.prop(context.space_data, "pivot_point")
    data = context.space_data
    r.label(text="Pivot")
    _Util.MPM_OT_SetString.operator(r, "", data, "pivot_point", "CURSOR", icon="PIVOT_CURSOR")
    _Util.MPM_OT_SetString.operator(r, "", data, "pivot_point", "MEDIAN", icon="PIVOT_MEDIAN")
    _Util.MPM_OT_SetString.operator(r, "", data, "pivot_point", "CENTER", icon="PIVOT_BOUNDBOX")
    _Util.MPM_OT_SetString.operator(r, "", data, "pivot_point", "INDIVIDUAL_ORIGINS", icon="PIVOT_INDIVIDUAL")

    # ストレッチ
    c.prop(data.uv_editor, "show_stretch")

    # カラー

    r = c.row(align=True)
    r.label(text="Tex Channels")
    # for i in _Util.enum_values(context.space_data, "display_channels"):
    # ['COLOR_ALPHA', 'COLOR', 'ALPHA', 'Z_BUFFER', 'RED', 'GREEN', 'BLUE']
    _Util.MPM_OT_SetString.operator(r, "", data, "display_channels", "COLOR_ALPHA",
                                    depress=data.display_channels == "COLOR_ALPHA", icon="IMAGE_RGB_ALPHA")
    _Util.MPM_OT_SetString.operator(r, "", data, "display_channels", "COLOR", depress=data.display_channels == "COLOR", icon="IMAGE_RGB")
    _Util.MPM_OT_SetString.operator(r, "", data, "display_channels", "ALPHA", depress=data.display_channels == "ALPHA", icon="IMAGE_ALPHA")
    _Util.MPM_OT_SetString.operator(r, "", data, "display_channels", "RED", depress=data.display_channels == "RED", icon="COLOR_RED")
    _Util.MPM_OT_SetString.operator(r, "", data, "display_channels", "GREEN", depress=data.display_channels == "GREEN", icon="COLOR_BLUE")
    _Util.MPM_OT_SetString.operator(r, "", data, "display_channels", "BLUE", depress=data.display_channels == "BLUE", icon="COLOR_GREEN")

    # オブジェクトメニュー
    c = row.column()
    box = c.box()
    box.label(text="Object")
    # UV
    c.prop(context.scene.mpm_prop, "UVMapPopoverEnum")


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


class MPM_OT_Utility_ARPExportPanel(bpy.types.Operator):
    bl_idname = "op.mpm_arp_export_panel"
    bl_label = "Export with ARP"

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return 0 < len(context.selected_objects) and context.mode == "OBJECT" and active != None and _Util.get_armature(active) != None

    def invoke(self, context, event):
        g.is_force_cancelled_piemenu = True
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        self.layout.label(text="ARP Export")
        c = self.layout.box().column(align=True)
        _Util.layout_operator(c, MPM_OT_Utility_ARPExportSingle.bl_idname)
        for i in MPM_OT_Utility_ARPExportSingle.label_targets(context):
            c.label(text=i)

        c = self.layout.box().column(align=True)
        _Util.layout_operator(c, MPM_OT_Utility_ARPExportAll.bl_idname)
        for i in MPM_OT_Utility_ARPExportAll.label_targets(context):
            c.label(text=i)

    def execute(self, context):
        return {'FINISHED'}


class MPM_OT_Utility_ARPExportAll(bpy.types.Operator):
    bl_idname = "op.mpm_arp_export_all"
    bl_label = "Export with all meshes tied current armature"

    @classmethod
    def label_targets(cls, context):
        active_arm = _Util.get_armature(context.active_object)
        sels = []
        for obj in context.selectable_objects:
            if obj.type == "MESH" and active_arm == _Util.get_armature(obj):
                sels.append(obj.name)
        label = [f"mesh: {', '.join(sels)}", f"armature: {active_arm.name}"]
        return label

    def execute(self, context):
        active_arm = _Util.get_armature(context.active_object)
        if active_arm is None:
            _Util.show_msgbox("Invalid selection!", icon="ERROR")
            return {"CANCELLED"}
        sels = []
        for obj in context.selectable_objects:
            if obj.type == "MESH" and active_arm == _Util.get_armature(obj):
                sels.append(obj)
        if 0 < len(sels):
            bpy.ops.object.select_all(action='DESELECT')
            for obj in sels:
                obj.select_set(True)
            _Util.select_active(active_arm)
            bpy.ops.arp.arp_export_fbx_panel("INVOKE_DEFAULT")
        return {"FINISHED"}


class MPM_OT_Utility_ARPExportSingle(bpy.types.Operator):
    bl_idname = "op.mpm_arp_export_single"
    bl_label = "Export with selected mesh"

    @classmethod
    def label_targets(cls, context):
        label = [f"mesh: {context.active_object.name}", f"armature: {_Util.get_armature(context.active_object).name}"]
        return label

    def execute(self, context):
        active_arm = _Util.get_armature(context.active_object)
        if active_arm is None:
            _Util.show_msgbox("Invalid selection!", icon="ERROR")
            return {"CANCELLED"}
        sel = None
        for obj in context.selected_objects:
            if obj.type == "MESH" and active_arm == _Util.get_armature(obj):
                sel = obj
                break
        if sel != None:
            bpy.ops.object.select_all(action='DESELECT')
            sel.select_set(True)
            _Util.select_active(active_arm)
            bpy.ops.arp.arp_export_fbx_panel("INVOKE_DEFAULT")
        return {"FINISHED"}
# --------------------------------------------------------------------------------


class MPM_OT_Utility_Snap3DCursorToSelectedEx(bpy.types.Operator):
    bl_idname = "op.mpm_snap_cursor_to_selected_ex"
    bl_label = "Snap 3DCursor to selected EX"
    bl_description = "Snap 3DCursor to selected EX"
    bl_options = {'REGISTER', 'UNDO'}
    perpendicular: bpy.props.FloatProperty(
        name="Perpendicular", description="Slide in the direction of the perpendicular vector between the two selected items")
    offset: bpy.props.FloatVectorProperty(name="Offset")

    @classmethod
    def poll(cls, context):
        return 0 < len(context.selected_objects)

    def draw(self, context):
        layout = self.layout
        _Util.layout_prop(layout, self, "perpendicular", isActive=self.perpendicular_vec != None)
        layout.label(text="Offset:")
        layout.prop(self, "offset", index=0, text="X")
        layout.prop(self, "offset", index=1, text="Y")
        layout.prop(self, "offset", index=2, text="Z")

    def execute(self, context):
        obj = context.active_object
        selected_objects = context.selected_objects
        center = sum((obj.matrix_world.translation for obj in selected_objects), mathutils.Vector()) / len(selected_objects)
        self.perpendicular_vec = None
        if obj.mode == "EDIT":
            bm = bmesh.from_edit_mesh(obj.data)
            selected_verts = [v.co for v in bm.verts if v.select]
            if 0 < len(selected_verts):
                center = sum(selected_verts, mathutils.Vector()) / len(selected_verts)
                center = obj.matrix_world @ center  # オブジェクトのワールドマトリクスを考慮
            if 2 == len(selected_verts):
                self.perpendicular_vec = (selected_verts[1] - selected_verts[0]).cross(mathutils.Vector((0, 0, 1)))
                self.perpendicular_vec.normalize()
        else:
            if 2 == len(selected_objects):
                self.perpendicular_vec = (selected_objects[1].matrix_world.translation -
                                          selected_objects[0].matrix_world.translation).cross(mathutils.Vector((0, 0, 1)))
                self.perpendicular_vec.normalize()
            selected_objects = context.selected_objects
            center = sum((obj.matrix_world.translation for obj in selected_objects), mathutils.Vector()) / len(selected_objects)
        # 3Dカーソルの位置を設定
        p = center.copy()
        if self.perpendicular_vec != None:
            p += self.perpendicular_vec * self.perpendicular
        p += mathutils.Vector(self.offset)
        context.scene.cursor.location = p
        return {"FINISHED"}
# --------------------------------------------------------------------------------


class MPM_OT_Utility_Snap3DCursorOnViewPlane(bpy.types.Operator):
    bl_idname = "op.mpm_snap_cursor_on_view_plane"
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
            delta_vector = region_2d_to_location_3d(region, rv3d, (event.mouse_x + rw * self.warp_x,
                                                    event.mouse_y + rh * self.warp_y), (0, 0, 0)) - self.start_mouse_location3d
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
            self.start_mouse_location3d = region_2d_to_location_3d(region, rv3d, (event.mouse_x, event.mouse_y), (0, 0, 0))
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        else:
            self.report({"WARNING"}, "View3D not found, cannot run operator")
            return {"CANCELLED"}
# --------------------------------------------------------------------------------


class MPM_OT_Utility_ViewportCameraTransformSave(bpy.types.Operator):
    bl_idname = "op.mpm_viewport_camera_transform_save"
    bl_label = "Save"
    bl_description = "Save the current viewport camera position and rotation"

    def execute(self, context):
        area = next(area for area in context.screen.areas if area.type == 'VIEW_3D')
        space = next(space for space in area.spaces if space.type == 'VIEW_3D')
        prop = context.scene.mpm_prop.ViewportCameraTransforms.add()
        prop.pos = space.region_3d.view_location.copy()
        prop.rot = space.region_3d.view_rotation.copy()
        prop.distance = space.region_3d.view_distance
        # self.report({'INFO'}, f"Saved Location: {prop.pos}, Rotation: {prop.rot}, Distance: {prop.distance}")
        return {'FINISHED'}


class MPM_OT_Utility_ViewportCameraTransformRestorePanel(bpy.types.Operator):
    bl_idname = "op.mpm_viewport_camera_transform_restore_panel"
    bl_label = "Restore"
    bl_description = "Restore the saved viewport camera position and rotation"
    init_values = {}

    @classmethod
    def poll(cls, context):
        return 0 < len(context.scene.mpm_prop.ViewportCameraTransforms)

    def invoke(self, context, event):
        # 現在値を保存
        area = next(area for area in context.screen.areas if area.type == 'VIEW_3D')
        space = next(space for space in area.spaces if space.type == 'VIEW_3D')
        self.init_values["pos"] = space.region_3d.view_location.copy()
        self.init_values["rot"] = space.region_3d.view_rotation.copy()
        self.init_values["distance"] = space.region_3d.view_distance
        g.is_force_cancelled_piemenu = True
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.label(text="Click to apply.")
        c = self.layout.column(align=True)
        for i, data in enumerate(context.scene.mpm_prop.ViewportCameraTransforms):
            data = context.scene.mpm_prop.ViewportCameraTransforms[i]
            name = f"#{i} - POS({int(data.pos[0])},{int(data.pos[1])},{int(data.pos[2])}), D({int(data.distance)})"
            r = c.row(align=True)
            r.operator(MPM_OT_Utility_ViewportCameraTransformRestore.bl_idname, text=name).idx = i
            r.operator(MPM_OT_Utility_ViewportCameraTransformRestoreRemove.bl_idname, text="", icon="X").idx = i

    def cancel(self, context):
        # 復元
        area = next(area for area in context.screen.areas if area.type == 'VIEW_3D')
        space = next(space for space in area.spaces if space.type == 'VIEW_3D')
        space.region_3d.view_location = self.init_values["pos"]
        space.region_3d.view_rotation = self.init_values["rot"]
        space.region_3d.view_distance = self.init_values["distance"]

    def execute(self, context):
        return {'FINISHED'}


class MPM_OT_Utility_ViewportCameraTransformRestore(bpy.types.Operator):
    bl_idname = "op.mpm_viewport_camera_transform_restore"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    idx: bpy.props.IntProperty()

    def execute(self, context):
        area = next(area for area in context.screen.areas if area.type == 'VIEW_3D')
        space = next(space for space in area.spaces if space.type == 'VIEW_3D')
        data = context.scene.mpm_prop.ViewportCameraTransforms[self.idx]
        space.region_3d.view_location = data.pos
        space.region_3d.view_rotation = data.rot
        space.region_3d.view_distance = data.distance
        return {"FINISHED"}


class MPM_OT_Utility_ViewportCameraTransformRestoreRemove(bpy.types.Operator):
    bl_idname = "op.mpm_viewport_camera_transform_restore_remove"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    idx: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.mpm_prop.ViewportCameraTransforms.remove(self.idx)
        return {"FINISHED"}
    import bpy


class MPM_OT_Utility_OpenDirectory(bpy.types.Operator):
    bl_idname = "op.mpm_open_directory"
    bl_label = "Open the directory location of the currently opened blend file"

    def execute(self, context):
        filepath = bpy.data.filepath
        if filepath:
            directory = os.path.dirname(filepath)
            # OSに応じてディレクトリを開く
            if os.name == "nt":  # Windows
                os.startfile(directory)
            elif os.name == "posix":  # macOS, Linux
                subprocess.Popen(["xdg-open", directory])
            else:
                self.report({"ERROR"}, "Unsupported OS")
                return {"CANCELLED"}
            self.report({"INFO"}, f"Opened directory: {directory}")
        else:
            self.report({"ERROR"}, "Blend file is not saved yet")
            return {"CANCELLED"}
        return {"FINISHED"}


# --------------------------------------------------------------------------------

class MPM_OT_Utility_DumpMissingReference(bpy.types.Operator):
    bl_idname = "op.mpm_dump_Missing_reference"
    bl_label = "Check Missing Reference"

    def execute(self, context):
        missing_images = []
        for image in bpy.data.images:
            file_path = bpy.path.abspath(image.filepath)
            if not os.path.exists(file_path):
                missing_images.append(image)
        if missing_images:
            _Util.show_report_warn(self, "The following image reference is missing:")
            for image in missing_images:
                _Util.show_report_warn(self, image.name, image.path)
        else:
            _Util.show_report(self, "There are no images with missing references.")

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
    MPM_OT_Utility_ViewportCameraTransformSave,
    MPM_OT_Utility_ViewportCameraTransformRestorePanel,
    MPM_OT_Utility_ViewportCameraTransformRestore,
    MPM_OT_Utility_ViewportCameraTransformRestoreRemove,
    MPM_OT_Utility_OpenFile,
    MPM_OT_Utility_ARPExportPanel,
    MPM_OT_Utility_ARPExportSingle,
    MPM_OT_Utility_ARPExportAll,
    MPM_OT_Utility_Snap3DCursorToSelectedEx,
    MPM_OT_Utility_Snap3DCursorOnViewPlane,
    MPM_OT_Utility_OpenDirectory,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
