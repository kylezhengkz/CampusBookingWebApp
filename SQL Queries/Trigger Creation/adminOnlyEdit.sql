CREATE TRIGGER "CheckAdminBeforeInsert_Edit"
BEFORE INSERT ON {AdminEditLogTable}
FOR EACH ROW
EXECUTE FUNCTION {AdminOnlyFunc}();