import bpy
import bmesh
from . import _Util
from bpy.app.translations import (
    pgettext_iface as iface_,
    pgettext_tip as tip_,
    contexts as i18n_contexts,
)
# --------------------------------------------------------------------------------
# モード切り替えメニュー
# --------------------------------------------------------------------------------


def PieMenuDraw_ModeChange(layout, context):

    if context.space_data.type == "VIEW_3D":
        DrawView3D(layout, context)
    elif context.space_data.type == "IMAGE_EDITOR":
        DrawImageEditor(layout, context)


def DrawView3D(layout, context):
    active = context.active_object
    object_mode = "OBJECT" if active is None else context.mode
    active_type_is_mesh = active != None and active.type == "MESH"
    active_type_is_armature = active != None and active.type == "ARMATURE"
    act_mode_i18n_context = bpy.types.Object.bl_rna.properties["mode"].translation_context

    # _PanelSelectionHistory.PanelHistory(box, context)

    box = layout.box()
    box.label(text="Mode")
    col = box.column(align=True)

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
    if active_type_is_mesh or active_type_is_armature:
        op.mode = "EDIT"
    if active_type_is_mesh:
        _Util.layout_operator(r, MPM_OT_ChangeModeWithArmature.bl_idname, "", icon="BONE_DATA").mode = "EDIT"

    # Sculpt
    r = col.row()
    r.active = object_mode != "SCULPT" and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_("Sculpt", act_mode_i18n_context), icon="SCULPTMODE_HLT", depress=object_mode == "SCULPT")
    if active_type_is_mesh:
        op.mode = "SCULPT"
        _Util.layout_operator(r, MPM_OT_ChangeSculptModeWithMask.bl_idname, "", icon="MOD_MASK")

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
    if active_type_is_mesh:
        op.mode = "TEXTURE_PAINT"

    # Vertex Paint
    r = col.row()
    r.active = object_mode != "PAINT_VERTEX" and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_("Vertex Paint", act_mode_i18n_context), icon="VPAINT_HLT", depress=object_mode == "PAINT_VERTEX")
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
        active = context.active_object
        bpy.ops.object.mode_set(mode="SCULPT")
        bpy.ops.op.mpm_make_mask_with_selected_vert(is_invert=True)
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
        return active != None and (active.type == "ARMATURE" or (active.type == "MESH" and _Util.get_armature(active) != None))

    def execute(self, context):
        active = context.active_object
        if active.type == "MESH":
            # bpy.ops.object.select_all(action='DESELECT')
            arm = _Util.get_armature(active)
            arm.select_set(True)
            context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="POSE")
        return {"FINISHED"}


classes = (
    MPM_OT_ChangeModeWithArmature,
    MPM_OT_ChangeSculptModeWithMask,
    MPM_OT_PoseMode,
    MPM_OT_ChangeUITypeUV,
    MPM_OT_ChangeUITypeImage,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
