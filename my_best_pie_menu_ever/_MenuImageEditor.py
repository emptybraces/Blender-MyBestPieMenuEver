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

    DrawTexutreInfo(c, context)

    # Apply
    box = box.box()
    box.label(text="Apply", icon="MODIFIER")


def DrawTexutreInfo(layout, context):
    image = context.area.spaces.active.image
    box = layout.box()
    box.label(text="Image Info")
    c = box.column(align=True)
    if image:
        r = c.row(align=True)
        r = r.row(align=True)
        if image.packed_file == None:
            r.operator("image.pack", text = "", icon="UGLYPACKAGE")
        else:
            r.operator("image.unpack", text = "", icon="PACKAGE")
        # r.label(icon="UGLYPACKAGE" if image.packed_file == None else "PACKAGE")
        r = r.row(align=True)
        r.active = image.packed_file == None
        r.scale_x = 3
        r.prop(image, "filepath_raw", text="")

        r = c.row(align=True)
        r.prop(image, "source", text="Source")
        r.label(text=f"{image.size[0]} x {image.size[1]}")
        r.prop(image.colorspace_settings, "name", text="")
    else:
        layout.label(text="No active image")


# --------------------------------------------------------------------------------
classes = [
]


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
