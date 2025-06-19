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
    arm = context.object.data

    # primary menu
    c = row.column()
    box = c.box()
    box.row().prop(arm, "pose_position", expand=True)
    r = box.row(align=True)
    _Util.layout_operator(r, MPM_OT_Pose_ResetBoneTransform.bl_idname)
    _Util.layout_operator(r, MPM_OT_Pose_ResetBoneTransformAndAnimationFrame.bl_idname, icon="ANIM")
    # bone collections
    if bpy.app.version < (4, 0, 0):
        box.prop(arm, "layers")
    else:
        box.popover(panel=MPM_PT_Pose_BoneCollectionPopover.bl_idname, icon="GROUP_BONE")

    # thirdparty shortcut
    draw_layout_3rdparty(context, row)

# --------------------------------------------------------------------------------


def draw_layout_3rdparty(context, layout):
    box = layout.box()
    box.label(text="3rdParty Shortcut")
    enabled_addons = context.preferences.addons.keys()
    if "wiggle_2" in enabled_addons:
        _Util.layout_operator(box, "wiggle.reset", text="Wiggle2: ResetPhysics")
    if any("auto_rig_pro" in i for i in enabled_addons):
        box.label(text="Auto-Rig Pro")
        c = box.column(align=True)
        # c.label(text="Auto-Rig Pro")
        r = c.row(align=True)
        r1, r2 = _Util.layout_split_row2(r, 0.3)
        r1.label(text="Arms")
        _Util.layout_operator(r2, MPM_OT_Pose_ARP_SnapIKFK.bl_idname, text="FK").type = "FK_Arm"
        _Util.layout_operator(r2, MPM_OT_Pose_ARP_SnapIKFK.bl_idname, text="IK").type = "IK_Arm"
        r1, r2 = _Util.layout_split_row2(r, 0.3)
        r1.label(text="Legs")
        _Util.layout_operator(r2, MPM_OT_Pose_ARP_SnapIKFK.bl_idname, text="FK").type = "FK_Leg"
        _Util.layout_operator(r2, MPM_OT_Pose_ARP_SnapIKFK.bl_idname, text="IK").type = "IK_Leg"


def draw_layout_bone_collection(layout, arm):
    def _get_all_bone_collections(arm):
        result = []

        def collect_recursive(collection, level=0):
            result.append((collection, level))
            for child in collection.children:
                collect_recursive(child, level + 1)
        for col in arm.collections:
            collect_recursive(col)
        return result

    selected_col_names = set()
    if bpy.context.mode in ("POSE", "PAINT_WEIGHT"):
        for pbone in bpy.context.selected_pose_bones:
            selected_col_names.update(col.name for col in pbone.bone.collections)
    all_collections = _get_all_bone_collections(arm)
    for col, level in all_collections:
        row = layout.row(align=True)
        row.separator(factor=level * 1)  # 階層インデント
        # icon = 'TRIA_DOWN' if BoneCollectionState.foldout_state.get(col.name, True) else 'TRIA_RIGHT'
        # op = row.operator("view3d.toggle_bone_collection_fold", text="", icon=icon, emboss=False)
        row.label(text=col.name)
        row.label(text="", icon="DOT" if col.name in selected_col_names else "NONE")
        row.prop(col, "is_visible", text="", toggle=True, icon="HIDE_OFF" if col.is_visible else "HIDE_ON")
        row.prop(col, "is_solo", text="", toggle=True, icon="SOLO_ON" if col.is_solo else "SOLO_OFF")


class MPM_PT_Pose_BoneCollectionPopover(bpy.types.Panel):
    bl_idname = "MPM_PT_pose_bone_collection_popover"
    bl_label = "Bone Collections"
    bl_space_type = "TOPBAR"  # ポップオーバー専用の空間
    bl_region_type = "WINDOW"
    bl_ui_units_x = 12  # 横幅

    def draw(self, context):
        draw_layout_bone_collection(self.layout.column(align=True), _Util.get_armature(context.object).data)
# --------------------------------------------------------------------------------


class MPM_OT_Pose_ResetBoneTransform(bpy.types.Operator):
    bl_idname = "mpm.pose_reset_bone_transform"
    bl_label = "Reset Bone Transform"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _Util.is_armature_in_selected()

    def execute(self, context):
        for obj in _Util.selected_objects():
            _Util.reset_pose_bone(obj)
        if context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
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
        for obj in _Util.selected_objects():
            _Util.reset_pose_bone(obj)
        if context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
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
        for obj in _Util.selected_objects():
            if arm := obj if obj.type == "ARMATURE" else obj.find_armature():
                arm.show_in_front = self.is_on
        return {"FINISHED"}
# --------------------------------------------------------------------------------


class MPM_OT_Pose_ARP_SnapIKFK(bpy.types.Operator):
    bl_idname = "mpm.pose_arp_snapikfk"
    bl_label = "AutoRigPro: Snap IK-FK"
    bl_options = {"REGISTER", "UNDO"}
    type: bpy.props.StringProperty()

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
        for arm in arms:
            _Util.select_active(arm)
            if self.type == "FK_Arm":
                self.convert(arm.pose.bones["c_hand_ik.l"].bone, bpy.ops.pose.arp_arm_fk_to_ik_)
                self.convert(arm.pose.bones["c_hand_ik.r"].bone, bpy.ops.pose.arp_arm_fk_to_ik_)
            elif self.type == "IK_Arm":
                self.convert(arm.pose.bones["c_hand_fk.l"].bone, bpy.ops.pose.arp_arm_ik_to_fk_)
                self.convert(arm.pose.bones["c_hand_fk.r"].bone, bpy.ops.pose.arp_arm_ik_to_fk_)
            elif self.type == "FK_Leg":
                self.convert(arm.pose.bones["c_foot_ik.l"].bone, bpy.ops.pose.arp_leg_fk_to_ik_)
                self.convert(arm.pose.bones["c_foot_ik.r"].bone, bpy.ops.pose.arp_leg_fk_to_ik_)
            elif self.type == "IK_Leg":
                self.convert(arm.pose.bones["c_foot_fk.l"].bone, bpy.ops.pose.arp_leg_ik_to_fk_)
                self.convert(arm.pose.bones["c_foot_fk.r"].bone, bpy.ops.pose.arp_leg_ik_to_fk_)
        if current_mode != "POSE":
            bpy.ops.object.mode_set(mode=current_mode)
        return {"FINISHED"}

    def convert(self, bone, func):
        bpy.ops.pose.select_all(action="DESELECT")
        bone.select = True
        func()


# --------------------------------------------------------------------------------
classes = (
    MPM_OT_Pose_ResetBoneTransform,
    MPM_OT_Pose_ResetBoneTransformAndAnimationFrame,
    MPM_OT_Pose_ARP_SnapIKFK,
    MPM_OT_Pose_ShowInFrontArmature,
    MPM_PT_Pose_BoneCollectionPopover,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
