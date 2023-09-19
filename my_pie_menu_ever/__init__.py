bl_info = {
    "name": "MyBestPieMenuEVER",
    "author": "emptybraces",
    "version": (1, 0),
    "blender": (3, 6, 1),
    "location": "3D View",
    "description": "My Best Pie Menu EVER!",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}
if "bpy" in locals():
    import imp
    imp.reload(_Util)
    imp.reload(_AddonPreferences)
    imp.reload(_MenuRoot)
else:
    from . import _Util
    from . import _AddonPreferences
    from . import _MenuRoot
import bpy

classes = (
    _AddonPreferences,
    _MenuRoot,
    _Util,
)

def register():
    for cls in classes:
        cls.register()
    
def unregister():
    for cls in classes:
        cls.unregister()

if __name__ == "__main__":
    register()
    #bpy.ops.wm.call_menu_pie(name=_MenuRoot.MT_Root.bl_idname)    
