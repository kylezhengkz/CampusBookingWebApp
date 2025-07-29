DROP TRIGGER IF EXISTS validBooking ON {BookingTable};
DROP FUNCTION IF EXISTS {BookingParticipantsCheckFunc}();
DROP TRIGGER IF EXISTS preventUserOverlap ON {BookingTable};
DROP FUNCTION IF EXISTS {BookingUserOverlapCheckFunc}();

CREATE FUNCTION {BookingParticipantsCheckFunc}() 
    RETURNS trigger
    LANGUAGE plpgsql AS $func$ 
DECLARE
    roomCapacity INT;
BEGIN
    SELECT "capacity" INTO roomCapacity
    FROM {RoomTable} 
    WHERE "roomID" = NEW."roomID";

    IF (NEW."participants" > roomCapacity) THEN
        RAISE EXCEPTION 'RoomOverCapacityError: The number of participants in the booking (%) is not smaller or equal to the capacity of the room (%)', NEW."participants", roomCapacity;
    END IF;

    RETURN NEW;
END; $func$;


CREATE TRIGGER validBooking
BEFORE INSERT OR UPDATE ON {BookingTable}
FOR EACH ROW
    EXECUTE FUNCTION {BookingParticipantsCheckFunc}();


CREATE FUNCTION {BookingUserOverlapCheckFunc}()
RETURNS trigger
LANGUAGE plpgsql AS $func$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM {BookingTable} b
        WHERE b."userID" = NEW."userID"
          AND b."bookingID" <> NEW."bookingID"
          AND DATE(b."bookStartDateTime") = DATE(NEW."bookStartDateTime")
          AND (
              NEW."bookStartDateTime" < b."bookEndDateTime"
              AND NEW."bookEndDateTime" > b."bookStartDateTime"
          )
          AND NOT EXISTS (
              SELECT 1 FROM {CancellationTable} c
              WHERE c."bookingID" = b."bookingID"
          )
    ) THEN
        RAISE EXCEPTION 'User already has an overlapping booking on this day.';
    END IF;

    RETURN NEW;
END;
$func$;

CREATE TRIGGER preventUserOverlap
BEFORE INSERT OR UPDATE ON {BookingTable}
FOR EACH ROW
EXECUTE FUNCTION {BookingUserOverlapCheckFunc}();