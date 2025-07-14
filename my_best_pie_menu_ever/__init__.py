import bpy
import sys
import importlib
# fmt:off
modules = (
    "my_best_pie_menu_ever.g",
    "my_best_pie_menu_ever._Util",
    "my_best_pie_menu_ever._AddonPreferences",
    "my_best_pie_menu_ever._PieMenu",
)
for mod_name in modules:
    if mod_name in sys.modules:
        importlib.reload(sys.modules[mod_name])
    else:
        __import__(mod_name)
from . import g, _Util, _AddonPreferences,_PieMenu
bl_info = {
    "name": "My Best Pie Menu Ever",
    "author": "emptybraces",
    "version": (2, 7, 0),
    "blender": (4, 4, 3),
    "location": "3D View",
    "description": "Quick access to the functions you need",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}
# fmt:on
classes = (
    _AddonPreferences,
    _PieMenu,
    _Util,
)
cat_3dview = "3D View"
cat_image = "Image"
addon_opid = _PieMenu.MPM_OT_OpenPieMenuModal.bl_idname


def register_keymap(is_force, cate, spaceType):
    kmkmi = _Util.find_keymap(cate, addon_opid) if not is_force else (None, None)
    if kmkmi[1] == None:
        kc = bpy.context.window_manager.keyconfigs.addon
        if kc == None:
            return
        km = kc.keymaps.get(cate)
        # userkc = bpy.context.window_manager.keyconfigs.user.keymaps.get(
        #     cate)
        # for i in userkc.keymap_items:
        #     print(i.name, i.type)
        if not km:
            print(f"new keymap: {cate}")
            km = kc.keymaps.new(name=cate, space_type=spaceType)
        kmi = km.keymap_items.get(addon_opid)
        if not kmi:
            print(f"new keymap_items: {addon_opid}")
            kmi = km.keymap_items.new(addon_opid, "W", "PRESS")
        else:
            kmi.type = "W"
            kmi.value = "PRESS"
            kmi.shift = False
            kmi.ctrl = False
    else:
        pass


def unregister_keymap():
    kmkmi = _Util.find_keymap(cat_3dview, addon_opid)
    if kmkmi[1] is not None:
        kmkmi[0].keymap_items.remove(kmkmi[1])
    kmkmi = _Util.find_keymap(cat_image, addon_opid)
    if kmkmi[1] is not None:
        kmkmi[0].keymap_items.remove(kmkmi[1])


def register():
    register_keymap(False, cat_3dview, "VIEW_3D")
    register_keymap(False, cat_image, "IMAGE_EDITOR")
    for cls in classes:
        cls.register()
    # bpy.app.timers.register(init, first_interval=0.1)


def unregister():
    unregister_keymap()
    for cls in classes:
        cls.unregister()


# is_try = False


# def init():
#     print("mpm: try init")
#     for window in bpy.context.window_manager.windows:
#         for area in window.screen.areas:
#             if area.type == "VIEW_3D":
#                 _PieMenu.init()
#                 return None  # タイマー終了
#     # 1回だけ
#     if is_try:
#         return None
#     is_try = True
#     return 1  # ウェイト

# print(__name__)
# if __name__ == "__main__":
#    register()
