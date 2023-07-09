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

import copy
import bpy
from bpy.types import Panel

# --------------------------------------------------------------------------------
class DeleteUnusedVertexAdditionalButton(bpy.types.Panel):
    bl_label = "Helper"
    bl_idname = "DATA_PT_add_button"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("mesh.delete_vertex_group")
        row.operator("mesh.delete_all_vertex_group")
# --------------------------------------------------------------------------------
# class CustomPreferences(bpy.types.AddonPreferences):
#     bl_idname = "CustomPreferences"
#     def draw(self, context):
#         layout = self.layout
#         box = layout.box()
#         box.label(text="Test")

classes = (
    DeleteUnusedVertexAdditionalButton,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    _Menu.register()
    _AddonPreferences.register()
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    _Menu.unregister()
    _AddonPreferences.unregister()

if __name__ == "__main__":
    register()
    bpy.ops.wm.call_menu_pie(name=_Menu.MT_Root.bl_idname)    

