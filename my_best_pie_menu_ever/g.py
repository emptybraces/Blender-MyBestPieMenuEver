import bpy
is_force_cancelled_piemenu_modal = False  # メニューモーダルの強制キャンセル。
is_request_reopen_piemenu = False  # パイメニュー再起動リクエスト

def force_cancel_piemenu_modal(context):
    global is_force_cancelled_piemenu_modal
    is_force_cancelled_piemenu_modal = True
    context.area.tag_redraw()

def is_v4_3_later(): return (4, 3, 0) <= bpy.app.version
