import bpy
import bmesh
from . import _Util
from bpy.app.translations import (
    pgettext_iface as iface_,
)
# --------------------------------------------------------------------------------
# モード切り替えメニュー
# --------------------------------------------------------------------------------


def PieMenuDraw_ChangeModeLast(layout, context):
    # print(context.scene.mpm_prop.PrevModeName)
    if context.scene.mpm_prop.PrevModeName == "OBJECT":
        DrawOperatorObjectMode(r, context)
    elif context.scene.mpm_prop.PrevModeName == "EDIT_MESH" or context.scene.mpm_prop.PrevModeName == "EDIT_ARMATURE":
        DrawOperatorEditMode(r, context)
    elif context.scene.mpm_prop.PrevModeName == "SCULPT":
        DrawOperatorSculptMode(r, context)
    elif context.scene.mpm_prop.PrevModeName == "POSE":
        DrawOperatorPoseMode(r, context)
    elif context.scene.mpm_prop.PrevModeName == "PAINT_WEIGHT":
        DrawOperatorWeightPaintMode(r, context)
    elif context.scene.mpm_prop.PrevModeName == "PAINT_TEXTURE":
        DrawOperatorTexturePaintMode(r, context)
    elif context.scene.mpm_prop.PrevModeName == "PAINT_VERTEX":
        DrawOperatorVertexPaintMode(r, context)
    else:
        layout.separator() # これで空白を描画して、位置を調整してる


def PieMenuDraw_ChangeMode(layout, context):

    if context.space_data.type == "VIEW_3D":
        DrawView3D(layout, context)
    elif context.space_data.type == "IMAGE_EDITOR":
        DrawImageEditor(layout, context)


def DrawView3D(layout, context):
    # _PanelSelectionHistory.PanelHistory(box, context)
    box = layout.box()
    box.label(text="Mode")
    col = box.column(align=True)

    DrawOperatorObjectMode(col, context)
    DrawOperatorEditMode(col, context)
    DrawOperatorSculptMode(col, context)
    DrawOperatorPoseMode(col, context)
    DrawOperatorWeightPaintMode(col, context)
    DrawOperatorTexturePaintMode(col, context)
    DrawOperatorVertexPaintMode(col, context)


def DrawOperatorObjectMode(layout, context):
    object_mode = "OBJECT" if context.active_object is None else context.mode
    # print(bpy.types.Object.bl_rna.properties["mode"].enum_items[object_mode].name)
    op = _Util.layout_operator(layout,  MPM_OT_ChangeMode.bl_idname, "Object", icon="OBJECT_DATA",
                               isActive=object_mode != "OBJECT", depress=object_mode == "OBJECT")
    op.mode = "OBJECT"


def DrawOperatorEditMode(layout, context):
    object_mode = "OBJECT" if context.active_object is None else context.mode
    active_type_is_mesh = context.active_object != None and context.active_object.type == "MESH"
    active_type_is_armature = context.active_object != None and context.active_object.type == "ARMATURE"
    act_mode_i18n_context = bpy.types.Object.bl_rna.properties["mode"].translation_context

    r = layout.row(align=True)
    r.enabled = object_mode != "EDIT_MESH" and active_type_is_mesh or active_type_is_armature
    depress_comp = "EDIT_MESH" if active_type_is_mesh else "EDIT_ARMATURE"
    op = _Util.layout_operator(r,  MPM_OT_ChangeMode.bl_idname, iface_("Edit", act_mode_i18n_context),
                               icon="EDITMODE_HLT", depress=object_mode == depress_comp)
    if active_type_is_mesh or active_type_is_armature:
        op.mode = "EDIT"
    if active_type_is_mesh:
        _Util.layout_operator(r, MPM_OT_ChangeModeWithArmature.bl_idname, "", icon="BONE_DATA").mode = "EDIT"


def DrawOperatorSculptMode(layout, context):
    object_mode = "OBJECT" if context.active_object is None else context.mode
    active_type_is_mesh = context.active_object != None and context.active_object.type == "MESH"

    r = layout.row()
    r.enabled = object_mode != "SCULPT" and active_type_is_mesh
    op = _Util.layout_operator(r,  MPM_OT_ChangeMode.bl_idname, "Sculpt", icon="SCULPTMODE_HLT", depress=object_mode == "SCULPT")
    if active_type_is_mesh:
        op.mode = "SCULPT"
    _Util.layout_operator(r, MPM_OT_ChangeSculptModeWithMask.bl_idname, "", icon="MOD_MASK")


def DrawOperatorPoseMode(layout, context):
    act_mode_i18n_context = bpy.types.Object.bl_rna.properties["mode"].translation_context
    _Util.layout_operator(layout, MPM_OT_ChangeModePose.bl_idname, text=iface_("Pose", act_mode_i18n_context), icon="POSE_HLT")


def DrawOperatorWeightPaintMode(layout, context):
    object_mode = "OBJECT" if context.active_object is None else context.mode
    active_type_is_mesh = context.active_object != None and context.active_object.type == "MESH"

    r = layout.row(align=True)
    r.enabled = object_mode != "PAINT_WEIGHT" and active_type_is_mesh
    op = _Util.layout_operator(r,  MPM_OT_ChangeMode.bl_idname, "Weight Paint", icon="WPAINT_HLT", depress=object_mode == "PAINT_WEIGHT")
    if active_type_is_mesh:
        op.mode = "WEIGHT_PAINT"
        _Util.layout_operator(r, MPM_OT_ChangeModeWithArmature.bl_idname, "", icon="BONE_DATA").mode = "WEIGHT_PAINT"


def DrawOperatorTexturePaintMode(layout, context):
    object_mode = "OBJECT" if context.active_object is None else context.mode
    active_type_is_mesh = context.active_object != None and context.active_object.type == "MESH"
    act_mode_i18n_context = bpy.types.Object.bl_rna.properties["mode"].translation_context

    r = layout.row()
    r.enabled = object_mode != "PAINT_TEXTURE" and active_type_is_mesh
    op = _Util.layout_operator(r,  MPM_OT_ChangeMode.bl_idname, iface_("Texture Paint", act_mode_i18n_context),
                               icon="TPAINT_HLT", depress=object_mode == "PAINT_TEXTURE")
    if active_type_is_mesh:
        op.mode = "TEXTURE_PAINT"


def DrawOperatorVertexPaintMode(layout, context):
    object_mode = "OBJECT" if context.active_object is None else context.mode
    active_type_is_mesh = context.active_object != None and context.active_object.type == "MESH"

    r = layout.row()
    r.enabled = object_mode != "PAINT_VERTEX" and active_type_is_mesh
    op = _Util.layout_operator(r,  MPM_OT_ChangeMode.bl_idname, "Vertex Paint", icon="VPAINT_HLT", depress=object_mode == "PAINT_VERTEX")
    if active_type_is_mesh:
        op.mode = "VERTEX_PAINT"


def DrawImageEditor(layout, context):
    box = layout.box()
    box.label(text="Mode")
    c = box.column(align=True)

    _Util.layout_operator(c, MPM_OT_ChangeUITypeUV.bl_idname, icon="UV")
    _Util.layout_operator(c, MPM_OT_ChangeUITypeImage.bl_idname, icon="IMAGE")


class MPM_OT_ChangeUITypeUV(bpy.types.Operator):
    bl_idname = "op.mpm_change_ui_type_uv"
    bl_label = "UV Editor"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.ui_type != "UV"

    def execute(self, context):
        context.area.ui_type = "UV"
        return {"FINISHED"}


class MPM_OT_ChangeUITypeImage(bpy.types.Operator):
    bl_idname = "op.mpm_change_ui_type_image"
    bl_label = "Image Editor"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.ui_type != "IMAGE_EDITOR"

    def execute(self, context):
        context.area.ui_type = "IMAGE_EDITOR"
        return {"FINISHED"}


class MPM_OT_ChangeMode(bpy.types.Operator):
    bl_idname = "op.mpm_change_mode"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    mode: bpy.props.StringProperty()

    def execute(self, context):
        context.scene.mpm_prop.PrevModeName = context.scene.mpm_prop.PrevModeNameTemp
        bpy.ops.object.mode_set(mode=self.mode)
        return {"FINISHED"}


class MPM_OT_ChangeModeWithArmature(bpy.types.Operator):
    bl_idname = "op.mpm_change_mode_with_armature"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}
    mode: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return active != None and active.type == "MESH" and _Util.get_armature(active) != None

    def execute(self, context):
        active = context.active_object
        if self.mode == "WEIGHT_PAINT":
            _Util.get_armature(active).select_set(True)
        elif self.mode == "EDIT":
            _Util.select_active(_Util.get_armature(active))
        context.scene.mpm_prop.PrevModeName = context.scene.mpm_prop.PrevModeNameTmp
        bpy.ops.object.mode_set(mode=self.mode)
        return {"FINISHED"}


class MPM_OT_ChangeSculptModeWithMask(bpy.types.Operator):
    bl_idname = "op.mpm_change_sculpt_mode_with_mask"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and any(v.select for v in obj.data.vertices)

    def execute(self, context):
        context.scene.mpm_prop.PrevModeName = context.scene.mpm_prop.PrevModeNameTmp
        bpy.ops.object.mode_set(mode="SCULPT")
        bpy.ops.op.mpm_make_mask_with_selected_vert(is_invert=True)
        return {"FINISHED"}


class MPM_OT_ChangeModePose(bpy.types.Operator):
    bl_idname = "op.mpm_change_mode_pose"
    bl_label = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.mode == "POSE":
            return False
        active = context.active_object
        return active != None and (active.type == "ARMATURE" or (active.type == "MESH" and _Util.get_armature(active) != None))

    def execute(self, context):
        context.scene.mpm_prop.PrevModeName = context.scene.mpm_prop.PrevModeNameTmp
        active = context.active_object
        if active.type == "MESH":
            # bpy.ops.object.select_all(action='DESELECT')
            arm = _Util.get_armature(active)
            arm.select_set(True)
            context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="POSE")
        return {"FINISHED"}


classes = (
    MPM_OT_ChangeMode,
    MPM_OT_ChangeModeWithArmature,
    MPM_OT_ChangeSculptModeWithMask,
    MPM_OT_ChangeModePose,
    MPM_OT_ChangeUITypeUV,
    MPM_OT_ChangeUITypeImage,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
