if "bpy" in locals():
    import importlib
    importlib.reload(_Util)
else:
    from . import _Util
import bpy

# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------


def draw(pie, context):
    pie = pie.split()
    box = pie.box()
    box.label(text="Object")

    # select tool
    LayoutSwitchSelectionOperator(context, box)

    r = box.row()
    c = r.column(align=True)

    from ._MenuWeightPaint import MirrorVertexGroup, MPM_OT_Weight_RemoveUnusedVertexGroup
    MirrorVertexGroup(c, "VGroup Mirror")
    _Util.layout_operator(c, MPM_OT_Weight_RemoveUnusedVertexGroup.bl_idname, icon="X")
    from ._MenuEditMesh import MPM_OT_EditMesh_Ghost
    _Util.layout_operator(c, MPM_OT_EditMesh_Ghost.bl_idname, icon="GHOST_ENABLED")

    # if imported
    from ._MenuPose import draw_layout_3rdparty
    draw_layout_3rdparty(context, r)


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
