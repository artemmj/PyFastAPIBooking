from pydantic import BaseModel, ConfigDict


class RoomSchema(BaseModel):
    id: int
    hotel_id: int
    name: str
    description: str
    price: int
    options: list[str]
    quantity: int
    image_id: int

    model_config = ConfigDict(from_attributes=True)


class NewRoomSchema(BaseModel):
    hotel_id: int
    name: str
    description: str
    price: int
    options: list[str]
    quantity: int
    image_id: int


class RoomsOptionsSchema(BaseModel):
    title: str


class RoomsOptionsFilterSchema(BaseModel):
    options: list[str]
