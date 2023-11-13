import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util
from . import _AddonPreferences
from . import _MenuPose
from . import _MenuWeightPaint

# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Object Primary')
    c = box.column(align = True)
    _Util.layout_operator(c, "wiggle.reset", "Wiggle2: ResetPhysics") # if imported
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