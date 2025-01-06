import bpy
import blf
import colorsys
import time
from math import sin
from . import _Util

FONT_SIZE_BASE = 20
FONT_SIZE_NORMAL = FONT_SIZE_BASE * 0.8
FONT_SIZE_INFO = FONT_SIZE_BASE * 0.7
COLOR_TITLE = colorsys.hsv_to_rgb(0.33, 0.5, 1)
COLOR_NORMAL = colorsys.hsv_to_rgb(0, 0, 1)
COLOR_VAR = colorsys.hsv_to_rgb(0.18, 0.8, 1)
ALPHA_BASE = 0.8
ALPHA_INFO = 0.7
OFS_X_TITLE = 60
OFS_X_FIELD = 65
OFS_Y_FIELD = -40
OFS_X_INFO = 260
LINE_HEIGHT = 25


def animate_clipping(fid, x, width, t):
    blf.enable(fid, blf.CLIPPING)
    t = min(1, t * 2)
    x += -bpy.context.area.x + OFS_X_TITLE
    blf.clipping(fid, x, bpy.context.area.y, _Util.lerp(x, x + width, t), bpy.context.area.height)


def draw_title(fid, text, x, y):
    x += -bpy.context.area.x + OFS_X_TITLE
    y += -bpy.context.area.y
    blf.position(fid, x, y, 0)
    blf.color(fid, COLOR_TITLE[0], COLOR_TITLE[1], COLOR_TITLE[2], ALPHA_BASE)
    blf.size(fid, FONT_SIZE_BASE)
    blf.draw(fid, "_" * (len(text) + 1))

    blf.enable(fid, blf.SHADOW)
    blf.shadow_offset(fid, int(1), int(-1))
    blf.position(fid, x, y + 20, 0)
    blf.size(fid, FONT_SIZE_BASE)
    blf.draw(fid, text)


def draw_variable_str(fid, text, x, y, idx):
    y += -bpy.context.area.y + OFS_Y_FIELD - idx * LINE_HEIGHT
    blf.position(fid, x, y, 0)
    blf.color(fid, COLOR_VAR[0], COLOR_VAR[1], COLOR_VAR[2], _Util.lerp(0.4, 1, (sin(time.time() * 10) + 1) / 2.0))
    blf.size(fid, FONT_SIZE_NORMAL)
    blf.draw(fid, text)


def draw_info(fid, text, x, y, idx):
    x += -bpy.context.area.x + OFS_X_INFO
    y += -bpy.context.area.y + OFS_Y_FIELD - idx * LINE_HEIGHT + 2
    blf.position(fid, x, y, 0)
    blf.color(fid, COLOR_NORMAL[0], COLOR_NORMAL[1], COLOR_NORMAL[2], ALPHA_INFO)
    blf.size(fid, FONT_SIZE_INFO)
    blf.draw(fid, text)


def draw_field(fid, field, var, info, x, y, idx):
    xx = x - bpy.context.area.x + OFS_X_FIELD
    yy = y - bpy.context.area.y + OFS_Y_FIELD - idx * LINE_HEIGHT
    blf.position(fid, xx, yy, 0)
    blf.color(fid, COLOR_NORMAL[0], COLOR_NORMAL[1], COLOR_NORMAL[2], ALPHA_BASE)
    blf.size(fid, FONT_SIZE_NORMAL)
    blf.draw(fid, field)
    if var:
        xx += blf.dimensions(fid, field)[0]
        draw_variable_str(fid, var, xx, y, idx)
    if info:
        draw_info(fid, info, x, y, idx)
