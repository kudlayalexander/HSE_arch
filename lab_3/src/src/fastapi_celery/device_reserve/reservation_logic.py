from ..device_data.model import Device
from typing import List, Dict
from ..enums import DeviceType
from collections import defaultdict
from ..exceptions import NotEnoughAvailableDevicesError


def count_devices_by_types(devices: List[Device]) -> Dict[DeviceType, int]:
    device_type_count: Dict[DeviceType, int] = defaultdict(int)

    for device in devices:
        device_type_count[device.type] += 1

    return device_type_count


def is_enough_devices(devices: List[Device], requested_types: Dict[DeviceType, int]) -> bool:
    current_types_count = count_devices_by_types(devices)

    for requested_type, amount in requested_types.items():
        if requested_type not in current_types_count or current_types_count[requested_type] < amount:
            return False

    return True


def select_devices_to_reserve(available_devices: List[Device], requested_types: Dict[DeviceType, int]) -> List[Device]:
    if not is_enough_devices(available_devices, requested_types):
        raise NotEnoughAvailableDevicesError(
            "Not enough available devices to select from")

    device_types_to_select = requested_types.copy()

    selected_devices: List[Device] = []

    for device in available_devices:
        if device.type in requested_types and device_types_to_select[device.type] > 0:
            selected_devices.append(device)
            device_types_to_select[device.type] -= 1

    return selected_devices
