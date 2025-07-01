class Monitor:

    def __init__(self):
        self.key_pressed_dict: dict[str, (bool, bool)] = {}

    def update(self, event, *keys):
        # Releaseされるまで押下判定しないようにする。
        def __proc(event, key):
            if event.type == key:
                if event.value == "PRESS":
                    is_current, is_prev = self.key_pressed_dict.get(key, (False, False))
                    self.key_pressed_dict[key] = (True, is_current)
                elif event.value == "RELEASE":
                    self.key_pressed_dict[key] = (False, False)
            else:
                is_current = self.key_pressed_dict.get(key, (False, False))[0]
                self.key_pressed_dict[key] = (is_current, is_current)
        for key in keys:
            __proc(event, key)

    def is_keydown(self, *keys):
        for key in keys:
            is_current, is_prev = self.key_pressed_dict.get(key, (False, False))
            if is_current and not is_prev:
                return True
        return False

    def is_keyup(self, event, key):
        return event.type == key and event.value == "RELEASE"
