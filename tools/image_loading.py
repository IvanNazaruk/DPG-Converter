from DPG_modules.ImageController import default_controller


class ENABLE_LOADING:
    _default_value: float = default_controller.max_inactive_time

    @classmethod
    def set(cls):
        default_controller.max_inactive_time = cls.default_value

    @classmethod
    def clear(cls):
        cls.default_value = default_controller.max_inactive_time
        default_controller.max_inactive_time = 1_000_000_000
