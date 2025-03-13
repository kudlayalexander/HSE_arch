from .schemas import ReservationSchema
from .model import Reservation


def convert_from_model_to_schema(model: Reservation) -> ReservationSchema:
    schema = ReservationSchema(
        id=model.id,
        reserved_by=model.reserved_by,
        time_start=model.time_start,
        time_end=model.time_end
    )

    return schema
