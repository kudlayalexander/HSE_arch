from enum import StrEnum

# --- Device properties ---


class DeviceReservationStatus(StrEnum):
    AVAILABLE = 'available'
    RESERVED = 'reserved'


class DeviceTestStage(StrEnum):
    NONE = 'none'
    INSTALLING_IMAGE = 'installing_image'
    RELOADING = 'reloading'
    SETTING_LICENSE = 'setting_license'
    MANUAL_TEST = 'manual_test'
    AUTO_TEST = 'auto_test'


class DeviceConnectionStatus(StrEnum):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'


class DeviceType(StrEnum):
    V1 = 'tedix-v1-02'
    V2 = 'tedix-v2-02'
    V2_LTE = 'tedix-v2-lte-02'
    R1 = 'tedix-r1-02'
    R2D1 = 'tedix-r2d1-02'
    R2D1_RTK = 'tedix-r2d1-rtk-02'
    R2D2_RTK = 'tedix-r2d2-rtk-02'


class DeviceTypeGroup(StrEnum):
    OBU = 'obu'
    RSU = 'rsu'


class StandUser(StrEnum):
    NONE = 'none'
    BAKANOV = 'Баканов Д.'
    BAKHMATOV = 'Бахматов Д.'
    EROKHIN = 'Ерохин В.'
    GAREEV = 'Гареев Т.'
    KLEPTSIN = 'Клепцин А.'
    KRASILOV = 'Красилов А.'
    KOCHKIN = 'Кочкин Е.'
    KUDLAY = 'Кудлай А.'
    MIKOV = 'Миков И.'
    OTHER = 'Другой'
    GITLAB = 'GITLAB'

# --- Request properties ---


class TaskStatus(StrEnum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    FINISHED = 'finished'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class TaskType(StrEnum):
    BOOKING = 'device_booking'
    SSH = 'device_ssh'
    RELOAD = 'device_reload'
    INSTALL = 'device_install'
    SET_LICENSE = 'device_set_license'
    RS232 = 'device_rs232'

# --- Modbus properties ---


class ModbusName(StrEnum):
    POWER = 'power'
    BOOT = 'boot'

# --- Image properties ---


class ImageType(StrEnum):
    NONE = 'none'
    DEV = 'dev'
    RELEASE = 'release'
    OTHER = 'other'


class SshUser(StrEnum):
    ROOT = 'root'

class PinType(StrEnum):
    BOOT = 'boot'
    POWER = 'power'