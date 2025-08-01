import bpy
import importlib
bl_info = {
    "name": "My Best Pie Menu Ever debug",
    "author": "emptybraces",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "location": "3D View",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

addon_name = "my_best_pie_menu_ever"
addon_path = "C:/user/projects/github_blender_MyBestPieMenuEver/my_best_pie_menu_ever.zip"


class OT_ReinstallAddon(bpy.types.Operator):
    bl_idname = "mpm_debug.reinstall"
    bl_label = "Reinstall Addon"

    def execute(self, context):
        exist_module = False
        global addon_name
        if addon_name in context.preferences.addons.keys():
            # if "my_pie_menu_ever._AddonPreferences" in sys.modules:
            # from addon_name import _AddonPreferences
            _AddonPreferences = importlib.import_module(f"{addon_name}._AddonPreferences")
            # print(module)
            if _AddonPreferences:
                ref = _AddonPreferences.Accessor.get_ref()
                if ref:
                    exist_module = True
                    self.dict = ref.dict()
            bpy.ops.preferences.addon_disable(module=addon_name)
            bpy.ops.preferences.addon_remove(module=addon_name)
            bpy.ops.preferences.addon_refresh()
        # インストール
        bpy.ops.preferences.addon_install(filepath=addon_path)
        bpy.ops.preferences.addon_refresh()

        # 再度検索
        bpy.ops.preferences.addon_enable(module=addon_name)
        bpy.ops.preferences.addon_refresh()
        if exist_module:
            # print("---------------")
            # print(addon_name)
            # print(bpy.context.preferences.addons.keys())
            # print(bpy.context.preferences.addons[addon_name].preferences)
            # print("---------------")
            _AddonPreferences = importlib.import_module(f"{addon_name}._AddonPreferences")
            _AddonPreferences.Accessor.get_ref().dict_apply(self.dict)
            self.dict = None

        # エラーが出るので、printに変えた
        # def draw(self, context):
        #     self.layout.label(text="reinstalled!")
        # context.window_manager.popup_menu(draw)
        self.report({"INFO"}, "[My Best Pie Menu Ever] reinstalled")
        return {"FINISHED"}


classes = (
    OT_ReinstallAddon,
)
addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(OT_ReinstallAddon.bl_idname, "W", "PRESS", ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
