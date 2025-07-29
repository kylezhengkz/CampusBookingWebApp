from enum import Enum


class TableNames(Enum):
    User = "User"
    Buiding = "Building"
    Booking = "Booking"
    Room = "Room"
    Cancellation = "Cancellation"
    AdminAddLog = "AdminAddLog"
    AdminEditLog = "AdminEditLog"
    AdminDeleteLog = "AdminDeleteLog"