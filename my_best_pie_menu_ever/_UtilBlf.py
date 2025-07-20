import bpy
import importlib
import blf
import colorsys
import time
from math import sin
from . import (
    _Util,
)
for m in (
    _Util,
):
    importlib.reload(m)
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


def animate_clipping(x, width, t):
    if t <= 1:
        blf.enable(0, blf.CLIPPING)
        t = min(1, t * 2)
        x += OFS_X_TITLE
        blf.clipping(0, x, bpy.context.area.y, _Util.lerp(x, x + width, t), bpy.context.area.height)
    else:
        blf.disable(0, blf.CLIPPING)


def draw_title(text, x, y):
    x += OFS_X_TITLE

    blf.position(0, x, y, 0)
    blf.color(0, *COLOR_TITLE)
    blf.size(0, FONT_SIZE_BASE)
    blf.draw(0, "_" * (len(text) + 1))

    blf.enable(0, blf.SHADOW)
    blf.shadow(0, *SHADOW)
    blf.shadow_offset(0, *SHADOW_OFS)
    blf.position(0, x, y + 20, 0)
    blf.size(0, FONT_SIZE_BASE)
    blf.draw(0, text)


def draw_field(field, var, desc, x, y, line_idx):
    xx = x + OFS_X_FIELD
    yy = y + OFS_Y_FIELD - line_idx * HEIGHT_FIELD
    blf.disable(0, blf.SHADOW)
    blf.position(0, xx, yy, 0)
    blf.color(0, *COLOR_NORMAL)
    blf.size(0, FONT_SIZE_NORMAL)
    blf.draw(0, field)
    if var:
        varx = xx + blf.dimensions(0, field)[0]
        draw_variable_str(var, varx, yy)
    if desc:
        blf.position(0, xx + OFS_X_INFO, yy + OFS_Y_INFO, 0)
        blf.color(0, *COLOR_NORMAL)
        blf.size(0, FONT_SIZE_INFO)
        blf.draw(0, desc)


def draw_variable_str(text, x, y):
    blf.position(0, x, y, 0)
    blf.color(0, COLOR_VAR[0], COLOR_VAR[1], COLOR_VAR[2], _Util.lerp(0.4, 1, (sin(time.time() * 10) + 1) / 2.0))
    blf.size(0, FONT_SIZE_NORMAL)
    blf.draw(0, text)


def draw_label_dimensions(text):
    blf.size(0, FONT_SIZE_LABEL)  # dimensionsの前
    return blf.dimensions(0, text)


LABEL_SIZE_Y = draw_label_dimensions("X")[1]


def draw_label(text, x, y, align="left", color=COLOR_LABEL):
    # これより上の関数はマウス位置が渡される前提の処理、修正する機会がもしあれば以下に統一する
    blf.size(0, FONT_SIZE_LABEL)  # dimensionsの前
    w, h = blf.dimensions(0, text)
    if align == "center":
        x = x - w / 2
    elif align == "right":
        x = x - w
    blf.enable(0, blf.SHADOW)
    blf.shadow(0, *SHADOW)
    blf.shadow_offset(0, *SHADOW_OFS)
    blf.position(0, x, y, 0)
    blf.color(0, *color)
    blf.draw(0, text)
    blf.disable(0, blf.SHADOW)
    return w, h


def draw_key_info(field, desc, x, y):
    blf.enable(0, blf.SHADOW)
    blf.shadow(0, *SHADOW)
    blf.position(0, x, y, 0)
    blf.color(0, *COLOR_NORMAL)
    blf.size(0, FONT_SIZE_NORMAL)
    blf.draw(0, field)

    blf.size(0, FONT_SIZE_INFO)
    for i, s in enumerate(desc.splitlines()):
        blf.position(0, x + OFS_X_INFO, y + OFS_Y_INFO - i * 10, 0)
        blf.draw(0, s)
    blf.disable(0, blf.SHADOW)


last_hover_time = {}
last_hover_key = ""


def is_mousehover_label(text, x, y, mx, my, w=0, h=0, align="left"):
    # エリア空間に変換
    mx = mx - bpy.context.area.x
    my = my - bpy.context.area.y
    blf.size(0, FONT_SIZE_LABEL)  # dimensionsの前
    ww, hh = blf.dimensions(0, text)
    w = w if 0 < w else ww
    h = h if 0 < h else hh
    if align == "center":
        x = x - w / 2
    elif align == "right":
        x = x - w
    ofs = 2
    is_in = x-ofs < mx < x + w + ofs and y-ofs < my < y + h + ofs
    return is_in


def draw_label_mousehover(text, desc, x, y, mx, my, w=0, h=0, active=False, hover_scale=1.0, align="left"):
    # エリア空間に変換
    mx = mx - bpy.context.area.x
    my = my - bpy.context.area.y
    blf.size(0, FONT_SIZE_LABEL)  # dimensionsの前
    ww, hh = blf.dimensions(0, text)
    w = w if 0 < w else ww
    h = h if 0 < h else hh
    if align == "center":
        x = x - w / 2
    elif align == "right":
        x = x - w
    ofs = 2
    is_in = x-ofs < mx < x + w + ofs and y-ofs < my < y + h + ofs
    if is_in and hover_scale != 1.0:
        blf.size(0, FONT_SIZE_LABEL * hover_scale)  # dimensionsの前
    blf.enable(0, blf.SHADOW)
    blf.shadow(0, *SHADOW)
    blf.shadow_offset(0, *SHADOW_OFS)
    blf.position(0, x, y, 0)
    blf.color(0, *COLOR_HIGHLIGHT if is_in else COLOR_HIGHLIGHT_ACTIVE if active else COLOR_LABEL)
    blf.draw(0, text)
    # blf.position(0, x + 100, y, 0)
    # blf.draw(0, f"{x},{y} < {x + w},{y + h} | {mx},{my}")
    # blf.position(0, x + 100, y-20, 0)
    # blf.draw(0, f"{sx},{sy} | {mx},{my}")
    # blf.position(0, x + 100, y-40, 0)
    # blf.draw(0, f"mouse position = {pm}")
    global last_hover_key
    if desc != "":
        key = f"{text}{int(x)}{int(y)}"
        if is_in:
            if last_hover_key != key or (last_hover_key == key and key not in last_hover_time):
                last_hover_time[key] = time.time()
            elif 0.3 < time.time() - last_hover_time.get(key, 0):
                blf.size(0, FONT_SIZE_INFO)
                ww, _ = blf.dimensions(0, desc)
                mx -= max(0, (mx + ww + 50) - bpy.context.area.width)
                blf.position(0, mx, y - 15, 0)
                blf.color(0, *COLOR_NORMAL)
                blf.draw(0, desc)
            last_hover_key = key
        else:
            last_hover_time.pop(key, None)
    blf.disable(0, blf.SHADOW)
    return is_in


def draw_separator(text, x, y):
    blf.position(0, x, y, 0)
    blf.color(0, *COLOR_TITLE)
    blf.size(0, FONT_SIZE_BASE)
    blf.draw(0, text)
