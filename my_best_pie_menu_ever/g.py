if "bpy" in locals():
    import importlib
    importlib.reload(_UtilBlf)
else:
    from . import _UtilBlf
import bpy
from typing import Callable

is_force_cancelled_piemenu_modal = False  # メニューモーダルの強制キャンセル。
is_request_reopen_piemenu = False  # パイメニュー再起動リクエスト
on_closed: dict[str, Callable[[], None]] = {}


def force_cancel_piemenu_modal(context):
    global is_force_cancelled_piemenu_modal
    is_force_cancelled_piemenu_modal = True
    context.area.tag_redraw()


def is_v4_3_later(): return (4, 3, 0) <= bpy.app.version


def is_unregistered(): return bpy.types.Scene.mpm_prop is None


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
