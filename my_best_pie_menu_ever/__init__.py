# ---------------------------
# 1.3.5 - ビューポートカメラの位置角度保存復元ボタン。Pivotセット、シェーディングセットボタン説明追加。クリース編集ボタン。孤立を削除ボタン追加。ブラシ蓄積プロパティ追加。Smoothスカルプトブラシ強さの変更。頂点グループ選択処理をその場で繰り返し設定できるように修正。頂点クリース追加。辺クリース修正。
# 1.3.4 - 頂点グループ追加ボタン。頂点グループ選択ボタン。頂点マージボタンの修正。３Dカーソルをビュー平面上移動。選択オブジェクトのPRSコピー。
# 1.3.3 - フォルダ名の変更
# 1.3.2 - blender_manifest更新
# 1.3.1 - BlenderExtension
# ---------------------------
bl_info = {
    "name": "MyBestPieMenuEVER",
    "author": "emptybraces",
    "version": (1, 3, 5),
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
    imp.reload(_PieMenu)
else:
    from . import _Util
    from . import _AddonPreferences
    from . import _PieMenu
import bpy

classes = (
    _AddonPreferences,
    _PieMenu,
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
