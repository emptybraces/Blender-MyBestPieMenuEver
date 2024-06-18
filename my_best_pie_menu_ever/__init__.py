# ---------------------------
# 1.3.4 - 頂点グループ追加ボタン。頂点マージボタンの修正。
# 1.3.3 - フォルダ名の変更
# 1.3.2 - blender_manifest更新
# 1.3.1 - BlenderExtension
# ---------------------------
bl_info = {
    "name": "MyBestPieMenuEVER",
    "author": "emptybraces",
    "version": (1, 3, 4),
    "blender": (4, 2, 0),
    "location": "3D View",
    "description": "My Best Pie Menu EVER!",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}
from . import g
g.ver = bl_info["version"]
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
