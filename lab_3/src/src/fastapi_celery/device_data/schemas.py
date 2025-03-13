from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field, field_validator

from ..enums import (DeviceReservationStatus, DeviceConnectionStatus, DeviceTestStage,
                     DeviceType, DeviceTypeGroup, StandUser)

from ..device_pin_control.schemas import BolidPinCreateSchema

def convert_type_to_group(type: DeviceType) -> DeviceTypeGroup:
    if type in [DeviceType.V1, DeviceType.V2, DeviceType.V2_LTE]:
        return DeviceTypeGroup.OBU

    return DeviceTypeGroup.RSU


class DeviceSchema(BaseModel):
    hostname: str
    type: DeviceType
    mac: str
    ip: str
    https_port: int
    ws_port: int
    rs232_port: str
    output_power_id: str
    output_boot_id: str
    reservation_status: Optional[DeviceReservationStatus] = DeviceReservationStatus.AVAILABLE
    image_id: Optional[str] = Field(default=None)
    reservation_id: Optional[str] = Field(default=None)
    connection_status: Optional[DeviceConnectionStatus] = Field(default=None)
    test_stage: Optional[DeviceTestStage] = Field(default=None)

    @computed_field
    @property
    def type_group(self) -> DeviceTypeGroup:
        return convert_type_to_group(self.type)

    class Config:
        from_attributes = True


class DeviceCreateSchema(BaseModel):
    hostname: str
    type: DeviceType
    mac: str
    ip: str
    https_port: int
    ws_port: int
    rs232_port: str
    output_power: BolidPinCreateSchema
    output_boot: BolidPinCreateSchema

    @computed_field
    @property
    def type_group(self) -> DeviceTypeGroup:
        return convert_type_to_group(self.type)

class DeviceUpdateSchema(BaseModel):
    reservation_status: Optional[DeviceReservationStatus]
    connection_status: Optional[DeviceConnectionStatus]
    test_stage: Optional[DeviceTestStage]
