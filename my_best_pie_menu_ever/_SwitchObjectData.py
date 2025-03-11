if "bpy" in locals():
    import importlib
    importlib.reload(_Util)
    importlib.reload(_UtilInput)
    importlib.reload(_UtilBlf)
    importlib.reload(_AddonPreferences)
    importlib.reload(g)
else:
    from . import _Util
    from . import _UtilInput
    from . import _UtilBlf
    from . import _AddonPreferences
    from . import g
import bpy


def draw_pie_menu(layout, context):
    layout.operator(MPM_OT_SwitchObjectDataModal.bl_idname)


class MPM_OT_SwitchObjectDataModal(bpy.types.Operator):
    bl_idname = "mpm.switch_object_data_modal"
    bl_label = "Switch Object Data"
    bl_description = ""

    current_item_idx = -1
    current_menu_idx = 0
    ROW_LIMIT = 30
    SHOW_STR_CNT = 20
    WIDTH_PER_CHAR = 9
    HOVER_SCALE = 1.2

    @classmethod
    def poll(self, context):
        return context.object != None and context.object.type == "MESH"

    def invoke(self, context, event):
        self.imx = event.mouse_x
        self.imy = event.mouse_y
        self.mx = event.mouse_x
        self.my = event.mouse_y
        self.prev_active_idx_vg = context.object.vertex_groups.active_index
        self.prev_active_idx_uv = context.object.data.uv_layers.active_index
        self.prev_active_idx_ca = context.object.data.color_attributes.active_color_index
        self.prev_active_idx_sk = context.object.active_shape_key_index
        self.prev_sk_values = [key.value for key in context.object.data.shape_keys.key_blocks] if context.object.data.shape_keys else []
        self.update_mode(self.current_menu_idx)
        self.timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        self.label_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_label, (), "WINDOW", "POST_PIXEL")
        _UtilInput.init()
        g.force_cancel_piemenu_modal(context)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mx = event.mouse_x
        self.my = event.mouse_y
        if event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.on_mousewheel and self.on_mousewheel(context, event.type == "WHEELUPMOUSE")
        elif _UtilInput.is_pressed_keys(event, "MIDDLEMOUSE"):
            self.on_middle_click and self.on_middle_click(context)
        elif _UtilInput.is_pressed_keys(event, "LEFTMOUSE", "SPACE"):
            return self.finished(context)
        elif _UtilInput.is_pressed_keys(event, "RIGHTMOUSE", "ESC"):
            return self.cancelled(context)
        elif _UtilInput.is_pressed_keys(event, "W"):
            ret = self.finished(context)
            bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_my_pie_menu")
            return ret
        return {"RUNNING_MODAL"}

    def finished(self, context):
        self.release(context)
        return {"FINISHED"}

    def cancelled(self, context):
        self.release(context)
        if -1 < self.prev_active_idx_vg:
            context.object.vertex_groups.active_index = self.prev_active_idx_vg
        for i, v in enumerate(self.prev_sk_values):
            if (i < len(context.object.data.shape_keys.key_blocks) < i):
                context.object.data.shape_keys.key_blocks[i].value = v
        if -1 < self.prev_active_idx_uv:
            context.object.data.uv_layers.active_index = self.prev_active_idx_uv
            context.object.data.uv_layers.active.active_render = True
        if -1 < self.prev_active_idx_ca:
            context.object.data.color_attributes.active_color_index = self.prev_active_idx_ca
            context.object.data.color_attributes.render_color_index = self.prev_active_idx_ca
        return {"CANCELLED"}

    def release(self, context):
        if self.label_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self.label_handler, "WINDOW")
            context.area.tag_redraw()
            self.label_handler = None
        if self.timer:
            context.window_manager.event_timer_remove(self.timer)
            self.timer = None

    def draw_label(self):
        self.draw_menu()
        self.draw_func()

    def draw_menu(self):
        menues = ["VertexGroup", "ShapeKeys", "UV Map", "ColorAttributes"]
        x = self.imx - bpy.context.area.x
        y = self.imy - bpy.context.area.y + 50
        WIDTH = 90
        HEIGHT = 20
        WIDTH_SLASH = 20
        for i, menu in enumerate(menues):
            if 0 < i:
                _UtilBlf.draw_label_fix(0, "/", x, y)
                x += WIDTH_SLASH
            if _UtilBlf.draw_label_mouseover(0, menu, x, y, self.mx, self.my, WIDTH, HEIGHT, self.current_menu_idx == i, align="center"):
                if self.current_menu_idx != i:
                    self.update_mode(i)
            x += WIDTH
        x = self.imx - bpy.context.area.x + 10 + self.current_menu_idx * (WIDTH + WIDTH_SLASH)
        y -= 30
        _UtilBlf.draw_field(0, "Activate", "| mouseover", x, y)
        x += 90
        if self.current_menu_idx == 1:
            _UtilBlf.draw_field(0, "Adjust", "| middle-click,", x, y)
            _UtilBlf.draw_field(0, "", "  mousewheel", x, y-10)
            x += 90
        _UtilBlf.draw_field(0, "Apply", "| left-click", x, y)
        x += 80
        _UtilBlf.draw_field(0, "Cancel", "| right-click, ESC", x, y)
        x = self.imx - bpy.context.area.x
        y -= 40
        _UtilBlf.draw_separator(0, "_____________________________", x, y)

    def update_mode(self, i):
        self.current_menu_idx = i
        self.on_middle_click = None
        self.on_mousewheel = None
        if i == 0:
            self.draw_func = self.draw_vgroups
        elif i == 1:
            self.draw_func = self.draw_shapekeys
            self.on_mousewheel = self.on_mousewheel_shapekey
            self.on_middle_click = self.on_middleclick_shapekey
        elif i == 2:
            self.draw_func = self.draw_uv
        elif i == 3:
            self.draw_func = self.draw_attributes

    def get_items_start_position(self):
        return self.imx - bpy.context.area.x, self.imy - bpy.context.area.y - 50

    def draw_vgroups(self):
        obj = bpy.context.object
        x, y = self.get_items_start_position()
        if obj.vertex_groups.active == None:
            _UtilBlf.draw_label_fix(0, "No VertexGroups found.", x, y)
            return
        ITEM_WIDTH = self.SHOW_STR_CNT * self.WIDTH_PER_CHAR
        ITEM_HEIGHT = 20
        active_idx = obj.vertex_groups.active_index
        tmp_current_idx = self.current_item_idx
        self.current_item_idx = -1

        def __draw(i,  is_fullname):
            vg = obj.vertex_groups[i]
            column = int(i / self.ROW_LIMIT)
            row = i % self.ROW_LIMIT
            label = vg.name if is_fullname else vg.name[:self.SHOW_STR_CNT] + (".." if self.SHOW_STR_CNT < len(vg.name) else "")
            if _UtilBlf.draw_label_mouseover(0, label, x + column * ITEM_WIDTH, y + (-ITEM_HEIGHT * row),
                                             self.mx, self.my, ITEM_WIDTH, ITEM_HEIGHT, active_idx == i, self.HOVER_SCALE):
                self.current_item_idx = i
                if active_idx != i:
                    obj.vertex_groups.active_index = i

        for i, vg in enumerate(obj.vertex_groups):
            # 最後に描画する
            if tmp_current_idx != -1 and tmp_current_idx == i:
                continue
            __draw(i, False)
        else:
            if tmp_current_idx != -1:
                __draw(tmp_current_idx, True)

    def draw_shapekeys(self):
        obj = bpy.context.object
        x, y = self.get_items_start_position()
        if obj.data.shape_keys == None:
            _UtilBlf.draw_label_fix(0, "No ShapeKeys found.", x, y)
            return
        ITEM_WIDTH = self.SHOW_STR_CNT * self.WIDTH_PER_CHAR + 40
        ITEM_HEIGHT = 20
        active_idx = obj.active_shape_key_index
        tmp_current_idx = self.current_item_idx
        self.current_item_idx = -1

        def __draw(i, is_fullname):
            sk = obj.data.shape_keys.key_blocks[i]
            column = int(i / self.ROW_LIMIT)
            row = i % self.ROW_LIMIT
            label = sk.name if is_fullname else sk.name[:self.SHOW_STR_CNT] + (".." if self.SHOW_STR_CNT < len(sk.name) else "")
            if 0 < i:
                label += f"[{sk.value:.1f}]"
            if _UtilBlf.draw_label_mouseover(0, label, x + column * ITEM_WIDTH, y + (-ITEM_HEIGHT * row),
                                             self.mx, self.my, ITEM_WIDTH, ITEM_HEIGHT, active_idx == i, self.HOVER_SCALE):
                self.current_item_idx = i
                if active_idx != i:
                    obj.active_shape_key_index = i

        for i, sk in enumerate(obj.data.shape_keys.key_blocks):
            # 最後に描画する
            if tmp_current_idx != -1 and tmp_current_idx == i:
                continue
            __draw(i, False)
        else:
            if tmp_current_idx != -1:
                __draw(tmp_current_idx, True)

    def on_mousewheel_shapekey(self, context, up):
        if self.current_item_idx <= 0:  # 先頭のBasisも操作しない
            return
        sk = context.object.data.shape_keys.key_blocks[self.current_item_idx]
        sk.value += 0.1 if up else -0.1
        sk.value = _Util.clamp(round(sk.value, 1), 0.0, 1.0)

    def on_middleclick_shapekey(self, context):
        if self.current_item_idx <= 0:  # 先頭のBasisも操作しない
            return
        sk = context.object.data.shape_keys.key_blocks[self.current_item_idx]
        sk.value = 0 if 0 < sk.value else 1

    def draw_uv(self):
        obj = bpy.context.object
        x, y = self.get_items_start_position()
        if obj.data.uv_layers.active == None:
            _UtilBlf.draw_label_fix(0, "No UV Maps found.", x, y)
            return
        ITEM_WIDTH = self.SHOW_STR_CNT * self.WIDTH_PER_CHAR
        ITEM_HEIGHT = 20
        active_idx = obj.data.uv_layers.active_index
        self.current_item_idx = -1
        for i, uv in enumerate(obj.data.uv_layers):
            column = int(i / self.ROW_LIMIT)
            row = i % self.ROW_LIMIT
            label = uv.name[:self.SHOW_STR_CNT] + (".." if self.SHOW_STR_CNT < len(uv.name) else "")
            if _UtilBlf.draw_label_mouseover(0, label, x + column * ITEM_WIDTH, y + (-ITEM_HEIGHT * row),
                                             self.mx, self.my, ITEM_WIDTH, ITEM_HEIGHT, active_idx == i, self.HOVER_SCALE):
                self.current_item_idx = i
                if active_idx != i:
                    obj.data.uv_layers.active_index = i
                    obj.data.uv_layers.active.active_render = True

    def draw_attributes(self):
        obj = bpy.context.object
        x, y = self.get_items_start_position()
        if obj.data.color_attributes and len(obj.data.color_attributes) == 0:
            _UtilBlf.draw_label_fix(0, "No ColorAttributes found.", x, y)
            return
        ITEM_WIDTH = self.SHOW_STR_CNT * self.WIDTH_PER_CHAR
        ITEM_HEIGHT = 20
        active_idx = obj.data.color_attributes.active_color_index
        tmp_current_idx = self.current_item_idx
        self.current_item_idx = -1

        def __draw(i,  is_fullname):
            ca = obj.data.color_attributes[i]
            column = int(i / self.ROW_LIMIT)
            row = i % self.ROW_LIMIT
            label = ca.name if is_fullname else ca.name[:self.SHOW_STR_CNT] + (".." if self.SHOW_STR_CNT < len(ca.name) else "")
            if _UtilBlf.draw_label_mouseover(0, label, x + column * ITEM_WIDTH, y + (-ITEM_HEIGHT * row),
                                             self.mx, self.my, ITEM_WIDTH, ITEM_HEIGHT, active_idx == i):
                self.current_item_idx = i
                if active_idx != i:
                    obj.data.color_attributes.active_color_index = i
                    obj.data.color_attributes.render_color_index = i

        for i, ca in enumerate(obj.data.color_attributes):
            # 最後に描画する
            if tmp_current_idx != -1 and tmp_current_idx == i:
                continue
            __draw(i, False)
        else:
            if tmp_current_idx != -1:
                __draw(tmp_current_idx, True)
# --------------------------------------------------------------------------------


classes = [
    MPM_OT_SwitchObjectDataModal,
]


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
