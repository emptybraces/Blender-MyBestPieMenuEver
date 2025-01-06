
key_pressed_dict: dict[str, bool] = {}


@staticmethod
def init():
    for key in key_pressed_dict:
        key_pressed_dict[key] = False


@staticmethod
def is_pressed_key(event, key):
    if event.type == key:
        is_pressed_down = False
        if event.value == "PRESS":
            is_pressed_down = not key_pressed_dict.get(key, False)
            key_pressed_dict[key] = True
        elif event.type == key and event.value == "RELEASE":
            key_pressed_dict[key] = False
        return is_pressed_down, key_pressed_dict.get(key, False)
    return False, False


@staticmethod
def is_pressed_keys(event, *keys):
    for key in keys:
        if event.type == key and event.value == "PRESS":
            return True
    return False
