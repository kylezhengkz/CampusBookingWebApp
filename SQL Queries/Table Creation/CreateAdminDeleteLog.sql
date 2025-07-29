create table {AdminDeleteLogTable} (
    "logID" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "userID" UUID NOT NULL,
    "roomName" TEXT,
    "capacity" INT,
    "buildingName" TEXT NOT NULL,
    "addressLine1" TEXT NOT NULL,
    "addressLine2" TEXT NOT NULL,
    "city" TEXT NOT NULL,
    "province" TEXT NOT NULL,
    "country" TEXT NOT NULL,
    "postalCode" TEXT NOT NULL,

    PRIMARY KEY("logID"),

    FOREIGN KEY("userID") REFERENCES {UserTable}("userID")
);