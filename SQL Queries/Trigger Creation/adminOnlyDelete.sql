CREATE TRIGGER "CheckAdminBeforeInsert_Delete"
BEFORE INSERT ON {AdminDeleteLogTable}
FOR EACH ROW
EXECUTE FUNCTION {AdminOnlyFunc}();