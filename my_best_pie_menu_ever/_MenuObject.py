import bpy
from . import _Util
from . import _MenuWeightPaint

# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    pie = pie.split()
    box = pie.box()
    box.label(text = 'Object Primary')
    c = box.column(align = True)
     # if imported
    if "wiggle_2" in context.preferences.addons.keys():
        _Util.layout_operator(c, "wiggle.reset", "Wiggle2: ResetPhysics")
    _MenuWeightPaint.MirrorVertexGroup(c)

# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    box = pie.split().box()
    box.label(text = 'Object Secondary')
    c = box.column(align = True)
    # box = root.split(factor=1.0).box()
# --------------------------------------------------------------------------------
classes = (
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)