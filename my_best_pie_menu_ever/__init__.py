if "bpy" in locals():
    import importlib
    importlib.reload(g)
    importlib.reload(_Util)
    importlib.reload(_AddonPreferences)
else:
    from . import g
    from . import _Util
    from . import _AddonPreferences
import bpy
bl_info = {
    "name": "My Best Pie Menu Ever",
    "author": "emptybraces",
    "version": (2, 2, 0),
    "blender": (4, 2, 0),
    "location": "3D View",
    "description": "Quick access to the functions you need",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}
# フォーマッタの都合上インポートを後にしてる
g.ver = bl_info["version"]
if "_PieMenu" in locals():
    import importlib
    importlib.reload(_PieMenu)
else:
    from . import _PieMenu

classes = [
    _AddonPreferences,
    _PieMenu,
    _Util,
]
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


def unregister():
    unregister_keymap()
    for cls in classes:
        cls.unregister()


if __name__ == "__main__":
    register()
