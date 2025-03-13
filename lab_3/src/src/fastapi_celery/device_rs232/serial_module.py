from ..config import server_settings
import serial

import logging

logger = logging.getLogger("DutSerialModule")


def connect_via_serial(port: str, baudrate: int, timeout: int) -> serial.SerialBase:
    """
    Connects to the device via RS232
    """
    if baudrate is None:
        baudrate = server_settings.RS232_SETTINGS.DEFAULT_BAUDRATE

    ser = serial.Serial(
        port,
        baudrate,
        bytesize=server_settings.RS232_SETTINGS.DEFAULT_BYTESIZE,
        parity=server_settings.RS232_SETTINGS.DEFAULT_PARITY,
        stopbits=server_settings.RS232_SETTINGS.DEFAULT_STOPBITS,
        timeout=timeout
    )
    logger.debug(
        f"Started connection. Port: {port}. Baudrate: {baudrate}. Timeout: {timeout}. 8N1")
    return ser


def read_from_serial(ser: serial.Serial) -> str:
    output = b''

    while True:
        data = ser.read(1)
        if data:
            output += data
        else:
            break

    logger.debug(
        f"Serial: {ser.port}. \nRead:\n'{output.decode(errors="ignore")}'")

    return output.decode(errors="ignore")


def write_to_serial(ser: serial.Serial, text: str) -> None:
    byte_text = text.encode()
    ser.write(byte_text)

    logger.debug(f"Serial: {ser.port}. \nWrote:\n'{byte_text}'")
