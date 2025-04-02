if "bpy" in locals():
    import importlib
    importlib.reload(_Util)
else:
    from . import _Util
import bpy
# --------------------------------------------------------------------------------
# ポーズメニュー
# --------------------------------------------------------------------------------


def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text="Pose Primary")
    row = box.row()

    # pose
    arm = context.object.data
    box = row.box()
    box.row().prop(arm, "pose_position", expand=True)
    r = box.row(align=True)
    _Util.layout_operator(r, MPM_OT_Pose_ResetBoneTransform.bl_idname)
    _Util.layout_operator(r, MPM_OT_Pose_ResetBoneTransformAndAnimationFrame.bl_idname, icon="ANIM")

    # thirdparty shortcut
    box = row.box()
    box.label(text="3rdParty Shortcut")
    enabled_addons = context.preferences.addons.keys()
    if "wiggle_2" in enabled_addons:
        _Util.layout_operator(box, "wiggle.reset", text="Wiggle2: ResetPhysics")
    if any("auto_rig_pro" in i for i in enabled_addons):
        _Util.layout_operator(box, MPM_OT_Pose_ARP_SnapIKFK.bl_idname)  # if imported

    if bpy.app.version < (4, 0, 0):
        box.prop(arm, "layers")


class MPM_OT_Pose_ResetBoneTransform(bpy.types.Operator):
    bl_idname = "mpm.pose_reset_bone_transform"
    bl_label = "Reset Bone Transform"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _Util.is_armature_in_selected()

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            _Util.reset_pose_bone(obj)
        return {"FINISHED"}


class MPM_OT_Pose_ResetBoneTransformAndAnimationFrame(bpy.types.Operator):
    bl_idname = "mpm.pose_reset_bone_transform_and_animation_frame"
    bl_label = ""
    bl_description = "Reset bone transform and animation frame"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _Util.is_armature_in_selected()

    def execute(self, context):
        context.scene.frame_set(context.scene.frame_start)
        selected_objects = context.selected_objects
        for obj in selected_objects:
            _Util.reset_pose_bone(obj)
        return {"FINISHED"}


class MPM_OT_Pose_ShowInFrontArmature(bpy.types.Operator):
    bl_idname = "mpm.pose_show_in_front_armature"
    bl_label = "Show In Front"
    bl_options = {"REGISTER", "UNDO"}
    is_on: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        return _Util.is_armature_in_selected()

    def execute(self, context):
        for obj in context.selected_objects:
            if arm := obj if obj.type == "ARMATURE" else obj.find_armature():
                arm.show_in_front = self.is_on
        return {"FINISHED"}
# --------------------------------------------------------------------------------


class MPM_OT_Pose_ARP_SnapIKFK(bpy.types.Operator):
    bl_idname = "mpm.pose_arp_snapikfk"
    bl_label = "AutoRigPro: Snap IK-FK"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _Util.get_armature(context.active_object) != None

    def execute(self, context):
        current_mode = context.active_object.mode
        arm = _Util.get_armature(context.active_object)
        _Util.select_active(arm)
        # アーマチュア選択後じゃないと、ポーズモードに変更できない
        arms = [i for i in bpy.context.selected_objects if i.type == "ARMATURE"]
        if 0 < len(arms) and current_mode != "POSE":
            bpy.ops.object.mode_set(mode="POSE")
        for obj in arms:
            if obj.type == "ARMATURE":
                bpy.ops.pose.select_all(action="DESELECT")
                bpy.context.object.data.bones.active = obj.pose.bones["c_hand_ik.l"].bone
                bpy.ops.pose.arp_switch_snap()
                bpy.ops.pose.select_all(action="DESELECT")
                bpy.context.object.data.bones.active = obj.pose.bones["c_hand_ik.r"].bone
                bpy.ops.pose.arp_switch_snap()
                bpy.ops.pose.select_all(action="DESELECT")
                bpy.context.object.data.bones.active = obj.pose.bones["c_foot_ik.r"].bone
                bpy.ops.pose.arp_switch_snap()
                bpy.ops.pose.select_all(action="DESELECT")
                bpy.context.object.data.bones.active = obj.pose.bones["c_foot_ik.l"].bone
                bpy.ops.pose.arp_switch_snap()
                bpy.ops.pose.select_all(action="DESELECT")
                break
        if current_mode != "POSE":
            bpy.ops.object.mode_set(mode=current_mode)
        return {"FINISHED"}


# --------------------------------------------------------------------------------
classes = (
    MPM_OT_Pose_ResetBoneTransform,
    MPM_OT_Pose_ResetBoneTransformAndAnimationFrame,
    MPM_OT_Pose_ARP_SnapIKFK,
    MPM_OT_Pose_ShowInFrontArmature,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
