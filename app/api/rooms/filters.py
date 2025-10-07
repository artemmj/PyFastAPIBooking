from typing import Optional

from fastapi_filter import Filter


class RoomFilter(Filter):
    quantity: Optional[str]
    city__in: Optional[list[str]]

    class Constants(Filter.Constants):
        model = Address
