# ---------------------------
# 1.3.9 - 頂点複製ミラーを追加。未使用頂点グループの一括削除処理を追加。頂点グループ選択パネルに頂点数を表示。
# 1.3.8 - uesrキーマップスコープに'3D View'がないとき、エラーが発生するバグを修正。
# 1.3.7 - カラーパレットアクセス。3Dカーソルの選択頂点垂直ベクトル移動。
# 1.3.6 - 1.3.5のバグ修正。
# 1.3.5 - ビューポートカメラの位置角度保存復元ボタン。Pivotセット、シェーディングセットボタン説明追加。クリース編集ボタン。孤立を削除ボタン追加。ブラシ蓄積プロパティ追加。Smoothスカルプトブラシ強さの変更。頂点グループ選択処理をその場で繰り返し設定できるように修正。頂点クリース追加。辺クリース修正。
# 1.3.4 - 頂点グループ追加ボタン。頂点グループ選択ボタン。頂点マージボタンの修正。３Dカーソルをビュー平面上移動。選択オブジェクトのPRSコピー。
# 1.3.3 - フォルダ名の変更
# 1.3.2 - blender_manifest更新
# 1.3.1 - BlenderExtension
# ---------------------------
import bpy
from . import g
bl_info = {
    "name": "MyBestPieMenuEVER",
    "author": "emptybraces",
    "version": (1, 3, 9),
    "blender": (4, 2, 0),
    "location": "3D View",
    "description": "My Best Pie Menu EVER",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}
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
