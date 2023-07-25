if "bpy" in locals():
    import imp
    imp.reload(_MenuRoot)
else:
    from . import _MenuRoot
import bpy
import rna_keymap_ui
from rna_prop_ui import PropertyPanel

addon_keymaps = []
class MT_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['3D View']
        for keymaps in addon_keymaps:
            col.context_pointer_set("keymap", keymaps[1])
            rna_keymap_ui.draw_kmi([], kc, km, keymaps[1], col, 0)

def registerKeyMap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS')
        kmi.properties.name = _MenuRoot.MT_Root.bl_idname
        addon_keymaps.append((km, kmi))
        
def unregisterKeyMap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    #kc = bpy.context.window_manager.keyconfigs.addon
    #if kc:
    #    for km, kmi in addon_keymaps:
    #        km.keymap_items.remove(kmi)
    #    for km in kc.keymaps:
    #        if km.name == "3D View":
    #            for kmi in km.keymap_items:
    #                if hasattr(kmi.properties, 'name') and kmi.properties.name == addon_id:
    #                    km.keymap_items.remove(kmi)
    #            break
    addon_keymaps.clear()

classes = (
    MT_AddonPreferences,
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    registerKeyMap()
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    unregisterKeyMap()
