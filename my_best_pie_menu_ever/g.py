import bpy
import importlib
from typing import Callable
from . import (
    _UtilBlf,
)
for m in (
    _UtilBlf,
):
    importlib.reload(m)
ver = (2, 8, 0)
is_force_cancelled_piemenu_modal = False  # メニューモーダルの強制キャンセル。
is_request_reopen_piemenu = False  # パイメニュー再起動リクエスト
on_closed: dict[str, Callable[[], None]] = {}


def force_cancel_piemenu_modal(context):
    global is_force_cancelled_piemenu_modal
    is_force_cancelled_piemenu_modal = True
    context.area.tag_redraw()


def is_v4_3_later(): return (4, 3, 0) <= bpy.app.version
def is_unregistered(): return bpy.types.Scene.mpm_prop is None


# -------------------------------------
# stackable ui関係
space_view_command_display_start_stack = []


def space_view_command_display_begin_pos(id):
    x = bpy.context.area.width * 0.7
    y = _UtilBlf.LABEL_SIZE_Y * 4
    for i in space_view_command_display_start_stack:
        if i["id"] == id:
            return (x, y)
        y += i["y"]
        y += _UtilBlf.LABEL_SIZE_Y*2  # スペース
    return (x, 0)


def space_view_command_display_stack_height(id, y=0):
    global space_view_command_display_start_stack
    if y == 0:
        y = _UtilBlf.LABEL_SIZE_Y
    for i in space_view_command_display_start_stack:
        if i["id"] == id:
            i["y"] = y
            return
    space_view_command_display_start_stack.append({"id": id, "y": y})


def space_view_command_display_stack_remove(id):
    global space_view_command_display_start_stack
    space_view_command_display_start_stack = [x for x in space_view_command_display_start_stack if x["id"] != id]


# -------------------------------------
# msgbus関係
# -------------------------------------
history_objs_and_mode = [([None], ""), ([None], "")]


def on_mode_change():
    global prev_obj_and_mode
    obj = bpy.context.object
    active = bpy.context.active_object
    if obj:
        selected = [active] + [obj for obj in bpy.context.selected_objects if obj != active]
        history_objs_and_mode.insert(0, (selected, obj.mode))
        print(history_objs_and_mode[0])
        if 10 < len(history_objs_and_mode):
            history_objs_and_mode.pop()


def get_last_objs_and_mode():
    return history_objs_and_mode[1]


msgbus_owner = "mpm.g.on_mode_change"


def register():
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
