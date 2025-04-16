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
    box = row.box()
    box.label(text="3rdParty Shortcut")
    enabled_addons = context.preferences.addons.keys()
    if "wiggle_2" in enabled_addons:
        _Util.layout_operator(box, "wiggle.reset", text="Wiggle2: ResetPhysics")
    if any("auto_rig_pro" in i for i in enabled_addons):
        _Util.layout_operator(box, MPM_OT_Pose_ARP_SnapIKFK.bl_idname)  # if imported

# --------------------------------------------------------------------------------


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
    MPM_PT_Pose_BoneCollectionPopover,
)


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
