if "bpy" in locals():
    import importlib
    for m in (
        _Util,
        g,
        _AddonPreferences,
    ):
        importlib.reload(m)
else:
    import bpy
    from . import (
        _Util,
        g,
        _AddonPreferences,
    )
from bpy.app.translations import pgettext_iface as iface_


def draw_pie_menu(layout, context):
    r = layout.row(align=True)
    r.scale_x = 1.2
    r.enabled = 1 < len(history_objs_and_mode)
    for i in reversed(range(len(history_objs_and_mode))):
        sels, mode = history_objs_and_mode[i]
        try:
            for sel in sels:
                _ = sel.name
        except ReferenceError:
            del history_objs_and_mode[i]
    r.popover(panel=MPM_PT_ModeHistory_HistoryPopover.bl_idname, icon="KEY_MENU")


class MPM_OT_ModeHistory_ChangePrevMode(bpy.types.Operator):
    bl_idname = "mpm.mode_change_last"
    bl_label = "Change Mode to last"
    bl_options = {"UNDO"}
    select_idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return get_last_objs_and_mode()[0] != None

    def execute(self, context):
        global enable_history
        enable_history = False
        sels, mode = history_objs_and_mode[self.select_idx]
        if bpy.context.view_layer.objects.active:
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        _Util.select_active(sels[0])
        for i in sels[1:]:
            _Util.select_add(i)
        bpy.ops.object.mode_set(mode=mode)
        return {"FINISHED"}


class MPM_PT_ModeHistory_HistoryPopover(bpy.types.Panel):
    bl_idname = "MPM_PT_mode_history_popover"
    bl_label = "Mode History"
    bl_space_type = "TOPBAR"  # ポップオーバー専用の空間
    bl_region_type = "WINDOW"
    bl_ui_units_x = 30  # 横幅

    def draw(self, context):
        c = self.layout.column(align=True)
        try:
            for i, (sels, mode) in enumerate(history_objs_and_mode[1:], start=1):
                # アクティブオブジェクトが生存中なら、
                if sels[0] is not None:
                    safe_sels = [i for i in sels if i != None]
                    r = c.row()
                    r.alignment = "LEFT"
                    cnt = len(safe_sels)
                    msg = f"{i}.{mode} | {self.middle_truncate(sels[0].name)}"
                    if 1 < cnt:
                        msg += f", {self.middle_truncate(sels[1].name)}"
                    if 2 < cnt:
                        msg += f", and {cnt-2} objs"
                    _Util.layout_operator(r, MPM_OT_ModeHistory_ChangePrevMode.bl_idname, msg).select_idx = i
        except Exception as e:
            print(2, e)

    def middle_truncate(self, text, max_length=20):
        if len(text) <= max_length:
            return text

        ellipsis = "..."
        keep = max_length - len(ellipsis)
        head_len = keep // 2
        tail_len = keep - head_len
        return text[:head_len] + ellipsis + text[-tail_len:]


msgbus_owner = "mpm.g.on_mode_change"
history_objs_and_mode = []
enable_history = True


def on_mode_change():
    global prev_obj_and_mode
    obj = bpy.context.object
    active = bpy.context.active_object
    if obj:
        selected = [active] + [obj for obj in bpy.context.selected_objects if obj != active]
        history_objs_and_mode.insert(0, (selected, obj.mode))
        print(history_objs_and_mode[0])
        if _AddonPreferences.get_data().modeHistoryLimit < len(history_objs_and_mode):
            history_objs_and_mode.pop()


def get_last_objs_and_mode():
    return history_objs_and_mode[1]


classes = (
    MPM_OT_ModeHistory_ChangePrevMode,
    MPM_PT_ModeHistory_HistoryPopover,
)


def register():
    _Util.register_classes(classes)

    def __register_safe_msgbus():
        bpy.msgbus.subscribe_rna(
            key=(bpy.types.Object, "mode"),
            owner=msgbus_owner,
            args=(),
            notify=on_mode_change,
        )
    bpy.app.timers.register(__register_safe_msgbus, persistent=True)


def unregister():
    bpy.msgbus.clear_by_owner(msgbus_owner)
    _Util.unregister_classes(classes)
