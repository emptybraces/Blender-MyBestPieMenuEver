import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util

# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    col_root = pie.split().column()

# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    col_root = pie.split().column()
    box = col_root.split(factor=1.0).box()
    box.label(text = 'File')
    box.operator("import_scene.fbx")
    box.operator("screen.userpref_show")

    # col_root.separator(factor=4.0)

    # box = col_root.split(factor=1.0).box()
    # box.label(text = 'File')
    # box.operator("import_scene.fbx")

    # col_root = pie.split().column()

    # box = col_root.split(factor=0.3).box()
    # box.label(text='File')
    # box.operator("import_scene.fbx")

    # col_root.separator(factor=4.0)


# --------------------------------------------------------------------------------
classes = (
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
