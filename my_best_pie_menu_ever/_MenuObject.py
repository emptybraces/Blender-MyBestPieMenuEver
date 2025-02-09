if "bpy" in locals():
    import importlib
    from . import _MenuPose
    from . import _MenuWeightPaint
    importlib.reload(_MenuPose)
    importlib.reload(_MenuWeightPaint)
else:
    from ._MenuWeightPaint import MirrorVertexGroup, MPM_OT_Weight_RemoveUnusedVertexGroup
    from ._MenuPose import MPM_OT_Pose_ARP_SnapIKFK
import bpy
from . import _Util

# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------


def MenuPrimary(pie, context):
    pie = pie.split()
    box = pie.box()
    box.label(text="Object")

    # select tool
    LayoutSwitchSelectionOperator(context, box)

    r = box.row()
    c = r.column(align=True)

    MirrorVertexGroup(c)
    _Util.layout_operator(c, MPM_OT_Weight_RemoveUnusedVertexGroup.bl_idname, icon="X")

    # if imported
    c = r.column(align=True)
    enabled_addons = context.preferences.addons.keys()
    if "wiggle_2" in enabled_addons:
        box = c.box()
        box.label(text="3rd Party Tool")
        _Util.layout_operator(box, "wiggle.reset", "Wiggle2: ResetPhysics")
    if any("auto_rig_pro" in i for i in enabled_addons):
        _Util.layout_operator(box, MPM_OT_Pose_ARP_SnapIKFK.bl_idname)

# --------------------------------------------------------------------------------


def LayoutSwitchSelectionOperator(context, layout):
    r = layout.row(align=True)
    r.label(text="SelectionTool")
    r = r.row(align=True)
    # r.scale_x = 0.5
    _Util.layout_operator(r, MPM_OT_SwitchSelectionToolTweak.bl_idname)
    _Util.layout_operator(r, MPM_OT_SwitchSelectionToolBox.bl_idname)
    _Util.layout_operator(r, MPM_OT_SwitchSelectionToolCircle.bl_idname)
    _Util.layout_operator(r, MPM_OT_SwitchSelectionToolLasso.bl_idname)


class MPM_OT_SwitchSelectionToolTweak(bpy.types.Operator):
    bl_idname = "mpm.switch_selection_tool_tweak"
    bl_label = "TWEAK"
    bl_description = "Tweak selection tool"

    @classmethod
    def poll(cls, context):
        return context.workspace.tools.from_space_view3d_mode(context.mode).idname != "builtin.select"

    def execute(self, context):
        bpy.ops.wm.tool_set_by_id(name="builtin.select")
        return {"FINISHED"}


class MPM_OT_SwitchSelectionToolBox(bpy.types.Operator):
    bl_idname = "mpm.switch_selection_tool_box"
    bl_label = "BOX"
    bl_description = "Box selection tool"

    @classmethod
    def poll(cls, context):
        return context.workspace.tools.from_space_view3d_mode(context.mode).idname != "builtin.select_box"

    def execute(self, context):
        bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
        return {"FINISHED"}


class MPM_OT_SwitchSelectionToolCircle(bpy.types.Operator):
    bl_idname = "mpm.switch_selection_tool_circle"
    bl_label = "CIRCLE"
    bl_description = "Circle selection tool"

    @classmethod
    def poll(cls, context):
        return context.workspace.tools.from_space_view3d_mode(context.mode).idname != "builtin.select_circle"

    def execute(self, context):
        bpy.ops.wm.tool_set_by_id(name="builtin.select_circle")
        return {"FINISHED"}


class MPM_OT_SwitchSelectionToolLasso(bpy.types.Operator):
    bl_idname = "mpm.switch_selection_tool_lasso"
    bl_label = "LASSO"
    bl_description = "Lasso selection tool"

    @classmethod
    def poll(cls, context):
        return context.workspace.tools.from_space_view3d_mode(context.mode).idname != "builtin.select_lasso"

    def execute(self, context):
        bpy.ops.wm.tool_set_by_id(name="builtin.select_lasso")
        return {"FINISHED"}



# --------------------------------------------------------------------------------
classes = [
    MPM_OT_SwitchSelectionToolTweak,
    MPM_OT_SwitchSelectionToolBox,
    MPM_OT_SwitchSelectionToolCircle,
    MPM_OT_SwitchSelectionToolLasso,
]


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
