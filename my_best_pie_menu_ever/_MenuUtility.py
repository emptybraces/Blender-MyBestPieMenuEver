if "bpy" in locals():
    import importlib
    importlib.reload(_AddonPreferences)
    importlib.reload(_Util)
    importlib.reload(_UtilInput)
    importlib.reload(_UtilBlf)
    importlib.reload(g)
    importlib.reload(_MenuPose)
else:
    from . import _AddonPreferences
    from . import _Util
    from . import _UtilInput
    from . import _UtilBlf
    from . import g
    from . import _MenuPose
import os
import subprocess
import bpy
import bmesh
import math
from time import time
from mathutils import Vector, Quaternion
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d, region_2d_to_origin_3d
from bpy.app.translations import pgettext_iface as iface_

# --------------------------------------------------------------------------------
# ユーティリティメニュー
# --------------------------------------------------------------------------------


class MPM_Prop_ViewportCameraTransform(bpy.types.PropertyGroup):
    pos: bpy.props.FloatVectorProperty(size=3)
    rot: bpy.props.FloatVectorProperty(size=4)
    distance: bpy.props.FloatProperty()


def draw_pie_menu(layout, context):
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
    row = layout.row()
    col = row.column()

    # ピボット、座標軸
    box = col.box()
    box.label(text="Anchor")
    c = box.column(align=True)
    r = c.row(align=True)
    r.label(text="Pivot")
    for item in bpy.types.ToolSettings.bl_rna.properties["transform_pivot_point"].enum_items:
        _Util.MPM_OT_SetString.operator(r, "", context.tool_settings, "transform_pivot_point", item.identifier,
                                        item.icon, context.tool_settings.transform_pivot_point == item.identifier)

    r = c.row(align=True)
    r.label(text="Orientation")
    for item in bpy.types.TransformOrientationSlot.bl_rna.properties["type"].enum_items:
        _Util.MPM_OT_SetString.operator(r, "", context.scene.transform_orientation_slots[0], "type", item.identifier,
                                        item.icon, context.scene.transform_orientation_slots[0].type == item.identifier)
    s = c.split(factor=0.7)
    _, r = s.row(), s.row()
    _Util.layout_operator(r, MPM_OT_Utility_PivotOrientationSet_Reset.bl_idname, text="Reset")
    # _Util.layout_operator(r, MPM_OT_Utility_PivotOrientationSet_Cursor.bl_idname, text="Cursor")

    # 3Dカーソル
    s = c.split(factor=0.25)
    r1, r2 = s.row(align=True), s.row(align=True)
    r1.label(text="3D Cursor")
    _Util.layout_operator(r2, "view3d.snap_cursor_to_center", text="", icon="TRANSFORM_ORIGINS")
    _Util.layout_operator(r2, "view3d.snap_cursor_to_selected", text="", icon="SNAP_FACE_CENTER")
    _Util.layout_operator(r2, MPM_OT_Utility_Snap3DCursorToSelectedEx.bl_idname, text="", icon="EMPTY_AXIS")
    _Util.layout_operator(r2, MPM_OT_Utility_Snap3DCursorOnViewPlane.bl_idname, text="", icon="MOUSE_MOVE")
    _Util.layout_operator(r2, MPM_OT_Utility_3DCursorPositionSetZero.bl_idname, text="X0").mode = "x"
    _Util.layout_operator(r2, MPM_OT_Utility_3DCursorPositionSetZero.bl_idname, text="Y0").mode = "y"
    _Util.layout_operator(r2, MPM_OT_Utility_3DCursorPositionSetZero.bl_idname, text="Z0").mode = "z"
    # 設定
    box = col.box()
    box.label(text="Settings")
    c = box.column(align=True)
    view = context.space_data
    shading = view.shading if view.type == "VIEW_3D" else context.scene.display.shading

    # オーバーレイ、最前面
    overlay = getattr(context.space_data, "overlay", None)
    r = c.row(align=True)
    r.enabled = overlay != None
    _Util.layout_prop(r, overlay, "show_overlays", "Overlay")
    r = r.row(align=True)
    _Util.layout_prop(r, overlay, "show_bones", "Bone", isActive=overlay.show_overlays)

    # ワイヤーフレーム、アノテーション
    r = c.row(align=True)
    _Util.layout_prop(r, overlay, "show_wireframes", "Wireframe", isActive=overlay.show_overlays)
    _Util.layout_prop(r, overlay, "show_annotation", "Annotation", isActive=overlay.show_overlays)
    # 透過
    r = c.row()
    _Util.layout_prop(r, shading, "show_xray", text="")
    _Util.layout_prop(r, shading, "xray_alpha", text="X-Ray", isActive=shading.show_xray)
    # シェーディングモード
    r = c.row(align=True)
    r.label(text="Shading")
    for item in bpy.types.View3DShading.bl_rna.properties["type"].enum_items:
        _Util.MPM_OT_SetString.operator(r, "", shading, "type", item.identifier, item.icon, shading.type == item.identifier)
    # オーバーレイとシェーディングのペアショートカット切り替え
    # 連続押しできるようになったのでコメント
    # r = r.row(align=True)
    # _Util.layout_operator(r, MPM_OT_Utility_ViewportShadingSetSolid.bl_idname, text="Ov+Solid")
    # _Util.layout_operator(r, MPM_OT_Utility_ViewportShadingSetMaterial.bl_idname, text="UnOv+Mat")
    # シェーディングカラー
    r1, r2 = _Util.layout_split_row2(c, 0.4)
    r1.label(text="ShadingColor")
    _Util.MPM_OT_SetString.operator(r2, "MAT", shading, "color_type", "MATERIAL", "NONE", shading.color_type == "MATERIAL")
    _Util.MPM_OT_SetString.operator(r2, "OBJ", shading, "color_type", "OBJECT", "NONE", shading.color_type == "OBJECT")
    _Util.MPM_OT_SetString.operator(r2, "VCOL", shading, "color_type", "VERTEX", "NONE", shading.color_type == "VERTEX")

    # -------------------------------
    # 次の列
    col = row.column()
    # オブジェクトメニュー
    box = col.box()
    c = box.column()
    c.label(text="Active")

    r = c.row(align=True)
    active_collec = context.view_layer.active_layer_collection
    r.label(text=active_collec.name, icon="OUTLINER_COLLECTION")
    _Util.layout_operator(r, MPM_OT_Utility_ActiveCollectionShowHide.bl_idname,
                          icon="HIDE_ON" if active_collec.hide_viewport else "HIDE_OFF")

    r = c.row(align=True)
    obj = context.object
    if obj:
        r.label(text=obj.name, icon="OBJECT_DATAMODE")
        _Util.MPM_OT_SetBoolToggle.operator(r, "", obj, "hide_viewport", "HIDE_ON" if obj.hide_viewport else "HIDE_OFF")
    else:
        r.label(text="No Active Object", icon="OBJECT_DATAMODE")
    _Util.layout_operator(r, MPM_OT_Utility_SelectionCycleSoloModal.bl_idname, "", icon="FILE_REFRESH")

    # アクティブオブジェクトがなければ空欄
    if obj:
        c = box.column(align=True)
        r = c.row(align=True)
        _Util.layout_prop(r, obj, "show_in_front")
        armature = _Util.get_armature(obj)
        _Util.layout_operator(r, _MenuPose.MPM_OT_Pose_ShowInFrontArmature.bl_idname, "", armature != None,  getattr(
            armature, "show_in_front", False), "BONE_DATA").is_on = not getattr(armature, "show_in_front", False)

        _Util.layout_prop(c, obj, "show_wire")

        r = c.row(align=True)
        r.label(text="Display Type")
        icons = ["PIVOT_BOUNDBOX", "MOD_WIREFRAME", "SHADING_SOLID", "TEXTURE"]
        for i, item in enumerate(bpy.types.Object.bl_rna.properties["display_type"].enum_items):
            _Util.MPM_OT_SetString.operator(r, "", obj, "display_type", item.identifier,
                                            icons[i], obj.display_type == item.identifier)
        # UV
        c.prop(context.scene.mpm_prop, "UVMapPopoverEnum")
        # ビューポートオブジェクトカラー
        r = c.row(align=True)
        r.scale_x = 0.5
        _Util.layout_prop(r, obj, "color", isActive=shading.color_type == "OBJECT")
        # コピー
        r = c.row(align=True)
        r.active = obj is not None and 1 < len(context.selected_objects)
        r1, r2 = _Util.layout_split_row2(r, 0.2)
        r1.label(text="Copy")
        _Util.layout_operator(r2, MPM_OT_Utility_CopyPosition.bl_idname)
        _Util.layout_operator(r2, MPM_OT_Utility_CopyRosition.bl_idname)
        _Util.layout_operator(r2, MPM_OT_Utility_CopyScale.bl_idname)
        # アーマチュア
        box = c.box()
        box.label(text="Armature")
        c = box.column(align=True)
        if armature != None:
            c.row(align=True).prop(armature.data, "pose_position", expand=True)
        r = c.row(align=True)
        _Util.layout_operator(r, _MenuPose.MPM_OT_Pose_ResetBoneTransform.bl_idname)
        _Util.layout_operator(r, _MenuPose.MPM_OT_Pose_ResetBoneTransformAndAnimationFrame.bl_idname, icon="ANIM")
        if armature != None:
            c.popover(panel=_MenuPose.MPM_PT_Pose_BoneCollectionPopover.bl_idname, icon="GROUP_BONE")
            _Util.layout_prop(c, armature.data, "display_type", isActive=armature != None)

    # -------------------------------
    # 次の列
    col = row.column()

    # Animation
    box = col.box()
    box.label(text="Animation")
    c = box.column(align=True)

    c.prop(context.scene.mpm_prop, "AnimationSpeed")
    r = c.row(align=True)
    r.scale_x = 0.9
    _Util.layout_prop(r, context.scene, "frame_start")
    _Util.layout_prop(r, context.scene, "frame_end")
    r = r.row()
    _Util.layout_operator(r, MPM_OT_Utility_AnimationEndFrameSyncCurrentAction.bl_idname, icon="FILE_REFRESH")
    r = c.row(align=True)
    _Util.layout_prop(r, context.scene, "frame_current", isActive=False)
    _Util.MPM_OT_CallbackOperator.operator(r, "Reset", __name__+".animation_frame_reset",
                                           lambda c: c.scene.frame_set(c.scene.frame_start), (context,), "FRAME_PREV")
    _Util.layout_prop(c, context.scene, "sync_mode")

    # その他
    box = col.box()
    box.label(text="Etc")
    c = box.column(align=True)
    # ビューポートカメラ保存
    r = c.row(align=True)
    r.label(text="VPCamera", icon="VIEW_CAMERA")
    _Util.layout_operator(r, MPM_OT_Utility_ViewportCameraTransformSave.bl_idname)
    _Util.layout_operator(r, MPM_OT_Utility_ViewportCameraTransformRestorePanel.bl_idname)


def DrawImageEditor(layout, context):
    row = layout.row(align=True)
    col = row.column()
    # Pivotメニュー
    box = col.box()
    box.label(text="Anchor")
    c = box.column(align=True)
    r = c.row(align=True)
    # r.prop(context.space_data, "pivot_point")
    data = context.space_data
    r.label(text="Pivot")
    _Util.MPM_OT_SetString.operator(r, "", data, "pivot_point", "CURSOR", icon="PIVOT_CURSOR")
    _Util.MPM_OT_SetString.operator(r, "", data, "pivot_point", "MEDIAN", icon="PIVOT_MEDIAN")
    _Util.MPM_OT_SetString.operator(r, "", data, "pivot_point", "CENTER", icon="PIVOT_BOUNDBOX")
    _Util.MPM_OT_SetString.operator(r, "", data, "pivot_point", "INDIVIDUAL_ORIGINS", icon="PIVOT_INDIVIDUAL")

    # 設定メニュー
    box = col.box()
    box.label(text="Settings")
    c = box.column(align=True)
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
    box.label(text="Selected Object")
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
        return {"FINISHED"}


class MPM_OT_Utility_CopyPosition(MPM_OT_Utility_CopyPRSBase, bpy.types.Operator):
    bl_idname = "mpm.util_copy_position"
    bl_label = "Position"
    bl_description = "Position copy from active_object to selections."
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context): return super().execute(context)


class MPM_OT_Utility_CopyRosition(MPM_OT_Utility_CopyPRSBase, bpy.types.Operator):
    bl_idname = "mpm.util_copy_rosition"
    bl_label = "Rotation"
    bl_description = "Rotation copy from active_object to selections."
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context): return super().execute(context)


class MPM_OT_Utility_CopyScale(MPM_OT_Utility_CopyPRSBase, bpy.types.Operator):
    bl_idname = "mpm.util_copy_scale"
    bl_label = "Scale"
    bl_description = "Scale copy from active_object to selections."
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context): return super().execute(context)
# --------------------------------------------------------------------------------


class MPM_OT_Utility_ChangeLanguage(bpy.types.Operator):
    bl_idname = "mpm.util_change_language"
    bl_label = "Change Language"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.context.preferences.view.language == "en_US":
            bpy.context.preferences.view.language = _AddonPreferences.Accessor.get_second_language()
            bpy.context.preferences.view.use_translate_new_dataname = False
        else:
            bpy.context.preferences.view.language = "en_US"
        return {"FINISHED"}
# --------------------------------------------------------------------------------


class MPM_OT_Utility_PivotOrientationSet_Reset(bpy.types.Operator):
    bl_idname = "mpm.util_pivot_orientation_set_reset"
    bl_label = "Pivot & Orientation Reset"
    bl_description = "Pivit=Origin, Orientation=Global"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.transform_orientation_slots[0].type = "GLOBAL"
        context.scene.tool_settings.transform_pivot_point = "INDIVIDUAL_ORIGINS"
        return {"FINISHED"}


class MPM_OT_Utility_PivotOrientationSet_Cursor(bpy.types.Operator):
    bl_idname = "mpm.util_pivot_orientation_set_cursor"
    bl_label = "Pivot & Orientation Cursor"
    bl_description = "Pivit=Cursor, Orientation=Cursor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.transform_orientation_slots[0].type = "CURSOR"
        context.scene.tool_settings.transform_pivot_point = "CURSOR"
        return {"FINISHED"}

# --------------------------------------------------------------------------------


class MPM_OT_Utility_OpenFile(bpy.types.Operator):
    bl_idname = "mpm.util_open_file"
    bl_label = "Open Path"
    path: bpy.props.StringProperty()

    def execute(self, context):
        import subprocess
        subprocess.Popen(['start', self.path], shell=True)
        return {"FINISHED"}
# --------------------------------------------------------------------------------


class MPM_OT_Utility_ARPExportPanel(bpy.types.Operator):
    bl_idname = "mpm.util_arp_export_panel"
    bl_label = "Export with ARP"

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return 0 < len(context.selected_objects) and context.mode == "OBJECT" and active != None and _Util.get_armature(active) != None

    def invoke(self, context, event):
        g.force_cancel_piemenu_modal(context)
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
        return {"FINISHED"}


class MPM_OT_Utility_ARPExportAll(bpy.types.Operator):
    bl_idname = "mpm.util_arp_export_all"
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
    bl_idname = "mpm.util_arp_export_single"
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
    bl_idname = "mpm.util_snap_cursor_to_selected_ex"
    bl_label = "Snap 3DCursor to selected EX"
    bl_description = "Snap 3DCursor to selected EX"
    bl_options = {"REGISTER", "UNDO"}
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
        center = sum((obj.matrix_world.translation for obj in selected_objects), Vector()) / len(selected_objects)
        self.perpendicular_vec = None
        if obj.mode == "EDIT":
            bm = bmesh.from_edit_mesh(obj.data)
            selected_verts = [v.co for v in bm.verts if v.select]
            if 0 < len(selected_verts):
                center = sum(selected_verts, Vector()) / len(selected_verts)
                center = obj.matrix_world @ center  # オブジェクトのワールドマトリクスを考慮
            if 2 == len(selected_verts):
                self.perpendicular_vec = (selected_verts[1] - selected_verts[0]).cross(Vector((0, 0, 1)))
                self.perpendicular_vec.normalize()
        else:
            if 2 == len(selected_objects):
                self.perpendicular_vec = (selected_objects[1].matrix_world.translation -
                                          selected_objects[0].matrix_world.translation).cross(Vector((0, 0, 1)))
                self.perpendicular_vec.normalize()
            selected_objects = context.selected_objects
            center = sum((obj.matrix_world.translation for obj in selected_objects), Vector()) / len(selected_objects)
        # 3Dカーソルの位置を設定
        p = center.copy()
        if self.perpendicular_vec != None:
            p += self.perpendicular_vec * self.perpendicular
        p += Vector(self.offset)
        context.scene.cursor.location = p
        return {"FINISHED"}
# --------------------------------------------------------------------------------


class MPM_OT_Utility_Snap3DCursorOnViewPlane(bpy.types.Operator):
    bl_idname = "mpm.util_snap_cursor_on_view_plane"
    bl_label = ""
    bl_description = "Move 3DCursor on View Plane"
    bl_options = {"REGISTER", "UNDO"}

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


class MPM_OT_Utility_3DCursorPositionSetZero(bpy.types.Operator):
    bl_idname = "mpm.util_3dcursor_position_set_zero"
    bl_label = ""
    bl_description = "Set 3DCursor Position Zero"
    bl_options = {"REGISTER", "UNDO"}
    mode: bpy.props.StringProperty(options={"HIDDEN"})

    def execute(self, context):
        if self.mode == "x":
            bpy.context.scene.cursor.location.x = 0.0
        elif self.mode == "y":
            bpy.context.scene.cursor.location.y = 0.0
        else:
            bpy.context.scene.cursor.location.z = 0.0
        return {"FINISHED"}

# --------------------------------------------------------------------------------


class MPM_OT_Utility_AnimationEndFrameSyncCurrentAction(bpy.types.Operator):
    bl_idname = "mpm.util_animation_end_frame_sync_current_action"
    bl_label = ""
    bl_description = "Synchronize start/end frame from selected object's action"

    @classmethod
    def poll(cls, context):
        for obj in _Util.selected_objects():
            if obj.animation_data and obj.animation_data.action:
                return True
            arm = obj.find_armature()
            if arm and arm.animation_data and arm.animation_data.action:
                return True
        return False

    def execute(self, context):
        MAX = 99999
        frame_start = MAX
        frame_end = -MAX
        for obj in _Util.selected_objects():
            action = obj.animation_data and obj.animation_data.action
            if not action:
                arm = obj.find_armature()
                action = arm and arm.animation_data and arm.animation_data.action
            if action:
                for fcurve in action.fcurves:
                    keyframe_points = fcurve.keyframe_points
                    if keyframe_points:
                        frame_start = min(frame_start, keyframe_points[0].co.x)
                        frame_end = max(frame_end, keyframe_points[-1].co.x)
        if frame_start != MAX and frame_end != -MAX:
            context.scene.frame_start = int(frame_start)
            context.scene.frame_end = int(frame_end * (context.scene.render.frame_map_new / context.scene.render.frame_map_old))
        return {"FINISHED"}
# --------------------------------------------------------------------------------


class MPM_OT_Utility_ViewportCameraTransformSave(bpy.types.Operator):
    bl_idname = "mpm.util_viewport_camera_transform_save"
    bl_label = "Save"
    bl_description = "Save the current viewport camera transform"

    def execute(self, context):
        prop = context.scene.mpm_prop.ViewportCameraTransforms.add()
        prop.pos = context.region_data.view_location.copy()
        prop.rot = context.region_data.view_rotation.copy()
        prop.distance = context.region_data.view_distance
        # self.report({'INFO'}, f"Saved Location: {prop.pos}, Rotation: {prop.rot}, Distance: {prop.distance}")
        return {"FINISHED"}


class MPM_OT_Utility_ViewportCameraTransformRestorePanel(bpy.types.Operator):
    bl_idname = "mpm.util_viewport_camera_transform_restore_panel"
    bl_label = "Restore"
    bl_description = "Restore the saved viewport camera transform"
    bl_options = {"REGISTER", "UNDO"}
    is_skip = False

    @classmethod
    def poll(cls, context):
        return 0 < len(context.scene.mpm_prop.ViewportCameraTransforms)

    def invoke(self, context, event):
        g.force_cancel_piemenu_modal(context)
        # 現在値を保存
        data = context.region_data
        self.original_transform = (data.view_location.copy(), data.view_rotation.copy(), data.view_distance)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        c = self.layout.column()
        c.label(text="Click to apply.")
        c = c.column(align=True)
        # 方角を求める
        directions = [
            ("↑", Quaternion((0, 0, 1), math.radians(0)) @ _Util.VEC3_Y()),
            ("↖", Quaternion((0, 0, 1), math.radians(45)) @ _Util.VEC3_Y()),
            ("←", Quaternion((0, 0, 1), math.radians(90)) @ _Util.VEC3_Y()),
            ("↙", Quaternion((0, 0, 1), math.radians(135)) @ _Util.VEC3_Y()),
            ("↓", Quaternion((0, 0, 1), math.radians(180)) @ _Util.VEC3_Y()),
            ("↘", Quaternion((0, 0, 1), math.radians(225)) @ _Util.VEC3_Y()),
            ("→", Quaternion((0, 0, 1), math.radians(270)) @ _Util.VEC3_Y()),
            ("↗", Quaternion((0, 0, 1), math.radians(315)) @ _Util.VEC3_Y()),
        ]
        for i, data in enumerate(context.scene.mpm_prop.ViewportCameraTransforms):
            # 現在のカメラの向き（+Yベクトルを回転させる）
            camera_direction = Quaternion(data.rot) @ Vector((0, 1, 0))
            # 最小角度を探す
            closest_direction = None
            min_angle = float("inf")
            for name, direction in directions:
                angle = camera_direction.angle(direction)
                if angle < min_angle:
                    min_angle = angle
                    closest_direction = name
            label = f"POS({int(data.pos[0])},{int(data.pos[1])},{int(data.pos[2])}), ROT({closest_direction}), D({int(data.distance)})"
            r = c.row(align=True)
            _Util.MPM_OT_CallbackOperator.operator(r, label, self.bl_idname+str(i), self.on_click_restore, (context, i))
            _Util.MPM_OT_CallbackOperator.operator(r, "", self.bl_idname+str(i), self.on_click_remove, (context, i), "X")
            _Util.MPM_OT_CallbackOperator.operator(r, "", self.bl_idname+str(i), self.on_click_movedown, (context, i), "TRIA_DOWN")
            _Util.MPM_OT_CallbackOperator.operator(r, "", self.bl_idname+str(i), self.on_click_moveup, (context, i), "TRIA_UP")
        c.label(text="Transition")
        r = c.row(align=True)
        _Util.layout_prop(r, self, "transition_factor", isActive=1 < len(context.scene.mpm_prop.ViewportCameraTransforms))
        _Util.layout_prop(r, self, "transition_span", isActive=1 < len(context.scene.mpm_prop.ViewportCameraTransforms))
        _Util.MPM_OT_CallbackOperator.operator(r, "Play", self.bl_idname+".transition_animation", self.on_click_play, (context,), "PLAY")

    def execute(self, context):
        _Util.MPM_OT_CallbackOperator.clear()
        return {"FINISHED"}

    def cancel(self, context):
        _Util.MPM_OT_CallbackOperator.clear()
        bpy.ops.mpm.util_viewport_camera_transform_restore_modal("INVOKE_DEFAULT",
                                                                 target_pos=self.original_transform[0], target_rot=self.original_transform[1], target_distance=self.original_transform[2])

    def on_click_moveup(self, context, idx):
        if 0 < idx:
            context.scene.mpm_prop.ViewportCameraTransforms.move(idx, idx-1)

    def on_click_movedown(self, context, idx):
        if idx + 1 < len(context.scene.mpm_prop.ViewportCameraTransforms):
            context.scene.mpm_prop.ViewportCameraTransforms.move(idx, idx+1)

    def on_click_remove(self, context, idx):
        context.scene.mpm_prop.ViewportCameraTransforms.remove(idx)

    def on_click_restore(self, context, idx):
        data = context.scene.mpm_prop.ViewportCameraTransforms[idx]
        self.is_skip = False
        _Util.callbacks["on_finish"] = lambda: self._on_finish(context, idx)
        bpy.ops.mpm.util_viewport_camera_transform_restore_modal("INVOKE_DEFAULT",
                                                                 target_pos=data["pos"], target_rot=data["rot"], target_distance=data["distance"])

    def on_click_play(self, context):
        _Util.callbacks["on_finish"] = lambda: self._on_finish(context, -1)
        # _Util.callbacks["on_update_factor"] = lambda x: setattr(self, "transition_factor", x)
        bpy.ops.mpm.util_viewport_camera_transform_restore_modal("INVOKE_DEFAULT", anim_whole=True, anim_duration=self.transition_span)

    def _on_transition_update(self, context):
        if MPM_OT_Utility_ViewportCameraTransformRestorePanel.is_skip:
            return
        MPM_OT_Utility_ViewportCameraTransformRestorePanel.set_view(self.transition_factor)

    transition_factor: bpy.props.FloatProperty(name="Factor", default=0.0, min=0.0, max=1.0, step=0.1, update=_on_transition_update)
    transition_span: bpy.props.FloatProperty(name="Duration", default=5, min=1)

    def _on_finish(self, context, idx):
        _Util.callback_remove("on_finish")
        _Util.callback_remove("on_update_factor")
        pos = [Vector(i.pos) for i in context.scene.mpm_prop.ViewportCameraTransforms]
        MPM_OT_Utility_ViewportCameraTransformRestorePanel.is_skip = True
        if idx == -1:
            idx = len(pos) - 1
        self.transition_factor = _Util.lerp_inverse_segments_by_distance(pos, idx)
        MPM_OT_Utility_ViewportCameraTransformRestorePanel.is_skip = False

    @staticmethod
    def set_view(factor):
        data = bpy.context.scene.mpm_prop.ViewportCameraTransforms
        pos = [Vector(i.pos) for i in data]
        rot = [Quaternion(i.rot) for i in data]
        distance = [i.distance for i in data]
        bpy.context.region_data.view_location = _Util.interp_catmull_rom(pos, factor)
        bpy.context.region_data.view_rotation = _Util.interp_slerp_quaternion(rot, factor)
        bpy.context.region_data.view_distance = _Util.interp_catmull_rom(distance, factor)


class MPM_OT_Utility_ViewportCameraTransformRestoreModal(bpy.types.Operator):
    bl_idname = "mpm.util_viewport_camera_transform_restore_modal"
    bl_label = ""
    target_pos: bpy.props.FloatVectorProperty(size=3)
    target_rot: bpy.props.FloatVectorProperty(size=4)
    target_distance: bpy.props.FloatProperty()
    anim_duration: bpy.props.FloatProperty(default=0.25)
    anim_whole: bpy.props.BoolProperty()
    anim_start_time = 0.0

    def invoke(self, context, event):
        if self.anim_whole == False:
            self.anim_duration = 0.25
        data = context.region_data
        self.start_transform = (data.view_location.copy(), data.view_rotation.copy(), data.view_distance)
        self.timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if not event.type in {"RIGHTMOUSE", "ESC"} and self.timer.time_duration <= self.anim_duration:
            if self.anim_whole:
                t = min(1.0, self.timer.time_duration / self.anim_duration)
                MPM_OT_Utility_ViewportCameraTransformRestorePanel.set_view(t)
                return {"RUNNING_MODAL"}
            else:
                t = min(1.0, self.timer.time_duration / self.anim_duration)
                context.region_data.view_location = self.start_transform[0].lerp(self.target_pos, t)
                context.region_data.view_rotation = self.start_transform[1].slerp(self.target_rot, t)
                context.region_data.view_distance = _Util.lerp(self.start_transform[2], self.target_distance, t)
                return {"RUNNING_MODAL"}
        _Util.callback_try("on_finish")
        context.window_manager.event_timer_remove(self.timer)
        return {"FINISHED"}


class MPM_OT_Utility_OpenDirectory(bpy.types.Operator):
    bl_idname = "mpm.util_open_directory"
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


class MPM_OT_Utility_ActiveCollectionShowHide(bpy.types.Operator):
    bl_idname = "mpm.util_active_collection_show_hide"
    bl_label = ""
    bl_description = "Show/Hide Active Collection"
    last_collection = None

    @classmethod
    def poll(cls, context):
        return cls.last_collection != None or context.scene.collection != context.view_layer.active_layer_collection.collection

    def execute(self, context):
        cls = MPM_OT_Utility_ActiveCollectionShowHide
        c = context.view_layer.active_layer_collection
        if cls.last_collection and context.scene.collection == c.collection:
            c = cls.last_collection
        c.hide_viewport = not c.hide_viewport
        cls.last_collection = c
        return {"FINISHED"}


class MPM_OT_Utility_SelectionCycleSoloModal(_Util.MPM_StackableViewportUI, bpy.types.Operator):
    bl_idname = "mpm.util_selection_cycle_solo_modal"
    bl_label = "Cycle Solo Selected"
    bl_description = "MouseWheel to isolate selected objects one by one"

    @classmethod
    def poll(cls, context):
        return 1 < len(context.selected_objects)

    def invoke(self, context, event):
        super().init_draw_class_instance(context, True, "cycle_solo", lambda: self.DrawModal(context.selected_objects, self.id))
        self.input = _UtilInput.Monitor()
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        # if context.area != self.target_area:
        #     return {'PASS_THROUGH'}
        # このモーダルは最後のDrawModalまで生存
        if "CANCELLED" in super().modal(context, event):
            return self.cancel(context)
        self.input.update(event, "LEFTMOUSE", "RIGHTMOUSE", "ESC")
        for modal in _Util.stackable_draw_modals[self.id]:
            if modal.is_current_modal:
                # print(modal.current_focus_type, self.input.is_keydown("LEFTMOUSE"))
                if modal.current_focus_type == "remove" and self.input.is_keydown("LEFTMOUSE"):
                    modal.cancel()
                    return {"RUNNING_MODAL"}
                elif modal.current_focus_type == "current_name":
                    if event.type == "WHEELUPMOUSE" or event.type == "WHEELDOWNMOUSE":
                        modal.switch_solo(event.type == "WHEELUPMOUSE")
                        return {"RUNNING_MODAL"}
                    elif self.input.is_keydown("LEFTMOUSE"):
                        modal.switch_all(True)
                        return {"RUNNING_MODAL"}
                    elif self.input.is_keydown("RIGHTMOUSE"):
                        modal.switch_all(False)
                        return {"RUNNING_MODAL"}
        return {"PASS_THROUGH"}

    def cancel(self, context):
        super().cancel(context)
        MPM_OT_Utility_SelectionCycleSoloModal.draw_modal = None
        return {"CANCELLED"}

    class DrawModal(_Util.MPM_StackableModalMonitor):
        def __init__(self, selected_objects, id):
            super().__init__(id)
            self.handler2d = bpy.types.SpaceView3D.draw_handler_add(self.draw2d, (), "WINDOW", "POST_PIXEL")
            self.selected_objects = list(selected_objects)
            self.sel_index = 0

        def draw2d(self):
            if self.try_cancel():
                return
            self.prepare_current_state()
            parent = MPM_OT_Utility_SelectionCycleSoloModal
            modals = _Util.stackable_draw_modals[self.id]
            modal_idx = modals.index(self)
            for i in reversed(range(len(self.selected_objects))):
                try:
                    _ = self.selected_objects[i].name  # 削除されたものは適当にアクセスして例外起こす
                except ReferenceError:
                    del self.selected_objects[i]
                    self.sel_index = 0
                    if len(self.selected_objects) <= 1:
                        self.cancel()
                        return
            # label
            text = "Cycle Solo:"
            w, h = _UtilBlf.draw_label_dimensions(text)
            h *= 1.5
            x, y = g.space_view_command_display_begin_pos(self.id)
            y += h * modal_idx
            if modal_idx == len(modals)-1:  # 最後だけ表示
                _UtilBlf.draw_label(text, x, y, "right")
            x += 10
            current = self.selected_objects[self.sel_index]
            text = f"({self.sel_index+1}/{len(self.selected_objects)}) "
            text += current.name[:15] + "..." if 15 < len(current.name) else current.name.ljust(18)[:18]
            if _UtilBlf.draw_label_mousehover(text, "mouse wheel: Next/Prev, LMB: Show all, RMB: Hide all",
                                              x, y, parent.mx, parent.my, active=self.is_current_modal and self.current_focus_type == "current_name", align="left"):
                self.is_current_modal = True
                self.current_focus_type = "current_name"
            x += _UtilBlf.draw_label_dimensions("w" * 18)[0]
            if _UtilBlf.draw_label_mousehover("[X]", "left click: Cancelling",
                                              x, y, parent.mx, parent.my, active=self.is_current_modal and self.current_focus_type == "remove", align="left"):
                self.is_current_modal = True
                self.current_focus_type = "remove"

        def switch_solo(self, isUp):
            self.sel_index = self.sel_index+1 if isUp else self.sel_index-1
            if self.sel_index < 0:
                self.sel_index = len(self.selected_objects)-1
            elif len(self.selected_objects) <= self.sel_index:
                self.sel_index = 0
            for i in range(len(self.selected_objects)):
                self.selected_objects[i].hide_set(i != self.sel_index)

        def switch_all(self, isShow):
            self.sel_index = 0
            for i in range(len(self.selected_objects)):
                self.selected_objects[i].hide_set(not isShow)

        def cancel(self):
            super().cancel()
            if self.handler2d:
                bpy.types.SpaceView3D.draw_handler_remove(self.handler2d, "WINDOW")
            self.handler2d = None


# --------------------------------------------------------------------------------


classes = (
    MPM_Prop_ViewportCameraTransform,
    MPM_OT_Utility_CopyPosition,
    MPM_OT_Utility_CopyRosition,
    MPM_OT_Utility_CopyScale,
    MPM_OT_Utility_ChangeLanguage,
    MPM_OT_Utility_PivotOrientationSet_Reset,
    MPM_OT_Utility_PivotOrientationSet_Cursor,
    MPM_OT_Utility_ViewportCameraTransformSave,
    MPM_OT_Utility_ViewportCameraTransformRestorePanel,
    MPM_OT_Utility_ViewportCameraTransformRestoreModal,
    MPM_OT_Utility_OpenFile,
    MPM_OT_Utility_ARPExportPanel,
    MPM_OT_Utility_ARPExportSingle,
    MPM_OT_Utility_ARPExportAll,
    MPM_OT_Utility_Snap3DCursorToSelectedEx,
    MPM_OT_Utility_Snap3DCursorOnViewPlane,
    MPM_OT_Utility_3DCursorPositionSetZero,
    MPM_OT_Utility_OpenDirectory,
    MPM_OT_Utility_AnimationEndFrameSyncCurrentAction,
    MPM_OT_Utility_ActiveCollectionShowHide,
    MPM_OT_Utility_SelectionCycleSoloModal,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
