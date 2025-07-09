if "bpy" in locals():
    import importlib
    importlib.reload(_UtilBlf)
else:
    from . import _UtilBlf
import bpy
import os
import json
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


config_data = {}


def get_config_path():
    config_dir = bpy.utils.user_resource("CONFIG", path="", create=True)
    return os.path.join(config_dir, "my_best_pie_menu_ever_config.json")


def get_config():
    global config_data
    if config_data:
        return config_data
    try:
        path = get_config_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        else:
            config_data = {}
    except (json.JSONDecodeError, OSError) as e:
        print(f"[MyBestPieMenuEver] Failed to load config file: {e}")
    return config_data


def save_config():
    try:
        path = get_config_path()
        with open(path, "w", encoding="utf-8") as f:
            config_data["last_saved_version"] = ver
            json.dump(config_data, f, indent=2)
    except (OSError, TypeError) as e:
        print(f"[MyBestPieMenuEver] Failed to save config file:: {e}")


def get_config_brush_params(key):
    c = get_config()
    if "brush_params" in c:
        return c["brush_params"].get(key, None)
    return None
