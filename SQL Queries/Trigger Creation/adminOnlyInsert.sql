CREATE TRIGGER "CheckAdminBeforeInsert_Add"
BEFORE INSERT ON {AdminAddLogTable}
FOR EACH ROW
EXECUTE FUNCTION {AdminOnlyFunc}();