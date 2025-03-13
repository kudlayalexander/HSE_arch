import json
from typing import Annotated, Any, List, Literal

from pydantic import (AnyUrl, BeforeValidator, Field, PostgresDsn,
                      computed_field)
from pydantic_core import MultiHostUrl, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from .bolid.schemas import BolidCreateSchema
from .device_data.schemas import DeviceCreateSchema


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_ignore_empty=True, extra="ignore")
    DOMAIN: str = 'localhost'
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    @computed_field
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    POSTGRESQL_USER: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_SERVER: str
    POSTGRESQL_PORT: int
    POSTGRESQL_DB: str

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRESQL_USER,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_SERVER,
            port=self.POSTGRESQL_PORT,
            path=self.POSTGRESQL_DB,
        )

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str


class Rs232Settings(BaseSettings):
    DEFAULT_BAUDRATE: int = Field(gt=0, examples=[115200])
    DEFAULT_BYTESIZE: int = Field(gt=0, examples=[8])
    DEFAULT_PARITY: str = Field(examples=["N"])
    DEFAULT_STOPBITS: int = Field(gt=0, examples=[1])


class SshSettings(BaseSettings):
    PASSWORD_UPLOADER_BIN_PATH: str
    REQUEST_TYPE: str
    DEV_PASSWORD: str


class ImageSettings(BaseSettings):
    FOLDER_PATH: str
    VALID_EXTS: List[str]


class BolidSettings(BaseSettings):
    PIN_AMOUNT: int


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(extra='forbid')

    RS232_SETTINGS: Rs232Settings
    SSH_SETTINGS: SshSettings
    IMAGE_SETTINGS: ImageSettings
    DEVICES: List[DeviceCreateSchema]
    BOLIDS: List[BolidCreateSchema]


def load_server_settings_from_json(json_file: str) -> ServerSettings:
    """Loads the configuration from a JSON file."""
    try:
        with open(json_file, 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {json_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {json_file}: {e}")

    try:
        return ServerSettings.model_validate(config_data)
    except ValidationError as e:
        raise ValueError(f"Configuration validation error: {e}")


env_settings = EnvSettings()
server_settings = load_server_settings_from_json(
    "src/fastapi_celery/config.json")
