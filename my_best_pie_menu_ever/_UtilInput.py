
key_pressed_dict: dict[str, (bool, bool)] = {}


@staticmethod
def init():
    for key in key_pressed_dict:
        key_pressed_dict[key] = (False, False)


@staticmethod
def update(event, *keys):
    # Releaseされるまで押下判定しないようにする。
    def __proc(event, key):
        if event.type == key:
            if event.value == "PRESS":
                is_current, is_prev = key_pressed_dict.get(key, (False, False))
                key_pressed_dict[key] = (True, is_current)
            elif event.value == "RELEASE":
                key_pressed_dict[key] = (False, False)
        else:
            is_current = key_pressed_dict.get(key, (False, False))[0]
            key_pressed_dict[key] = (is_current, is_current)
    for key in keys:
        __proc(event, key)


@staticmethod
def is_keydown(*keys):
    for key in keys:
        is_current, is_prev = key_pressed_dict.get(key, (False, False))
        if is_current and not is_prev:
            return True
    return False


@staticmethod
def is_keyup(event, key):
    return event.type == key and event.value == "RELEASE"
