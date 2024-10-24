# ---------------------------
# 1.5.0 - ディレクトリオープンボタン追加。頂点グループオーバーレイボタンを追加。先頭にアンダースコアが付いているブラシ名に変更するとエラーが発生するバグを修正。スカルプトモード変更時に自動でワイヤーフレーム化するオプションを追加。頂点複製ミラーした頂点に各情報を全てコピーするように修正。UVMap選択リスト追加。Sculpt＋マスク遷移ボタン。UVEditorパイメニュー更新。直前のモード変更ボタンを追加。
# 1.4.1 - 頂点複製ミラーのバグ修正。ライセンスをGPL3.0に変更。
# 1.4.0 - 頂点複製ミラーを追加。未使用頂点グループの一括削除処理を追加。頂点グループ選択パネルに頂点数を表示。修正：ARPFKIP切り替えショートカットが動作していなかった。ウェイトペイントメニューにぼかしブラシ強さを常時表示。選択辺に沿ってボーン生成する機能を追加。スカルプトモードで選択した頂点をマスクする機能を追加。選択ツール切り替えボタン追加。頂点グループ選択パネル内にCLEAR SELECTIONボタンを追加。
# -
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
    "version": (1, 5, 0),
    "blender": (4, 2, 3),
    "location": "3D View",
    "description": "My Best Pie Menu EVER",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}
g.ver = bl_info["version"]

if "_Util" in locals():
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


cat_3dview = "3D View"
cat_image = "Image"
addon_opid = "op.mpm_open_pie_menu"


def find_keymap(keymapName, itemName):
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.get(keymapName)
    kmi = km.keymap_items.get(itemName) if km != None else None
    return (km, kmi)


def register_keymap(is_force, cate, spaceType):
    kmkmi = find_keymap(cate, addon_opid) if not is_force else (None, None)
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
    kmkmi = find_keymap(cat_3dview, addon_opid)
    if kmkmi[1] is not None:
        kmkmi[0].keymap_items.remove(kmkmi[1])
    kmkmi = find_keymap(cat_image, addon_opid)
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
