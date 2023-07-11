if "bpy" in locals():
    import imp
    imp.reload(_AddonPreferences)
else:
    from . import _AddonPreferences

import copy
import bpy
from bpy.types import Panel, Menu, Operator
from rna_prop_ui import PropertyPanel
from bpy.app.translations import (
    pgettext_iface as iface_,
    pgettext_tip as tip_,
    contexts as i18n_contexts,
)
PREID = "MYPIEMENUEVER"
# --------------------------------------------------------------------------------
# ルートメニュー
# --------------------------------------------------------------------------------
class MT_Root(Menu):
    bl_idname = PREID + "_MT_Root"
    bl_label = ""
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        PieMenu_ObjectMode(pie, context)
        PieMenu_Utility(pie, context)

        # Pose
        pie = layout.menu_pie()
        pie.menu(MT_Pose.bl_idname, text="Pose")
        
        # Apply
        pie = layout.menu_pie()
        pie.menu(MT_Apply.bl_idname, text="Apply")

        # TexturePaint
        PieMenu_TexturePaint(pie, context)
        
class OT_ChangePivot(bpy.types.Operator):
    bl_idname = "op.pivot"
    bl_label = "Change Pivot"
    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_pivot_pie")
        return {'FINISHED'}
    
class OT_ChangeOrientations(bpy.types.Operator):
    bl_idname = "op.orientations"
    bl_label = "Change Orientations"
    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_orientations_pie")
        return {'FINISHED'}
class OT_InvertValue(bpy.types.Operator):
    bl_idname = "op.invert_value"
    bl_label = ""
    propName: bpy.props.StringProperty()
    def execute(self, context):
        target = getattr(context, self.propName, None)
        setattr(target, self.propName, not getattr(target, self.propName))
        return {'FINISHED'}
    @staticmethod
    def operator(layout, label, propName, targetObj):
        layout.context_pointer_set(name=propName, data=targetObj)
        layout.operator(OT_InvertValue.bl_idname, text=label, depress=layout.active and getattr(targetObj, propName, False)).propName = propName
# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------
def PieMenu_ObjectMode(pie, context):
    active = context.active_object
    object_mode = 'OBJECT' if active is None else active.mode
    active_type_is_mesh = active != None and active.type == 'MESH'
    active_type_is_armature = active != None and active.type == 'ARMATURE'
    act_mode_i18n_context = bpy.types.Object.bl_rna.properties["mode"].translation_context
    box = pie.split().box()
    box.label(text='Mode');
    col = box.column()
    row = col.row(align=False)

    r = row.row()
    # print(object_mode)
    # print(bpy.types.Object.bl_rna.properties["mode"].enum_items[object_mode].name)
    r.active = object_mode != 'OBJECT'
    r.operator("object.mode_set", text=iface_('Object', act_mode_i18n_context), icon="OBJECT_DATA", depress=object_mode == 'OBJECT').mode = 'OBJECT'

    r = row.row()
    r.active = object_mode != 'EDIT'
    r.operator("object.mode_set", text=iface_('Edit', act_mode_i18n_context), icon="EDITMODE_HLT", depress=object_mode == 'EDIT').mode = 'EDIT'

    r = row.row()
    r.active = object_mode != 'SCULPT' and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_('Sculpt', act_mode_i18n_context), icon="SCULPTMODE_HLT", depress=object_mode == 'SCULPT')
    if active_type_is_mesh: op.mode = 'SCULPT'

    r = row.row()
    r.active = object_mode != 'POSE' and active_type_is_armature
    op = r.operator("object.mode_set", text=iface_("Pose", act_mode_i18n_context), icon='POSE_HLT', depress=object_mode == 'POSE')
    if active_type_is_armature: op.mode = 'POSE'

    row = col.row(align=False)
    r = row.row()
    r.active = object_mode != 'WEIGHT_PAINT' and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_('Weight Paint', act_mode_i18n_context), icon="WPAINT_HLT", depress=object_mode == 'WEIGHT_PAINT')
    if active_type_is_mesh: op.mode = 'WEIGHT_PAINT'

    r = row.row()
    r.active = object_mode != 'TEXTURE_PAINT' and active_type_is_mesh
    op = r.operator("object.mode_set", text=iface_("Texture Paint", act_mode_i18n_context), icon="TPAINT_HLT", depress=object_mode == 'TEXTURE_PAINT')
    if active_type_is_mesh: op.mode = 'TEXTURE_PAINT'

# --------------------------------------------------------------------------------
# ユーティリティメニュー
# --------------------------------------------------------------------------------
def PieMenu_Utility(pie, context):
    def _DrawPivot(layout):
        text = bpy.context.scene.tool_settings.transform_pivot_point
        if text == 'ACTIVE_ELEMENT':
            text = "Active"
            icon = "PIVOT_ACTIVE"
        elif text == 'BOUNDING_BOX_CENTER':
            text = "BoundingBox"
            icon = "PIVOT_BOUNDBOX"
        elif text == 'CURSOR':
            text = "Cursor"
            icon = "PIVOT_CURSOR"
        elif text == 'INDIVIDUAL_ORIGINS':
            text = "Origin"
            icon = "PIVOT_INDIVIDUAL"
        elif text == 'MEDIAN_POINT':
            text = "Median"
            icon = "PIVOT_MEDIAN"
        layout.operator(OT_ChangePivot.bl_idname, text=text, icon=icon)
    def _DrawOrientation(layout):
        text = bpy.context.scene.transform_orientation_slots[0].type
        icon = "ORIENTATION_" + text
        layout.operator(OT_ChangeOrientations.bl_idname, text=text, icon=icon)
    box = pie.split().box()
    box.label(text = 'Utilities')
    col = box.column()
    col.operator(OT_Utility_ChangeLanguage.bl_idname, text="Change Language")
    row = col.row(align=False)
    _DrawPivot(row)
    _DrawOrientation(row)
    row = col.row(align=False)
    r = row.row()
    r.active = getattr(context.space_data, "overlay", None) != None
    OT_InvertValue.operator(r, "overlay", "show_overlays", context.space_data.overlay)
    OT_InvertValue.operator(r, "bone", "show_bones", context.space_data.overlay)
    r = row.row()
    r.active =  0 < len(context.selected_objects)
    OT_InvertValue.operator(r, "wireframe", "show_wire", context.object)
    OT_InvertValue.operator(r, "front", "show_in_front", context.object)
class OT_Utility_ChangeLanguage(bpy.types.Operator):
    bl_idname = "op.changelanguage"
    bl_label = ""
    def execute(self, context):
        if bpy.context.preferences.view.language == "ja_JP":
            bpy.context.preferences.view.language = "en_US"
        elif bpy.context.preferences.view.language == "en_US":
            bpy.context.preferences.view.language = "ja_JP"
        return {'FINISHED'}
# --------------------------------------------------------------------------------
# ポーズメニュー
# --------------------------------------------------------------------------------
class MT_Pose(Menu):
    bl_idname = PREID + "_MT_Pose"
    bl_label = "Pie POSE Menu"
    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'ARMATURE'
    def draw(self, context):
        layout = self.layout
        arm = bpy.context.object.data;
        #pie = layout.menu_pie()
        box = layout.column()
        box.operator(OT_Pose_ClearTransform.bl_idname)

        box.separator()
        box.label(text="Layers:")
        row = box.row(align=True)
        for i in range(32):
            if i == 8 or i == 24:
                row.separator()
            elif i == 16:
                row = box.row(align=True)
            r = row.row(align=True)
            op = r.operator(OT_Pose_ToggleBoneLayer.bl_idname, text="", icon="RADIOBUT_ON" if arm.layers[i] else "RADIOBUT_OFF")
            op.idx = i    

class OT_Pose_ToggleBoneLayer(bpy.types.Operator):
    bl_idname = "op.toggle_bone_layer"
    bl_label = ""
    idx:bpy.props.IntProperty()
    def execute(self, context):
        bpy.context.object.data.layers[self.idx] = True
        for i in range(32):
            bpy.context.object.data.layers[i] = i == self.idx
        return {'FINISHED'}

class OT_Pose_ClearTransform(bpy.types.Operator):
    bl_idname = "op.clear_transform"
    bl_label = "Clear Transform"
    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'ARMATURE'
    def execute(self, context):
        current_mode = context.active_object.mode
        bpy.ops.object.mode_set(mode='POSE')
        # backup
        buf = []
        for i in range(32):
            buf.append(bpy.context.object.data.layers[i])
            bpy.context.object.data.layers[i] = True
        # execution
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.scale_clear()
        # restore
        for i in range(32):
            bpy.context.object.data.layers[i] = buf[i]
        bpy.ops.object.mode_set( mode = current_mode)
        return {'FINISHED'}

# --------------------------------------------------------------------------------
# オブジェクト適用メニュー
# --------------------------------------------------------------------------------
class MT_Apply(Menu):
    bl_idname = PREID + "_MT_Apply"
    bl_label = "Apply Menu"
    @classmethod
    def poll(cls, context):
        return 0 < len(context.selected_objects)
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=False)
        col.operator_menu_enum(OT_Apply_ChangeDisplayType.bl_idname, "types", text="Change DisplayType")
        
class OT_Apply_ChangeDisplayType(bpy.types.Operator):
    bl_idname = "op.apply_change_display_type"
    bl_label = "Change Display Type"
    def items(self, context):
        return [("WIRE","WIRE",""),("TEXTURED","TEXTURED","")]
    types: bpy.props.EnumProperty(items = items, name = "description", description = "description")
#    @classmethod
#    def poll(cls, context):
#        return context.active_object.type == 'ARMATURE'
    def execute(self, context):
        for x in bpy.context.selected_objects:
            x.display_type = self.types
        return {'FINISHED'}
# --------------------------------------------------------------------------------
# テクスチャペイントメニュー
# --------------------------------------------------------------------------------
# class MT_TexturePaint(Menu):
#     bl_idname = PREID + "_MT_TexturePaint"
#     bl_label = "TexturePaint Menu"
#     @classmethod
#     def poll(cls, context):
#         return context.mode == "PAINT_TEXTURE"
#     def draw(self, context):
#         layout = self.layout
#         row =layout.row(align=False)
#         row.operator("image.save_all_modified", text="Save All Images")
def PieMenu_TexturePaint(pie, context):
    if context.mode != "PAINT_TEXTURE":
        return
    box = pie.split().box()
    box.label(text = 'Texture Paint')
    col = box.column()
    row = col.row()
    OT_InvertValue.operator(row, "SYM_X", "use_mesh_mirror_x", bpy.context.object)

    # row.operator(OT_TexturePaint_SymmetryX.bl_idname, text="SYM_X", depress = OT_TexturePaint_SymmetryX.isState())
    row.operator("image.save_all_modified", text="Save All Images") 

    row = col.row()
    box = row.box()
    rowinbox = box.row()
    col2 = rowinbox.column()
    col2.label(text = "Brushes")
    cnt = 0
    for i in bpy.data.brushes:
        if i.use_paint_image:
            is_use = bpy.context.tool_settings.image_paint.brush.name == i.name
            col2.operator(OT_TexturePaint_ChangeBrush.bl_idname, text=i.name, depress = is_use).brushName = i.name
            cnt += 1;
            if cnt == 10:
                 col2 = rowinbox.column()
            # print(dir(i))
    col2 = row.box().column()
    col2.label(text = "Stroke")
    for i in enum_values(bpy.context.tool_settings.image_paint.brush, 'stroke_method'):
        is_use = OT_TexturePaint_StrokeMethod.getCurrent() == i
        col2.operator(OT_TexturePaint_StrokeMethod.bl_idname, text=i, depress = is_use).methodName = i
class OT_TexturePaint_ChangeBrush(bpy.types.Operator):
    bl_idname = "op.texturepaint_changebrush"
    bl_label = "Change Brush"
    brushName: bpy.props.StringProperty()
    def execute(self, context):
        bpy.context.tool_settings.image_paint.brush = bpy.data.brushes[self.brushName]
        return {'FINISHED'}
class OT_TexturePaint_SymmetryX(bpy.types.Operator):
    bl_idname = "op.texturepaint_symmetryx"
    bl_label = "Toggle SymmetryX"
    FIELD = "use_mesh_mirror_x"
    @classmethod
    def isState(self):
        return getattr(bpy.context.object, self.FIELD)
    def execute(self, context):
        setattr(bpy.context.object, self.FIELD, not self.isState())
        return {'FINISHED'}
class OT_TexturePaint_StrokeMethod(bpy.types.Operator):
    bl_idname = "op.texturepaint_strokemethod"
    bl_label = "Change Display Type"
    methodName: bpy.props.StringProperty()
    @classmethod
    def getCurrent(self):
        return bpy.context.tool_settings.image_paint.brush.stroke_method
    def execute(self, context):
        bpy.context.tool_settings.image_paint.brush.stroke_method = self.methodName
        return {'FINISHED'}
# class OT_TexturePaint_StrokeMethodList(bpy.types.Operator):
#     bl_idname = "op.texturepaint_strokemethodlist"
#     bl_label = "Change Display Type"
#     def items(self, context):
#         values = enum_values(bpy.context.tool_settings.image_paint.brush, 'stroke_method')
#         return [(value, value, "") for value in values]
#     item: bpy.props.EnumProperty(items = items, name = "description")
#     def execute(self, context):
#         show_enum_values(bpy.context.tool_settings.image_paint.brush, 'stroke_method')
#         bpy.context.tool_settings.image_paint.stroke_method = self.item
#         return {'FINISHED'}

# --------------------------------------------------------------------------------
def show_enum_values(obj, prop_name):
    print([item.identifier for item in obj.bl_rna.properties[prop_name].enum_items])
def enum_values(obj, prop_name):
    return [item.identifier for item in obj.bl_rna.properties[prop_name].enum_items]
# --------------------------------------------------------------------------------

classes = (
    MT_Root,
    MT_Pose,
    MT_Apply,
    # MT_TexturePaint,
    OT_ChangePivot,
    OT_ChangeOrientations,
    OT_InvertValue,
    OT_Utility_ChangeLanguage,
    OT_Pose_ClearTransform,
    OT_Pose_ToggleBoneLayer,
    OT_Apply_ChangeDisplayType,
    OT_TexturePaint_ChangeBrush,
    OT_TexturePaint_SymmetryX,
    OT_TexturePaint_StrokeMethod,
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
