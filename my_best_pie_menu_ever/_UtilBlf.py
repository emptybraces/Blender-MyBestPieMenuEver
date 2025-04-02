import bpy
import blf
import colorsys
import time
from math import sin
from . import _Util

FONT_SIZE_BASE = 20
FONT_SIZE_NORMAL = FONT_SIZE_BASE * 0.8
FONT_SIZE_INFO = FONT_SIZE_BASE * 0.55
FONT_SIZE_LABEL = FONT_SIZE_BASE * 0.7
COLOR_TITLE = [*colorsys.hsv_to_rgb(0.33, 0.5, 1), 0.8]
COLOR_NORMAL = [*colorsys.hsv_to_rgb(0, 0, 1), 0.8]
COLOR_VAR = [*colorsys.hsv_to_rgb(0.18, 0.8, 1), 0.4]
COLOR_LABEL = (*colorsys.hsv_to_rgb(0.35, 0.6, 1), 0.8)
COLOR_HIGHLIGHT = [*colorsys.hsv_to_rgb(0.0, 0.8, 1), 1.0]
COLOR_HIGHLIGHT_ACTIVE = [*colorsys.hsv_to_rgb(0.0, 0.6, 1), 0.8]
SHADOW = [6, 0, 0, 0, 1]  # The blur level (0, 3, 5) or outline (6).
SHADOW_OFS = [int(1), int(-1)]
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
        x += OFS_X_TITLE
        blf.clipping(fid, x, bpy.context.area.y, _Util.lerp(x, x + width, t), bpy.context.area.height)
    else:
        blf.disable(fid, blf.CLIPPING)


def draw_title(fid, text, x, y):
    x += OFS_X_TITLE

    blf.position(fid, x, y, 0)
    blf.color(fid, *COLOR_TITLE)
    blf.size(fid, FONT_SIZE_BASE)
    blf.draw(fid, "_" * (len(text) + 1))

    blf.enable(fid, blf.SHADOW)
    blf.shadow(fid, *SHADOW)
    blf.shadow_offset(fid, *SHADOW_OFS)
    blf.position(fid, x, y + 20, 0)
    blf.size(fid, FONT_SIZE_BASE)
    blf.draw(fid, text)


def draw_field(fid, field, var, desc, x, y, line_idx):
    xx = x + OFS_X_FIELD
    yy = y + OFS_Y_FIELD - line_idx * HEIGHT_FIELD
    blf.disable(fid, blf.SHADOW)
    blf.position(fid, xx, yy, 0)
    blf.color(fid, *COLOR_NORMAL)
    blf.size(fid, FONT_SIZE_NORMAL)
    blf.draw(fid, field)
    if var:
        varx = xx + blf.dimensions(fid, field)[0]
        draw_variable_str(fid, var, varx, yy)
    if desc:
        blf.position(fid, xx + OFS_X_INFO, yy + OFS_Y_INFO, 0)
        blf.color(fid, *COLOR_NORMAL)
        blf.size(fid, FONT_SIZE_INFO)
        blf.draw(fid, desc)


def draw_variable_str(fid, text, x, y):
    blf.position(fid, x, y, 0)
    blf.color(fid, COLOR_VAR[0], COLOR_VAR[1], COLOR_VAR[2], _Util.lerp(0.4, 1, (sin(time.time() * 10) + 1) / 2.0))
    blf.size(fid, FONT_SIZE_NORMAL)
    blf.draw(fid, text)


def draw_label(fid, text, x, y, align="left"):
    # これより上の関数はマウス位置が渡される前提の処理、修正する機会がもしあれば以下に統一する
    blf.size(fid, FONT_SIZE_LABEL)  # dimensionsの前
    if align == "center":
        x = x - blf.dimensions(fid, text)[0] / 2
    blf.enable(fid, blf.SHADOW)
    blf.shadow(fid, *SHADOW)
    blf.shadow_offset(fid, *SHADOW_OFS)
    blf.position(fid, x, y, 0)
    blf.color(fid, *COLOR_LABEL)
    blf.draw(fid, text)
    blf.disable(fid, blf.SHADOW)


def draw_key_info(fid, field, desc, x, y):
    blf.enable(fid, blf.SHADOW)
    blf.shadow(fid, *SHADOW)
    blf.position(fid, x, y, 0)
    blf.color(fid, *COLOR_NORMAL)
    blf.size(fid, FONT_SIZE_NORMAL)
    blf.draw(fid, field)

    blf.size(fid, FONT_SIZE_INFO)
    for i, s in enumerate(desc.splitlines()):
        blf.position(fid, x + OFS_X_INFO, y + OFS_Y_INFO - i * 10, 0)
        blf.draw(fid, s)
    blf.disable(fid, blf.SHADOW)


def draw_label_mousehover(fid, text, x, y, mx, my, width, height, active=False, hover_scale=1.0, align="left"):
    # エリア空間に変換
    mx = mx - bpy.context.area.x
    my = my - bpy.context.area.y
    is_in = x < mx < x + width and y < my < y + height
    blf.size(fid, FONT_SIZE_LABEL * (hover_scale if is_in else 1))  # dimensionsの前
    blf.enable(fid, blf.SHADOW)
    blf.shadow(fid, *SHADOW)
    blf.shadow_offset(fid, *SHADOW_OFS)
    if align == "center":
        x = (x + width/2) - (blf.dimensions(fid, text)[0]/2)
    blf.position(fid, x, y, 0)
    blf.color(fid, *COLOR_HIGHLIGHT if is_in else COLOR_HIGHLIGHT_ACTIVE if active else COLOR_LABEL)
    blf.draw(fid, text)
    # blf.position(fid, x + 100, y, 0)
    # blf.draw(fid, f"{x},{y} < {x + w},{y + h} | {mx},{my}")
    # blf.position(fid, x + 100, y-20, 0)
    # blf.draw(fid, f"{sx},{sy} | {mx},{my}")
    # blf.position(fid, x + 100, y-40, 0)
    # blf.draw(fid, f"mouse position = {pm}")
    blf.disable(fid, blf.SHADOW)
    return is_in


def draw_separator(fid, text, x, y):
    blf.position(fid, x, y, 0)
    blf.color(fid, *COLOR_TITLE)
    blf.size(fid, FONT_SIZE_BASE)
    blf.draw(fid, text)
