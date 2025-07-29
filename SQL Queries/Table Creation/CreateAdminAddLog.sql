create table {AdminAddLogTable} (
    "logID" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "userID" UUID NOT NULL,
    "roomID" UUID NOT NULL,

    PRIMARY KEY("logID"),

    FOREIGN KEY("userID") REFERENCES {UserTable}("userID")
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY("roomID") REFERENCES {RoomTable}("roomID")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);