if "bpy" in locals():
    import imp
    imp.reload(_AddonPreferences)
    imp.reload(_Util)
    imp.reload(_MenuPose)
else:
    from . import _AddonPreferences
    from . import _Util
    from . import _MenuPose
import bpy
from bpy.types import Panel, Menu, Operator
# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def MenuPrimary(pie, context):
    box = pie.split().box()
    box.label(text = 'Object')
    _Util.layout_operator(box, _MenuPose.OT_ClearTransform.bl_idname, "Clear Pose Transform", isActive=_Util.is_armature_in_selected())
    _Util.layout_operator(box, "wiggle.reset", "Wiggle2: ResetPhysics") # if imported

# --------------------------------------------------------------------------------
def MenuSecondary(pie, context):
    root = pie.split().row()
    box = root.split(factor=1.0).box()
    box.label(text = 'File')
    box.operator("import_scene.fbx")
    box.operator("screen.userpref_show")
    # box = root.split(factor=1.0).box()
# --------------------------------------------------------------------------------
classes = (
)
def register():
    _Util.register_classes(classes)
def unregister():
    _Util.unregister_classes(classes)