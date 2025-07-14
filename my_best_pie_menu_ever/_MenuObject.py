import bpy
import sys
import importlib
from bpy.app.translations import pgettext_iface as iface_
# fmt:off
modules = (
    "my_best_pie_menu_ever._Util",
)
for mod_name in modules:
    if mod_name in sys.modules:
        importlib.reload(sys.modules[mod_name])
    else:
        __import__(mod_name)
from . import _Util
# fmt:on
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
    # s = layout.row().split(factor=0.25, align=True)
    r = layout.row(align=True)
    r1 = r2 = r
    # r1 = s.row()
    # r2 = s.row(align=True)
    r1.label(text=iface_("Selection Tool"))
    _Util.layout_operator(r2, MPM_OT_SwitchSelectionToolTweak.bl_idname)
    _Util.layout_operator(r2, MPM_OT_SwitchSelectionToolBox.bl_idname)
    _Util.layout_operator(r2, MPM_OT_SwitchSelectionToolCircle.bl_idname)
    _Util.layout_operator(r2, MPM_OT_SwitchSelectionToolLasso.bl_idname)


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
