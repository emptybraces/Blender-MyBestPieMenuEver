import bpy
from bpy.types import Panel, Menu, Operator
from rna_prop_ui import PropertyPanel
from bpy.app.translations import (
    pgettext_iface as iface_,
    pgettext_tip as tip_,
    contexts as i18n_contexts,
)
class OT_InvertValue(bpy.types.Operator):
    bl_idname = "op.invert_value"
    bl_label = ""
    propName: bpy.props.StringProperty()
    def execute(self, context):
        target = getattr(context, self.propName, None)
        setattr(target, self.propName, not getattr(target, self.propName))
        return {'FINISHED'}
    @staticmethod
    def operator(layout, label, propName, targetObj, isActive = True, ctxt = ''):
        layout.context_pointer_set(name=propName, data=targetObj)
        op = layout.operator(OT_InvertValue.bl_idname, text=label, text_ctxt =ctxt, depress=layout.active and getattr(targetObj, propName, False))
        op.propName = propName
        layout.enabled = isActive and targetObj != None
# --------------------------------------------------------------------------------
def show_enum_values(obj, prop_name):
    print([item.identifier for item in obj.bl_rna.properties[prop_name].enum_items])
def enum_values(obj, prop_name):
    return [item.identifier for item in obj.bl_rna.properties[prop_name].enum_items]
def layout_prop_noneable(layout, target, prop, text=None, expand=False):
    if target != None:
        layout.prop(target, prop, text=text, expand=expand)
    else:
        layout.label(text='None')
# --------------------------------------------------------------------------------
classes = (
    OT_InvertValue,
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
