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


def is_unregistered(): bpy.types.Scene.mpm_prop is None
