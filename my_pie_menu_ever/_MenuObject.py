import bpy
from bpy.types import Panel, Menu, Operator
from . import _Util
from . import _AddonPreferences
from . import _MenuPose
# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Object Primary')
    c = box.column(align = True)
    _Util.layout_operator(c, _MenuPose.OT_ClearTransform.bl_idname, "Clear Pose Transform", isActive=_Util.is_armature_in_selected())
    _Util.layout_operator(c, "wiggle.reset", "Wiggle2: ResetPhysics") # if imported

# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    box = pie.split().box()
    box.label(text = 'Object Secondary')
    c = box.column(align = True)
    c.operator("import_scene.fbx", icon='IMPORT')
    c.operator("screen.userpref_show", icon='PREFERENCES')
    c.operator("wm.console_toggle", icon='CONSOLE')
    # box = root.split(factor=1.0).box()
# --------------------------------------------------------------------------------
classes = (
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)