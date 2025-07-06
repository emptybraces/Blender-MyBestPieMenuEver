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

    @classmethod
    def poll(self, context):
        return context.object != None and context.object.type == "MESH"

    def invoke(self, context, event):
        cls = MPM_OT_SwitchObjectDataModal
        self.menu_classes = [
            cls.DrawerVGroup(context, event),
            cls.DrawerShapeKeys(context, event),
            cls.DrawerUVMap(context, event),
            cls.DrawerColorAttribute(context, event),
        ]
        if _Util.get_armature(context.object):
            self.menu_classes.append(cls.DrawerBoneCollection(context, event))
        self.input = _UtilInput.Monitor()
        self.current_menu = self.menu_classes[0]
        self.imx = self.mx = event.mouse_x
        self.imy = self.my = event.mouse_y
        self.is_move_mode = False
        self.last_mode = context.object.mode
        bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
        self.timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        self.label_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw2d, (), "WINDOW", "POST_PIXEL")
        g.force_cancel_piemenu_modal(context)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mx = event.mouse_x
        self.my = event.mouse_y
        self.input.update(event, "MIDDLEMOUSE", "LEFTMOUSE", "SPACE", "RIGHTMOUSE", "ESC", "W", "G")
        ret = self.current_menu.modal(context, event, self.input)
        if ret:
            return ret
        # 通常のカメラ移動はスルー
        if event.type == "MIDDLEMOUSE" or event.type == "WHEELUPMOUSE" or event.type == "WHEELDOWNMOUSE":
            return {"PASS_THROUGH"}
        if self.input.is_keydown("LEFTMOUSE", "SPACE"):
            return self.finished(context)
        elif self.input.is_keydown("RIGHTMOUSE", "ESC"):
            return self.cancelled(context)
        elif self.input.is_keydown("W"):
            ret = self.finished(context)
            bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_my_pie_menu")
            return ret
        elif self.input.is_keydown("G"):
            self.is_move_mode = True
        elif self.input.is_keyup(event, "G"):
            self.is_move_mode = False
        if self.is_move_mode:
            self.imx = event.mouse_x
            self.imy = event.mouse_y
            for menu in self.menu_classes:
                menu.imx = event.mouse_x
                menu.imy = event.mouse_y
        return {"RUNNING_MODAL"}

    def finished(self, context):
        for i in self.menu_classes:
            i.on_close(context, False)
        self.release(context)
        return {"FINISHED"}

    def cancelled(self, context):
        for i in self.menu_classes:
            i.on_close(context, True)
        self.release(context)
        bpy.ops.object.mode_set(mode=self.last_mode)
        return {"CANCELLED"}

    def release(self, context):
        if self.label_handler:
            bpy.types.SpaceView3D.draw_handler_remove(self.label_handler, "WINDOW")
            context.area.tag_redraw()
            self.label_handler = None
        if self.timer:
            context.window_manager.event_timer_remove(self.timer)
            self.timer = None

    def draw2d(self):
        if not self.current_menu:
            return
        self.draw_menu()
        self.current_menu.draw_list()

    def draw_menu(self):
        x = self.imx - bpy.context.area.x
        y = self.imy - bpy.context.area.y + 50
        menu_sep = " | "
        menu_sep_width = _UtilBlf.draw_label_dimensions(menu_sep)[0]
        for i, menu in enumerate(self.menu_classes):
            if 0 < i:
                _UtilBlf.draw_label(menu_sep, x, y)
                x += menu_sep_width
            w, h = _UtilBlf.draw_label_dimensions(menu.name)
            if _UtilBlf.draw_label_mousehover(menu.name, "", x, y, self.mx, self.my, w, h, self.current_menu == menu, align="left"):
                if self.current_menu != menu:
                    self.current_menu = menu
                    menu.on_mode_change(bpy.context)
            x += w
        x = self.imx - bpy.context.area.x + 10  # + self.current_menu_idx * (WIDTH + slash_width)
        y -= 30
        self.current_menu.draw_key_info(x, y)
        x = self.imx - bpy.context.area.x
        y -= 40
        _UtilBlf.draw_separator("_____________________________", x, y)

    class DrawerBase:
        ROW_LIMIT = 40
        SHOW_STR_CNT = 20

        def __init__(self, context, event):
            self.current_hover_idx = -1
            self.current_active_idx = -1
            self.imx = self.mx = event.mouse_x
            self.imy = self.my = event.mouse_y
            self.last_mode = context.object.mode
            self.reserved_mode = None

        def on_mode_change(self, context):
            self.reserved_mode = self.last_mode

        def modal(self, context, event, input):
            self.mx = event.mouse_x
            self.my = event.mouse_y
            if self.reserved_mode:
                bpy.ops.object.mode_set(mode=self.reserved_mode)
                self.reserved_mode = None
            return None

        def get_items_start_position(self):
            return self.imx - bpy.context.area.x, self.imy - bpy.context.area.y - 50

        def _find_mousehovered(self, i, label, x, y, w, h):
            column = int(i / self.ROW_LIMIT)
            row = i % self.ROW_LIMIT
            return _UtilBlf.is_mousehover_label(label, x + column * w, y + (-h * row), self.mx, self.my, w, h)

        def _draw_label(self, i, label, x, y, w, h, isHighlight):
            column = int(i / self.ROW_LIMIT)
            row = i % self.ROW_LIMIT
            _UtilBlf.draw_label(label, x + column * w, y + (-h * row),
                                color=_UtilBlf.COLOR_HIGHLIGHT_ACTIVE if isHighlight else _UtilBlf.COLOR_LABEL)

        def _draw_label_list(self, data, funcLabel):
            x, y = self.get_items_start_position()
            item_w, item_h = _UtilBlf.draw_label_dimensions("a")
            item_w *= self.SHOW_STR_CNT
            item_h *= 2
            self.current_hover_idx = -1

            for i, bc in enumerate(data):
                label = funcLabel(i, bc, False)
                if self._find_mousehovered(i, label, x, y, item_w, item_h):
                    self.current_hover_idx = i
                    if self.current_active_idx != i:
                        self.current_active_idx = i
                    break
            for i, bc in enumerate(data):
                # 名前を全表示するものは最後に描画しないと、ほかのラベルに被って見えない。
                if self.current_active_idx == i:
                    continue
                self._draw_label(i, funcLabel(i, bc, False), x, y, item_w, item_h, False)
            else:
                if self.current_active_idx != -1:
                    label = funcLabel(self.current_active_idx, data[self.current_active_idx], True)
                    self._draw_label(self.current_active_idx, label, x, y, item_w, item_h, True)

    class DrawerVGroup(DrawerBase):
        name = "VertexGroup"

        def __init__(self, context, event):
            super().__init__(context, event)
            self.prev_active_idx_vg = context.object.vertex_groups.active_index

        def modal(self, context, event, input):
            super().modal(context, event, input)
            if self.current_active_idx != -1 and context.object.vertex_groups.active_index != self.current_active_idx:
                context.object.vertex_groups.active_index = self.current_active_idx
            return None

        def on_close(self, context, is_cancel):
            if is_cancel:
                if -1 < self.prev_active_idx_vg:
                    context.object.vertex_groups.active_index = self.prev_active_idx_vg

        def on_mode_change(self, context):
            super().on_mode_change(context)
            self.current_active_idx = context.object.vertex_groups.active_index
            self.reserved_mode = "WEIGHT_PAINT"

        def draw_key_info(self, x, y):
            w = _UtilBlf.draw_label_dimensions("Activate")[0]*2
            _UtilBlf.draw_key_info("Activate", "| mousehover", x, y)
            _UtilBlf.draw_key_info("Apply", "| left-click", x := x+w, y)
            _UtilBlf.draw_key_info("Cancel", "| right-click, ESC", x := x+w, y)
            _UtilBlf.draw_key_info("MovePanel", "| G", x := x+w, y)

        def draw_list(self):
            obj = bpy.context.object
            x, y = self.get_items_start_position()
            if 0 == len(obj.vertex_groups):
                _UtilBlf.draw_label("No VertexGroups found.", x, y)
                return

            def __label(i, vg, is_fullname):
                return vg.name if is_fullname else vg.name[:self.SHOW_STR_CNT] + (".." if self.SHOW_STR_CNT < len(vg.name) else "")
            self._draw_label_list(obj.vertex_groups, __label)

    class DrawerShapeKeys(DrawerBase):
        name = "Shapekeys"

        def __init__(self, context, event):
            super().__init__(context, event)
            self.prev_active_idx_sk = context.object.active_shape_key_index
            self.prev_sk_values = [key.value for key in context.object.data.shape_keys.key_blocks] if context.object.data.shape_keys else []

        def modal(self, context, event, input):
            super().modal(context, event, input)
            if self.current_active_idx != -1 and context.object.active_shape_key_index != self.current_active_idx:
                context.object.active_shape_key_index = self.current_active_idx
            # 分かりずらいのでここでself.input.updateしない。元でまとめてやる
            if -1 != self.current_hover_idx:
                if event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
                    self.on_mousewheel(context, event.type == "WHEELUPMOUSE")
                elif input.is_keydown("MIDDLEMOUSE"):
                    self.on_middleclick(context)
                return {"RUNNING_MODAL"}
            return None

        def on_close(self, context, is_cancel):
            if is_cancel:
                for i, v in enumerate(self.prev_sk_values):
                    if (i < len(context.object.data.shape_keys.key_blocks)):
                        context.object.data.shape_keys.key_blocks[i].value = v

        def on_mode_change(self, context):
            super().on_mode_change(context)
            self.current_active_idx = context.object.active_shape_key_index
            self.reserved_mode = "EDIT"

        def on_mousewheel(self, context, up):
            if self.current_hover_idx <= 0:  # 先頭のBasisも操作しない
                return
            sk = context.object.data.shape_keys.key_blocks[self.current_hover_idx]
            sk.value += 0.1 if up else -0.1
            sk.value = _Util.clamp(round(sk.value, 1), 0.0, 1.0)

        def on_middleclick(self, context):
            if self.current_hover_idx <= 0:  # 先頭のBasisも操作しない
                return
            sk = context.object.data.shape_keys.key_blocks[self.current_hover_idx]
            sk.value = 0 if 0 < sk.value else 1

        def draw_key_info(self, x, y):
            w = _UtilBlf.draw_label_dimensions("Activate")[0]*2
            _UtilBlf.draw_key_info("Activate", "| mousehover", x, y)
            _UtilBlf.draw_key_info("Adjust", "| middle-click,\n  mousewheel",  x := x + w, y)
            _UtilBlf.draw_key_info("Apply", "| left-click",  x := x + w, y)
            _UtilBlf.draw_key_info("Cancel", "| right-click, ESC",  x := x + w, y)
            _UtilBlf.draw_key_info("MovePanel", "| G",  x := x + w, y)

        def draw_list(self):
            obj = bpy.context.object
            x, y = self.get_items_start_position()
            if obj.data.shape_keys == None:
                _UtilBlf.draw_label("No ShapeKeys found.", x, y)
                return

            def __label(i, sk, is_fullname):
                label = sk.name if is_fullname else sk.name[:self.SHOW_STR_CNT] + (".." if self.SHOW_STR_CNT < len(sk.name) else "")
                if 0 < i:
                    label += f"[{sk.value:.1f}]"
                return label
            self._draw_label_list(obj.data.shape_keys.key_blocks, __label)

    class DrawerUVMap(DrawerBase):
        name = "UV Map"

        def __init__(self, context, event):
            super().__init__(context, event)
            self.prev_active_idx_uv = context.object.data.uv_layers.active_index

        def modal(self, context, event, input):
            super().modal(context, event, input)
            if self.current_active_idx != -1 and context.object.data.uv_layers.active_index != self.current_active_idx:
                context.object.data.uv_layers.active_index = self.current_active_idx
                context.object.data.uv_layers.active.active_render = True
            return None

        def on_close(self, context, is_cancel):
            if is_cancel:
                if -1 < self.prev_active_idx_uv:
                    context.object.data.uv_layers.active_index = self.prev_active_idx_uv
                    context.object.data.uv_layers.active.active_render = True

        def on_mode_change(self, context):
            super().on_mode_change(context)
            self.current_active_idx = context.object.data.uv_layers.active_index

        def draw_key_info(self, x, y):
            w = _UtilBlf.draw_label_dimensions("Activate")[0]*2
            _UtilBlf.draw_key_info("Activate", "| mousehover", x, y)
            _UtilBlf.draw_key_info("Apply", "| left-click", x := x+w, y)
            _UtilBlf.draw_key_info("Cancel", "| right-click, ESC", x := x+w, y)
            _UtilBlf.draw_key_info("MovePanel", "| G", x := x+w, y)

        def draw_list(self):
            obj = bpy.context.object
            x, y = self.get_items_start_position()
            if obj.data.uv_layers.active == None:
                _UtilBlf.draw_label("No UV Maps found.", x, y)
                return

            def __label(i, uv, is_fullname):
                return uv.name if is_fullname else uv.name[:self.SHOW_STR_CNT] + (".." if self.SHOW_STR_CNT < len(uv.name) else "")
            self._draw_label_list(obj.data.uv_layers, __label)

    class DrawerColorAttribute(DrawerBase):
        name = "ColorAttribute"

        def __init__(self, context, event):
            super().__init__(context, event)
            self.prev_active_idx_ca = context.object.data.color_attributes.active_color_index

        def modal(self, context, event, input):
            super().modal(context, event, input)
            if self.current_active_idx != -1 and context.object.data.color_attributes.active_color_index != self.current_active_idx:
                context.object.data.color_attributes.active_color_index = self.current_active_idx
                context.object.data.color_attributes.render_color_index = self.current_active_idx
            return None

        def on_close(self, context, is_cancel):
            if is_cancel:
                if -1 < self.prev_active_idx_ca:
                    context.object.data.color_attributes.active_color_index = self.prev_active_idx_ca
                    context.object.data.color_attributes.render_color_index = self.prev_active_idx_ca

        def on_mode_change(self, context):
            super().on_mode_change(context)
            self.current_active_idx = context.object.data.color_attributes.active_color_index
            self.reserved_mode = "VERTEX_PAINT"

        def draw_key_info(self, x, y):
            w = _UtilBlf.draw_label_dimensions("Activate")[0]*2
            _UtilBlf.draw_key_info("Activate", "| mousehover", x, y)
            _UtilBlf.draw_key_info("Apply", "| left-click", x := x+w, y)
            _UtilBlf.draw_key_info("Cancel", "| right-click, ESC", x := x+w, y)
            _UtilBlf.draw_key_info("MovePanel", "| G", x := x+w, y)

        def draw_list(self):

            obj = bpy.context.object
            x, y = self.get_items_start_position()
            if obj.data.color_attributes and len(obj.data.color_attributes) == 0:
                _UtilBlf.draw_label("No ColorAttributes found.", x, y)
                return

            def __label(i, ca, is_fullname):
                return ca.name if is_fullname else ca.name[:self.SHOW_STR_CNT] + (".." if self.SHOW_STR_CNT < len(ca.name) else "")
            self._draw_label_list(obj.data.color_attributes, __label)

    class DrawerBoneCollection(DrawerBase):
        name = "BoneCollection"

        def __init__(self, context, event):
            super().__init__(context, event)
            self.prev_active_idx_ca = context.object.data.color_attributes.active_color_index
            self.arm = _Util.get_armature(context.object)

        def modal(self, context, event, input):
            super().modal(context, event, input)
            if self.current_active_idx != -1 and not self.arm.data.collections_all[self.current_active_idx].is_solo:
                for i, bc in enumerate(self.arm.data.collections_all):
                    bc.is_solo = i == self.current_active_idx
            return None

        def on_close(self, context, is_cancel):
            for i, bc in enumerate(self.arm.data.collections_all):
                bc.is_solo = False

        def on_mode_change(self, context):
            super().on_mode_change(context)

        def draw_key_info(self, x, y):
            w = _UtilBlf.draw_label_dimensions("Activate")[0]*2
            _UtilBlf.draw_key_info("Activate", "| mousehover", x, y)
            _UtilBlf.draw_key_info("Apply", "| left-click", x := x+w, y)
            _UtilBlf.draw_key_info("Cancel", "| right-click, ESC", x := x+w, y)
            _UtilBlf.draw_key_info("MovePanel", "| G", x := x+w, y)

        def draw_list(self):
            x, y = self.get_items_start_position()
            if len(self.arm.data.collections_all) == 0:
                _UtilBlf.draw_label("No BoneCollection found.", x, y)
                return

            def __label(i, bc, is_fullname):
                return bc.name if is_fullname else bc.name[:self.SHOW_STR_CNT] + (".." if self.SHOW_STR_CNT < len(bc.name) else "")
            self._draw_label_list(self.arm.data.collections_all, __label)


# --------------------------------------------------------------------------------


classes = [
    MPM_OT_SwitchObjectDataModal,
]


def register():
    _Util.register_classes(classes)


def unregister():
    _Util.unregister_classes(classes)
