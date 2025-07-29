from enum import Enum


class DBFuncNames(Enum):
    CheckBookingParticipants = "checkBookingParticipants"
    CheckCancellationDateTime = "checkCancellationDateTime"
    CheckBookingUserOverlap = "checkBookingUserOverlap"
    CheckAdminOnly = "checkAdminOnly"