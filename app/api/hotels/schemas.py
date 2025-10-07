from pydantic import BaseModel, ConfigDict


class HotelSchema(BaseModel):
    id: int
    name: str
    address: str
    image_id: int

    model_config = ConfigDict(from_attributes=True)


class NewHotelSchema(BaseModel):
    name: str
    address: str
    image_id: int
