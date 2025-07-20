import bpy
import importlib
from bpy.app.handlers import persistent
from . import (
    _Util,
)
for m in (
    _Util,
):
    importlib.reload(m)
g_history = []
g_history_no = 1
g_history_current_no = -1
g_is_busy = False
# --------------------------------------------------------------------------------
# 選択履歴
# --------------------------------------------------------------------------------


def PanelHistory(layout, context):
    pass
    # layout.label(text="v4 dont work...")
    # layout.operator_menu_enum(MPM_OT_SelectionHistory.bl_idname, 'historyEnum')

# --------------------------------------------------------------------------------


class MPM_OT_SelectionHistory(bpy.types.Operator):
    bl_idname = "mpm.selection_history"
    bl_description = "selection history"
    bl_label = "Selection History"

    def get(self, context):
        global g_history_current_no
        r = []
        show_elems = 3
        for i in range(len(g_history)):
            no = g_history[i]["no"]
            objs = g_history[i]["objects"]
            data = g_history[i]["data"]
            mode = g_history[i]["mode"]
            if g_history_current_no == no:
                s = f"* {no} {mode} | "
            else:
                s = f"{no} {mode} | "
            if mode == 'PAINT_TEXTURE' and objs is None:
                s += "Brush Change " + data
            else:
                s += ", ".join([obj.name for obj in objs[:show_elems]]) if 1 < len(objs) else objs[0].name
                if (show_elems < len(objs)):
                    s += "..."
                if data and 0 < len(data):
                    s += " | "
                    if mode == 'EDIT_ARMATURE':
                        s += ", ".join([str(len(b)) for b in data[:show_elems]]) + " editbones"
                    else:
                        s += ", ".join([obj.name for obj in data[:show_elems]]) if 1 < len(data) else data[0].name
                    if (show_elems < len(data)):
                        s += "..."
            r.append((str(no), s, ""))
        return r

    historyEnum: bpy.props.EnumProperty(items=get)

    def execute(self, context):
        global g_is_busy
        global g_history
        global g_history_current_no
        identifiers = [str(values["no"]) for values in g_history]
        # print("self.historyEnum=", self.historyEnum)
        index = identifiers.index(self.historyEnum)
        # print("index=", index)
        objs = g_history[index]["objects"]
        data = g_history[index]["data"]
        mode = g_history[index]["mode"]
        g_history_current_no = g_history[index]["no"]
        # print("select", objs, data)
        # objectの選択
        if objs:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            for o in objs:
                o.select_set(True)
                bpy.context.view_layer.objects.active = o
        # texturepaintのbrushの選択
        if mode == "PAINT_TEXTURE":
            g_is_busy = True
            brushes = [b for b in bpy.data.brushes if b.use_paint_image and b.name == data]
            if 0 < len(brushes):
                context.tool_settings.image_paint.brush = brushes[0]
        # boneの選択
        elif mode == "POSE":
            g_is_busy = True
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')
            for o in data:
                o.bone.select = True
                bpy.context.object.data.bones.active = o.bone
        elif mode == "EDIT_ARMATURE":
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.select_all(action='DESELECT')
            for i, o in enumerate(objs):
                g_is_busy = True
                tuples = data[i]
                for eb, tpl in [(eb, tpl) for eb in o.data.edit_bones for tpl in tuples if eb.name == tpl[0]]:
                    eb.select = tpl[1]
                    eb.select_head = tpl[2]
                    eb.select_tail = tpl[3]
                    # bpy.context.object.data.edit_bones.active = eb
        else:
            g_is_busy = True
        return {'FINISHED'}
# --------------------------------------------------------------------------------


@persistent
def on_selection_changed(context):
    global g_is_busy
    global g_history_no
    global g_history_current_no
    if g_is_busy:
        g_is_busy = False
        return
    ctx = bpy.context
    objs = ctx.selected_objects
    # print(f"objs={objs}, mode={ctx.mode}")
    data = None
    is_register = objs and 0 < len(objs)
    if ctx.mode == 'PAINT_TEXTURE':
        data = ctx.tool_settings.image_paint.brush.name
        if 0 < len(g_history) and g_history[0]["data"] == data:
            return
        objs = None
        is_register = True
    elif ctx.mode == 'POSE':
        if not objs:
            return
        data = ctx.selected_pose_bones
        if 0 < len(g_history) and g_history[0]["objects"] == objs and (not data or g_history[0]["data"] == data):
            return
    elif ctx.mode == 'EDIT_ARMATURE':
        if not objs:
            return
        # なんでか参照が永続化されないので必要なパラメータを抽出
        data = [[(b.name, b.select, b.select_head, b.select_tail)
                 for b in obj.data.edit_bones if b.select or b.select_head or b.select_tail] for obj in objs]
        if 0 < len(g_history) and g_history[0]["objects"] == objs and (not data or g_history[0]["bones"] == data):
            return
    max_count = 20
    if is_register:
        g_history_no += 1
        item = {"no": g_history_no, "objects": objs, "data": data, "mode": ctx.mode}
        g_history.insert(0, item)
        if max_count < len(g_history):
            del g_history[-1]
        g_history_current_no = -1
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
classes = [
    MPM_OT_SelectionHistory,
]


def register():
    pass
    # bpy.app.handlers.depsgraph_update_post.append(on_selection_changed)
    # _Util.register_classes(classes)


def unregister():
    pass
    # _Util.unregister_classes(classes)
    # bpy.app.handlers.depsgraph_update_post.remove(on_selection_changed)
    # global g_history
    # global g_history_no
    # global g_history_current_no
    # global g_is_busy
    # g_history.clear()
    # g_history_no = 0
    # g_history_current_no = -1
    # g_is_busy = False
