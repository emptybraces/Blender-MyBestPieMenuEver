import bpy
from . import _Util
from . import g
import os
import shutil

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
    DrawSimilarTexutreNameList(r, context)

    # Apply
    box = box.box()
    box.label(text="Apply", icon="MODIFIER")

    c = box.column(align=True)
    _Util.layout_operator(c, MPM_OT_SeparateTextureChannelPanel.bl_idname)
    _Util.layout_operator(c, MPM_OT_LostRefImagePanel.bl_idname)


def DrawTexutreInfo(layout, context):
    image = context.area.spaces.active.image
    box = layout.box()
    box.label(text="Image Info")
    c = box.column(align=True)
    if image:
        info = "PACKED" if image.packed_file else "UNPACKED"
        info += f", {image.size[0]} x {image.size[1]}"
        c.label(text=info)
        r = c.row(align=True)

        if image.packed_file == None:
            r.operator("image.pack", text="", icon="UGLYPACKAGE")
        else:
            r.operator("image.unpack", text="", icon="PACKAGE")

        rr = r.row(align=True)
        rr.enabled = image.packed_file == None
        rr.scale_x = 2.0
        rr.prop(image, "filepath", text="")

        rr = r.row(align=True)
        rr.operator(MPM_OT_ReloadImage.bl_idname, text="", icon="FILE_REFRESH")
        rr.operator(MPM_OT_DeleteImage.bl_idname, text="", icon="TRASH")

        r = c.row(align=True)
        r.prop(image, "source", text="Source")
        r.prop(image.colorspace_settings, "name", text="")
    else:
        layout.label(text="No active image")


def DrawSimilarTexutreNameList(layout, context):
    current_image = context.area.spaces.active.image
    if not current_image:
        return

    box = layout.box()
    box.label(text="Similar named images")
    c = box.column(align=True)
    name = current_image.name

    def _op(find_name, cnt):
        # 検索関数
        for img in (img for img in bpy.data.images if find_name in img.name):
            if img == current_image:
                continue
            cnt = cnt + 1
            _Util.MPM_OT_SetPointer.operator(c, img.name, context.area.spaces.active, "image", img)
            if 6 <= cnt:
                break
        return cnt
    # 後ろから検索
    cnt = _op(name[:-5] if 5 < len(name) else name, 0)
    # 前から検索
    if cnt < 6 and 5 < len(name):
        cnt = _op(name[:5], cnt)
    if cnt == 0:
        c.label(text="Not found.")


class MPM_OT_DeleteImage(bpy.types.Operator):
    bl_idname = "mpm.image_delete"
    bl_label = "Delete Image"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        return context.area.spaces.active.image is not None

    def invoke(self, context, event):
        g.force_cancel_piemenu_modal(context)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.label(text="Do you want to delete this image? (Undoable)")

    def execute(self, context):
        bpy.data.images.remove(context.area.spaces.active.image)
        context.area.spaces.active.image = None
        return {"FINISHED"}


class MPM_OT_ReloadImage(bpy.types.Operator):
    bl_idname = "mpm.image_reload"
    bl_label = "Reload Image"

    @classmethod
    def poll(self, context):
        return context.area.spaces.active.image is not None

    def execute(self, context):
        context.area.spaces.active.image.reload()
        return {"FINISHED"}


class MPM_OT_LostRefImagePanel(bpy.types.Operator):
    bl_idname = "mpm.image_lost_ref_image_panel"
    bl_label = "Show Lost Reference Image"

    def invoke(self, context, event):
        g.force_cancel_piemenu_modal(context)
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        c = self.layout.column()
        is_found = False
        for image in bpy.data.images:
            if image.source !=  "GENERATED" and not image.packed_file:
                file_path = bpy.path.abspath(image.filepath)
                if any(file_path) and not os.path.exists(file_path):
                    is_found = True
                    _Util.MPM_OT_SetPointer.operator(c, image.name, context.area.spaces.active, "image", image)
        if not is_found:
            self.layout.label(text="No lost images were found.")
        # self.layout.label(text="Select the channel to output.")

    def execute(self, context):
        return {"FINISHED"}


class MPM_OT_SeparateTextureChannelPanel(bpy.types.Operator):
    bl_idname = "mpm.image_separate_texture_channel_panel"
    bl_label = "Separate Texture Channel"
    channels: bpy.props.BoolVectorProperty(size=4)
    output_type: bpy.props.EnumProperty(items=[("exr", "exr", ""), ("png", "png", "")])
    export_type: bpy.props.EnumProperty(items=[("PACK", "PACK", ""), ("EXPORT", "EXPORT", "")])
    relative_path: bpy.props.StringProperty(default="tex")

    @classmethod
    def poll(self, context):
        return context.area.spaces.active.image is not None

    def invoke(self, context, event):
        g.force_cancel_piemenu_modal(context)
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.label(text="Select the channel to output.")
        c = self.layout.column()
        r = c.row(align=True)
        _Util.layout_prop(r, self, "channels", text="R", toggle=1, index=0)
        _Util.layout_prop(r, self, "channels", text="G", toggle=1, index=1)
        _Util.layout_prop(r, self, "channels", text="B", toggle=1, index=2)
        _Util.layout_prop(r, self, "channels", text="A", toggle=1, index=3, isActive=context.area.spaces.active.image.channels == 4)

        r = c.row(align=True)
        r.prop(self, "export_type", expand=True)

        # r = c.row(align=True)
        _Util.layout_prop(c, self, "output_type", expand=True, isActive=self.export_type == "EXPORT")

        _Util.layout_prop(c, self, "relative_path", text="Folder", isActive=self.export_type == "EXPORT")

    def execute(self, context):
        filepath = bpy.data.filepath
        if not filepath:
            _Util.show_report_error(self, "filepath not found.")
            return {"CANCELLED"}
        if not any(self.channels):
            _Util.show_report_error(self, "Please select at least one channnel.")
            return {"CANCELLED"}
        self.export_rgb_channels(context,
                                 context.area.spaces.active.image.name,
                                 os.path.join(os.path.dirname(filepath), self.relative_path) if self.export_type == "EXPORT" else None,
                                 self.channels,
                                 self.output_type)
        return {"FINISHED"}

    def export_rgb_channels(self, context, image_name, export_path, channels, file_ext):
        image = bpy.data.images.get(image_name)
        if image is None:
            _Util.show_report_error(f"Can't found '{image_name}'.")
            return
        image.reload()
        pixels = list(image.pixels)
        width, height = image.size
        r_channel = [0] * (width * height * 4)
        g_channel = [0] * (width * height * 4)
        b_channel = [0] * (width * height * 4)
        a_channel = [0] * (width * height * 4)

        # ピクセルデータをチャンネルごとに分解
        for i in range(0, len(pixels), 4):
            r = pixels[i]
            r_channel[i] = r_channel[i+1] = r_channel[i+2] = r  # R値をグレースケール化
            r_channel[i+3] = 1  # アルファ値

            g = pixels[i+1]
            g_channel[i] = g_channel[i+1] = g_channel[i+2] = g  # G値をグレースケール化
            g_channel[i+3] = 1

            b = pixels[i+2]
            b_channel[i] = b_channel[i+1] = b_channel[i+2] = b  # B値をグレースケール化
            b_channel[i+3] = 1

            a = pixels[i+3]
            a_channel[i] = a_channel[i+1] = a_channel[i+2] = a  # A値をグレースケール化
            b_channel[i+3] = 1

        # チャンネルごとの画像を作成
        def get_or_new_image(name, pixels):
            image = bpy.data.images.get(name)
            if image == None or len(image.pixels) != len(pixels):
                image = bpy.data.images.new(name=name, width=width, height=height)
            image.pixels = pixels
            return image

        r_image = get_or_new_image(image_name + "_R", r_channel) if channels[0] else None
        g_image = get_or_new_image(image_name + "_G", g_channel) if channels[1] else None
        b_image = get_or_new_image(image_name + "_B", b_channel) if channels[2] else None
        a_image = get_or_new_image(image_name + "_A", a_channel) if channels[3] and image.channels == 4 else None

        tmp_scene = bpy.data.scenes.new("tmp_scene")
        render_settings = tmp_scene.render.image_settings
        if file_ext == "exr":
            render_settings.file_format = "OPEN_EXR"
            render_settings.exr_codec = 'ZIP'  # 'ZIP', 'PIZ', 'RLE', 'ZIPS'
            render_settings.color_depth = '16'
        else:
            render_settings.file_format = "PNG"

        if export_path and not os.path.exists(export_path):
            os.makedirs(export_path)

        def save(image, path):
            if not image:
                return
            if path:
                if image.packed_file:
                    image.unpack(method="REMOVE")
                path = os.path.join(path, image.name + "." + file_ext)
                image.save_render(path, scene=tmp_scene)
                image.source = "FILE"
                image.filepath_raw = path
                image.colorspace_settings.name = "Non-Color"
                image.alpha_mode = "NONE"
                # image.update()
                _Util.show_report(self, f"{image.name} saved in the following path:\n{path}")
            else:
                if not image.packed_file:
                    image.pack()
                image.colorspace_settings.name = "Non-Color"
                image.alpha_mode = "NONE"
                _Util.show_report(self, f"{image.name} saved.")
            context.area.spaces.active.image = image

        save(r_image, export_path)
        save(g_image, export_path)
        save(b_image, export_path)
        save(a_image, export_path)

        bpy.data.scenes.remove(tmp_scene)

        # 画像を削除
    #    bpy.data.images.remove(r_image)
    #    bpy.data.images.remove(g_image)
    #    bpy.data.images.remove(b_image)
    #


# --------------------------------------------------------------------------------
classes = [
    MPM_OT_DeleteImage,
    MPM_OT_ReloadImage,
    MPM_OT_SeparateTextureChannelPanel,
    MPM_OT_LostRefImagePanel,
]


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
