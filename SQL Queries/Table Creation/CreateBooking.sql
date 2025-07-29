CREATE TABLE {BookingTable} (
    "bookingID" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "userID" UUID NOT NULL,
    "roomID" UUID NOT NULL,
    "bookDateTime" TIMESTAMP WITHOUT TIME ZONE,
    "bookStartDateTime" TIMESTAMP WITHOUT TIME ZONE,
    "bookEndDateTime" TIMESTAMP WITHOUT TIME ZONE,
    "participants" INT,

    PRIMARY KEY("bookingID"),
    FOREIGN KEY("userID") REFERENCES {UserTable}("userID")
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY("roomID") REFERENCES {RoomTable}("roomID")
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT validBookingCommitDate CHECK({BookingTable}."bookDateTime" < {BookingTable}."bookStartDateTime"),
    CONSTRAINT validBookingRange CHECK({BookingTable}."bookStartDateTime" < {BookingTable}."bookEndDateTime"),
    CONSTRAINT bookingStartWindow CHECK ("bookStartDateTime"::time >= TIME '07:00'),
    CONSTRAINT bookingEndWindow CHECK ("bookEndDateTime"::time <= TIME '23:00')
);

CREATE INDEX IF NOT EXISTS idx_user_start_time
ON {BookingTable}("userID", "bookStartDateTime");

CREATE INDEX IF NOT EXISTS idx_user
ON {BookingTable}("userID");

CREATE INDEX IF NOT EXISTS idx_room
ON {BookingTable}("roomID");