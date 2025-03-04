import bpy
import blf
import colorsys
import time
from math import sin
from . import _Util

FONT_SIZE_BASE = 20
FONT_SIZE_NORMAL = FONT_SIZE_BASE * 0.8
FONT_SIZE_INFO = FONT_SIZE_BASE * 0.55
FONT_SIZE_MSG = FONT_SIZE_BASE * 0.7
COLOR_TITLE = (*colorsys.hsv_to_rgb(0.33, 0.5, 1), 0.8)
COLOR_NORMAL = (*colorsys.hsv_to_rgb(0, 0, 1), 0.8)
COLOR_VAR = (*colorsys.hsv_to_rgb(0.18, 0.8, 1), 0.4)
COLOR_LABEL = (*colorsys.hsv_to_rgb(0.35, 0.5, 1), 0.6)
COLOR_HIGHLIGHT = (*colorsys.hsv_to_rgb(0.2, 0.6, 1), 0.8)
OFS_X_TITLE = 60
OFS_X_FIELD = 65
OFS_Y_FIELD = -40
OFS_X_INFO = 10
OFS_Y_INFO = -16
HEIGHT_FIELD = 50


def animate_clipping(fid, x, width, t):
    if t <= 1:
        blf.enable(fid, blf.CLIPPING)
        t = min(1, t * 2)
        x += -bpy.context.area.x + OFS_X_TITLE
        blf.clipping(fid, x, bpy.context.area.y, _Util.lerp(x, x + width, t), bpy.context.area.height)
    else:
        blf.disable(fid, blf.CLIPPING)


def draw_title(fid, text, x, y):
    x += -bpy.context.area.x + OFS_X_TITLE
    y += -bpy.context.area.y
    x = _Util.clamp(x, 0, bpy.context.area.width)
    y = _Util.clamp(y, 0, bpy.context.area.height)

    blf.position(fid, x, y, 0)
    blf.color(fid, *COLOR_TITLE)
    blf.size(fid, FONT_SIZE_BASE)
    blf.draw(fid, "_" * (len(text) + 1))

    blf.enable(fid, blf.SHADOW)
    blf.shadow_offset(fid, int(1), int(-1))
    blf.position(fid, x, y + 20, 0)
    blf.size(fid, FONT_SIZE_BASE)
    blf.draw(fid, text)


def draw_variable_str(fid, text, x, y):
    x = _Util.clamp(x, 0, bpy.context.area.width)
    y = _Util.clamp(y, 0, bpy.context.area.height)
    blf.position(fid, x, y, 0)
    blf.color(fid, COLOR_VAR[0], COLOR_VAR[1], COLOR_VAR[2], _Util.lerp(0.4, 1, (sin(time.time() * 10) + 1) / 2.0))
    blf.size(fid, FONT_SIZE_NORMAL)
    blf.draw(fid, text)


def draw_info(fid, text, x, y):
    x = _Util.clamp(x, 0, bpy.context.area.width)
    y = _Util.clamp(y, 0, bpy.context.area.height)
    blf.position(fid, x, y, 0)
    blf.color(fid, *COLOR_NORMAL)
    blf.size(fid, FONT_SIZE_INFO)
    blf.draw(fid, text)


def draw_field(fid, field, var, info, x, y, idx):
    xx = x - bpy.context.area.x + OFS_X_FIELD
    yy = y - bpy.context.area.y + OFS_Y_FIELD - idx * HEIGHT_FIELD
    xx = _Util.clamp(xx, 0, bpy.context.area.width)
    yy = _Util.clamp(yy, 0, bpy.context.area.height)
    blf.disable(fid, blf.SHADOW)
    blf.position(fid, xx, yy, 0)
    blf.color(fid, *COLOR_NORMAL)
    blf.size(fid, FONT_SIZE_NORMAL)
    blf.draw(fid, field)
    if var:
        varx = xx + blf.dimensions(fid, field)[0]
        draw_variable_str(fid, var, varx, yy)
    if info:
        infox = xx + OFS_X_INFO
        infoy = yy + OFS_Y_INFO
        draw_info(fid, info, infox, infoy)


def draw_label(fid, text, x, y, align="left"):
    # 座標(0, 0)は今のエリアでの一番左下。
    # マウスの取得座標はBlenderウィンドウでの絶対値。
    blf.size(fid, FONT_SIZE_MSG)
    if align == "center":
        xx = x - bpy.context.area.x - blf.dimensions(fid, text)[0] / 2
    else:
        xx = x - bpy.context.area.x
    yy = y - bpy.context.area.y
    xx = _Util.clamp(xx, 0, bpy.context.area.width)
    yy = _Util.clamp(yy, 0, bpy.context.area.height)
    blf.enable(fid, blf.SHADOW)
    blf.shadow_offset(fid, int(1), int(-1))
    blf.position(fid, xx, yy, 0)
    blf.color(fid, *COLOR_LABEL)
    blf.draw(fid, text)
    blf.disable(fid, blf.SHADOW)


def draw_label_click_handler(fid, text, x, y, pmi, pm):
    blf.size(fid, FONT_SIZE_MSG)
    w, h = blf.dimensions(fid, text)
    sx = x - pmi.x + bpy.context.area.x # ラベル位置補正を無視し、ウィンドウ絶対値に変換
    sy = y - pmi.y + bpy.context.area.y
    mx = pm.x - pmi.x # ラベル位置補正を無視して統一。もともとevent.mouse.xはウィンドウ絶対値
    my = pm.y - pmi.y
    is_in = sx < mx < sx + w and sy < my < sy + h
    blf.enable(fid, blf.SHADOW)
    blf.shadow_offset(fid, int(1), int(-1))
    blf.position(fid, x, y, 0)
    blf.color(fid, *COLOR_HIGHLIGHT if is_in else COLOR_LABEL)
    blf.draw(fid, text)
    # blf.position(fid, x + 100, y, 0)
    # blf.draw(fid, f"{x},{y} < {x + w},{y + h} | {mx},{my}")
    # blf.position(fid, x + 100, y-20, 0)
    # blf.draw(fid, f"{sx},{sy} | {mx},{my}")
    # blf.position(fid, x + 100, y-40, 0)
    # blf.draw(fid, f"mouse position = {pm}")
    blf.disable(fid, blf.SHADOW)
