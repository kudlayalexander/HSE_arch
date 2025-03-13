import subprocess

from celery.utils.log import get_task_logger

from ..config import server_settings
from ..enums import DeviceType
from ..exceptions import ReceivingPasswordError
from ..enums import ImageType, SshUser

logger = get_task_logger("SshTask")


def get_password(user: str, image_type: ImageType, device_type: DeviceType) -> str:
    if user == SshUser.ROOT:
        if image_type == ImageType.DEV:
            return server_settings.SSH_SETTINGS.DEV_PASSWORD

        if image_type == ImageType.RELEASE:
            return get_release_password(device_type)

        raise ReceivingPasswordError(
            f"Don't know password for image of type: {image_type}")


def get_release_password(device_type: DeviceType):
    path: str = server_settings.SSH_SETTINGS.PASSWORD_UPLOADER_BIN_PATH
    request_type: str = server_settings.SSH_SETTINGS.REQUEST_TYPE
    command = f"{path} {request_type} {device_type}"

    timeout_s: int = 15

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, shell=True, check=True, timeout=timeout_s)

        return result.stdout
    except subprocess.CalledProcessError as exc:
        raise ReceivingPasswordError(
            f"Got exception when tried to request release password from server. Return code: {exc.returncode}. ")
    except subprocess.TimeoutExpired as exc:
        raise ReceivingPasswordError(
            f"Process was running more than {timeout_s}, process stopped."
        )
    except Exception as exc:
        raise ReceivingPasswordError(
            f"Unexpected exception. Exception: {str(exc)}. Type: {type(exc)}"
        )
