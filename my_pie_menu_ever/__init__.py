bl_info = {
    "name": "MyPieMenuEVER",
    "author": "emptybraces",
    "version": (1, 0),
    "blender": (3, 5, 1),
    "location": "",
    "description": "My Pie Menu EVER!",
    "warning": "",
    "doc_url": "",
    "category": "",
}
if "bpy" in locals():
    import imp
    imp.reload(_Menu)
    imp.reload(_AddonPreferences)
else:
    from . import _Menu
    from . import _AddonPreferences
import bpy

classes = (
    _Menu,
    _AddonPreferences,
)

def register():
    for cls in classes:
        cls.register()
    
def unregister():
    for cls in classes:
        cls.unregister()

if __name__ == "__main__":
    register()
    bpy.ops.wm.call_menu_pie(name=_Menu.MT_Root.bl_idname)    

