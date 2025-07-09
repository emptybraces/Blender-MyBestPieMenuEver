if "bpy" in locals():
    import importlib
    importlib.reload(_Util)
    importlib.reload(_MenuImageEditor)
else:
    from . import _Util
    from . import _MenuImageEditor
import bpy

# --------------------------------------------------------------------------------
# UVEditorモードメニュー
# --------------------------------------------------------------------------------


def draw(pie, context):
    pie = pie.split()
    box = pie.box()
    box.label(text="UV Editor")

    # select tool
    LayoutSwitchSelectionOperator(context, box)

    r = box.row()
    c = r.column(align=True)

    _MenuImageEditor.DrawTexutreInfo(c, context)
    _MenuImageEditor.DrawSimilarTexutreNameList(r, context)


def LayoutSwitchSelectionOperator(context, layout):
    r = layout.row(align=True)
    r.label(text="SelectionTool")
    r = r.row(align=True)
    # r.scale_x = 0.5
    _Util.layout_operator(r, MPM_OT_UVMenuSwitchSelectionToolTweak.bl_idname)
    _Util.layout_operator(r, MPM_OT_UVMenuSwitchSelectionToolBox.bl_idname)
    _Util.layout_operator(r, MPM_OT_UVMenuSwitchSelectionToolCircle.bl_idname)
    _Util.layout_operator(r, MPM_OT_UVMenuSwitchSelectionToolLasso.bl_idname)


class MPM_OT_UVMenuSwitchSelectionToolTweak(bpy.types.Operator):
    bl_idname = "mpm.uvmenu_switch_selection_tool_tweak"
    bl_label = "TWEAK"
    bl_description = "Tweak selection tool"

    @classmethod
    def poll(cls, context):
        mode = context.workspace.tools.from_space_image_mode(context.space_data.mode)
        if mode == None:
            return True
        return mode.idname != "builtin.select"

    def execute(self, context):
        bpy.ops.wm.tool_set_by_id(name="builtin.select")
        return {"FINISHED"}


class MPM_OT_UVMenuSwitchSelectionToolBox(bpy.types.Operator):
    bl_idname = "mpm.uvmenu_switch_selection_tool_box"
    bl_label = "BOX"
    bl_description = "Box selection tool"

    @classmethod
    def poll(cls, context):
        mode = context.workspace.tools.from_space_image_mode(context.space_data.mode)
        if mode == None:
            return True
        return mode.idname != "builtin.select_box"

    def execute(self, context):
        bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
        return {"FINISHED"}


class MPM_OT_UVMenuSwitchSelectionToolCircle(bpy.types.Operator):
    bl_idname = "mpm.uvmenu_switch_selection_tool_circle"
    bl_label = "CIRCLE"
    bl_description = "Circle selection tool"

    @classmethod
    def poll(cls, context):
        mode = context.workspace.tools.from_space_image_mode(context.space_data.mode)
        if mode == None:
            return True
        return mode.idname != "builtin.select_circle"

    def execute(self, context):
        bpy.ops.wm.tool_set_by_id(name="builtin.select_circle")
        return {"FINISHED"}


class MPM_OT_UVMenuSwitchSelectionToolLasso(bpy.types.Operator):
    bl_idname = "mpm.uvmenu_switch_selection_tool_lasso"
    bl_label = "LASSO"
    bl_description = "Lasso selection tool"

    @classmethod
    def poll(cls, context):
        mode = context.workspace.tools.from_space_image_mode(context.space_data.mode)
        if mode == None:
            return True
        return mode.idname != "builtin.select_lasso"

    def execute(self, context):
        bpy.ops.wm.tool_set_by_id(name="builtin.select_lasso")
        return {"FINISHED"}


# --------------------------------------------------------------------------------
classes = [
    MPM_OT_UVMenuSwitchSelectionToolTweak,
    MPM_OT_UVMenuSwitchSelectionToolBox,
    MPM_OT_UVMenuSwitchSelectionToolCircle,
    MPM_OT_UVMenuSwitchSelectionToolLasso,
]


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
