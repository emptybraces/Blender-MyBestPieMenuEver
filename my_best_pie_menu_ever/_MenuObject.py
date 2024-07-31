import bpy
from . import _Util
from . import _MenuWeightPaint
from ._MenuPose import MPM_OT_ARP_SnapIKFK

# --------------------------------------------------------------------------------
# オブジェクトモードメニュー
# --------------------------------------------------------------------------------


def MenuPrimary(pie, context):
    pie = pie.split()
    box = pie.box()
    box.label(text="Object Primary")
    r = box.row()
    c = r.column(align=True)

    _MenuWeightPaint.MirrorVertexGroup(c)
    _Util.layout_operator(c, MPM_OT_RemoveUnusedVertexGroup.bl_idname, icon="X")

    # if imported
    c = r.column(align=True)
    enabled_addons = context.preferences.addons.keys()
    if "wiggle_2" in enabled_addons:
        box = c.box()
        box.label(text="3rd Party Tool")
        _Util.layout_operator(box, "wiggle.reset", "Wiggle2: ResetPhysics")
    if any("auto_rig_pro" in i for i in enabled_addons):
        _Util.layout_operator(box, MPM_OT_ARP_SnapIKFK.bl_idname)

# --------------------------------------------------------------------------------


class MPM_OT_RemoveUnusedVertexGroup(bpy.types.Operator):
    bl_idname = "op.mpm_remove_unused_vgroup"
    bl_label = "Remove Unused VGroup"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        current_mode = context.active_object.mode
        if current_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        obj = bpy.context.active_object
        remove_groups = []
        for vg in obj.vertex_groups:
            has_weight = False
            for vertex in obj.data.vertices:
                for group in vertex.groups:
                    if group.group == vg.index:
                        has_weight = True
                        break
                if has_weight:
                    break
            # ウェイトが存在しない頂点グループ
            if not has_weight:
                remove_groups.append(vg)

        # 削除
        if 0 < len(remove_groups):
            _Util.show_msgbox("\n".join(["Remove: " + i.name for i in remove_groups]), "Remove Unused Vetex Group")
            for vg in remove_groups:
                _Util.show_report(self, f"Remove: {vg.name}")
                obj.vertex_groups.remove(vg)
        else:
            _Util.show_msgbox("Not found unused vertex groups.", "Remove Unused Vetex Group")

        if current_mode != "OBJECT":
            bpy.ops.object.mode_set(mode=current_mode)
        return {"FINISHED"}


# --------------------------------------------------------------------------------
classes = [
    MPM_OT_RemoveUnusedVertexGroup,
]


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
