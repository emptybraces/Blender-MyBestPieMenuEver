import bpy

g_history = []
g_history_idx = 1
g_is_busy = False
# --------------------------------------------------------------------------------
# 選択履歴
# --------------------------------------------------------------------------------
def PanelHistory(pie, context):
    box = pie.split().box()
    box.prop(context.scene, "selection_history")

# --------------------------------------------------------------------------------
def on_selection_changed(context):
    global g_is_busy
    global g_history_idx
    if g_is_busy:
        # print("busy!")
        return
    ctx = bpy.context
    objs = ctx.selected_objects
    if not objs: return;
    bones = None
    if bpy.context.mode == 'POSE':
        bones = ctx.selected_pose_bones
    elif bpy.context.mode == 'EDIT_ARMATURE':
        # なんでか参照が永続化されないので必要なパラメータを抽出
        bones = [[(b.name, b.select, b.select_head, b.select_tail) for b in obj.data.edit_bones if b.select or b.select_head or b.select_tail] for obj in objs]
        # print("bones = ", bones)
    if 0 < len(g_history) and g_history[0]["objects"] == objs and (not bones or g_history[0]["bones"] == bones):
        # print("interrpt because same selection.")
        return
    # print(bpy.context.mode, objs, bones)
    max_count = 20
    if objs and 0 < len(objs):
        g_history_idx += 1
        item = {"no": g_history_idx, "objects":objs, "bones": bones, "mode": bpy.context.mode}
        g_history.insert(0, item)
        if max_count < len(g_history):
            del g_history[-1]
# --------------------------------------------------------------------------------
def get_history(self, context):
    r = []
    show_elems = 3
    for i in range(len(g_history)):
        no = g_history[i]["no"]
        objs = g_history[i]["objects"]
        bones = g_history[i]["bones"]
        mode = g_history[i]["mode"]
        s = f"{no} {mode} | "
        s += ", ".join([obj.name for obj in objs[:show_elems]]) if 1 < len(objs) else objs[0].name
        if (show_elems < len(objs)):
            s += "..."
        if bones and 0 < len(bones):
            s += " | "
            if mode == 'EDIT_ARMATURE':
                s += ", ".join([str(len(b)) for b in bones[:show_elems]]) + " editbones"
            else:
                s += ", ".join([obj.name for obj in bones[:show_elems]]) if 1 < len(bones) else bones[0].name
            if (show_elems < len(bones)):
                s += "..."
        r.append(
            (str(i), s, "", i)
        )
    return r

def set_history(self, value):
    global g_is_busy
    g_is_busy = True
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    objs = g_history[value]["objects"]
    bones = g_history[value]["bones"]
    mode = g_history[value]["mode"]
    # print("select", objs, bones)
    # objectの選択
    for o in objs:
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
    # boneの選択
    if mode == "POSE":
        bpy.ops.object.mode_set(mode = 'POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        for o in bones:
            o.bone.select = True
            bpy.context.object.data.bones.active = o.bone
    elif mode == "EDIT_ARMATURE":
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        for i, o in enumerate(objs):
            tuples = bones[i]
            # print(1, tuples)
            for eb, tpl in [(eb, tpl) for eb in o.data.edit_bones for tpl in tuples if eb.name == tpl[0]]:
                eb.select = tpl[1]
                eb.select_head = tpl[2]
                eb.select_tail = tpl[3]
                # bpy.context.object.data.edit_bones.active = eb
    g_is_busy = False
    # print("-----------------------------")
# --------------------------------------------------------------------------------

def register():
    bpy.app.handlers.depsgraph_update_post.append(on_selection_changed)
    bpy.types.Scene.selection_history = bpy.props.EnumProperty(items=get_history, set=set_history)

def unregister():
    global g_history
    global g_history_idx
    global g_is_busy
    bpy.app.handlers.depsgraph_update_post.remove(on_selection_changed)
    del bpy.types.Scene.selection_history
    g_history.clear()
    g_history_idx = 1
    g_is_busy = False