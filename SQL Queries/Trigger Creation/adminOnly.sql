CREATE OR REPLACE FUNCTION {AdminOnlyFunc}()
RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM {UserTable} u
    WHERE u."userID" = NEW."userID" AND u."permissionLevel" = 1
  ) THEN
    RAISE EXCEPTION 'Non-admin attempted to execute restricted query';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;