import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util
# --------------------------------------------------------------------------------
# ポーズメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Pose Primary')
    arm = context.object.data;
    box.row().prop(arm, "pose_position", expand=True)
    box.prop(arm, 'layers')

class MPM_OT_ClearTransform(bpy.types.Operator):
    bl_idname = "op.clear_transform"
    bl_label = "Reset Bone Transform"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            _Util.reset_pose_bone(obj)
        # 古い処理
        # current_mode = context.active_object.mode
        # # backup
        # buf = []
        # for i in range(32):
        #     buf.append(bpy.context.object.data.layers[i])
        #     bpy.context.object.data.layers[i] = True
        # # execution
        # bpy.ops.pose.select_all(action='SELECT')
        # bpy.ops.pose.rot_clear()
        # bpy.ops.pose.loc_clear()
        # bpy.ops.pose.scale_clear()
        # # restore
        # for i in range(32):
        #     bpy.context.object.data.layers[i] = buf[i]
        # bpy.ops.object.mode_set( mode = current_mode)
        return {'FINISHED'}
# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    box = pie.split().box()
    box.label(text = 'Pose Secondary')
    _Util.layout_operator(box, "wiggle.reset", text="Wiggle2: ResetPhysics") # if imported
    _Util.layout_operator(box, MPM_OT_ARP_SNAPIKFK.bl_idname) # if imported

class MPM_OT_ARP_SNAPIKFK(bpy.types.Operator):
    bl_idname = "op.mpm_arp_snapikfk"
    bl_label = "AutoRigPro: Snap IK-FK"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == "ARMATURE":
                bpy.ops.pose.select_all(action='DESELECT')
                bpy.context.object.data.bones.active = obj.pose.bones["c_hand_ik.l"].bone
                bpy.ops.pose.arp_switch_snap()
                bpy.ops.pose.select_all(action='DESELECT')
                bpy.context.object.data.bones.active = obj.pose.bones["c_hand_ik.r"].bone
                bpy.ops.pose.arp_switch_snap()
                bpy.ops.pose.select_all(action='DESELECT')
                bpy.context.object.data.bones.active = obj.pose.bones["c_foot_ik.r"].bone
                bpy.ops.pose.arp_switch_snap()
                bpy.ops.pose.select_all(action='DESELECT')
                bpy.context.object.data.bones.active = obj.pose.bones["c_foot_ik.l"].bone
                bpy.ops.pose.arp_switch_snap()
                bpy.ops.pose.select_all(action='DESELECT')
                break
        return {'FINISHED'}

# --------------------------------------------------------------------------------
classes = (
    MPM_OT_ClearTransform,
    MPM_OT_ARP_SNAPIKFK,
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)