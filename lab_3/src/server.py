import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.fastapi_celery.config import (EnvSettings, ServerSettings,
                                       env_settings, server_settings)
from src.fastapi_celery.database import engine
from src.fastapi_celery.dependencies import Base
from src.fastapi_celery.device_data.views import router as device_data_router
from src.fastapi_celery.device_reserve.views import \
    router as device_reserve_router
from src.fastapi_celery.device_rs232.views import router as device_rs232_router
from src.fastapi_celery.device_ssh.views import router as device_ssh_router
from src.fastapi_celery.bolid.views import router as bolid_router
from src.fastapi_celery.device_pin_control.views import router as device_pin_control_router
from src.fastapi_celery.exceptions import BaseException
from src.fastapi_celery.images.views import router as images_router
from src.fastapi_celery.init_database import init_devices, init_bolids, clear_tables
from src.fastapi_celery.docs import title, tags_metadata, description

logger = logging.getLogger()

Base.metadata.create_all(bind=engine)

clear_tables()
init_bolids()
init_devices()

app = FastAPI(title=title, description=description, tags_metadata=tags_metadata)

if env_settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in env_settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(device_data_router, prefix='/api', tags=["Device Data"])
app.include_router(device_ssh_router, prefix='/api', tags=["Device SSH"])
app.include_router(device_rs232_router, prefix='/api', tags=["Device RS232"])
app.include_router(images_router, prefix='/api', tags=["Image"])
app.include_router(device_reserve_router, prefix='/api', tags=["Device Reserve"])
app.include_router(bolid_router, prefix='/api', tags=["Bolid"])
app.include_router(device_pin_control_router, prefix='/api', tags=["Device Pin Control"])


@app.exception_handler(BaseException)
async def app_exception_handler(request, exc: BaseException):
    logger.error("Application error: %s", exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
