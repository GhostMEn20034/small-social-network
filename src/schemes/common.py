from datetime import date

from pydantic import BaseModel


class DateRange(BaseModel):
    date_from: date
    date_to: date
