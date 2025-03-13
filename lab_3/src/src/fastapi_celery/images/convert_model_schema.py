from .schemas import ImageSchema
from .model import Image


def convert_from_model_to_schema(model: Image) -> ImageSchema:
    schema = ImageSchema(
        id=model.id,
        type=model.type,
        version=model.version,
        commit=model.commit,
        filename=model.filename
    )

    return schema
