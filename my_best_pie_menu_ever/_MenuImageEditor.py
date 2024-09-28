import bpy
from . import _Util

# --------------------------------------------------------------------------------
# ImageEditorモードメニュー
# --------------------------------------------------------------------------------


def MenuPrimary(pie, context):
    pie = pie.split()
    box = pie.box()
    box.label(text="Image Editor")

    r = box.row()
    c = r.column(align=True)



# --------------------------------------------------------------------------------
classes = [
]


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
