if "bpy" in locals():
    import imp
    imp.reload(_MenuRoot)
    imp.reload(_Util)
else:
    from . import _MenuRoot
    from . import _Util
import bpy
import rna_keymap_ui
from rna_prop_ui import PropertyPanel
from bpy.props import IntProperty, IntVectorProperty, StringProperty

addon_keymaps = []
class MT_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    pass_addon: StringProperty(
        name="Addon Pass",
    )
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "pass_addon")
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['3D View']
        for keymaps in addon_keymaps:
            box.context_pointer_set("keymap", keymaps[1])
            rna_keymap_ui.draw_kmi([], kc, km, keymaps[1], box, 0)

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
    _Util.register_classes(classes)
    registerKeyMap()
    
def unregister():
    _Util.unregister_classes(classes)
    unregisterKeyMap()
