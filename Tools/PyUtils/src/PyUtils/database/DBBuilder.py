import psycopg2
from psycopg2.sql import SQL, Identifier
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from typing import Union, Optional, List, Any, Dict, Tuple

from ..constants.TableNames import TableNames
from ..constants.DBFuncNames import DBFuncNames
from ..constants.Paths import Paths
from .DBTool import DBTool
from .DBConnData import DBConnData


# DBBuilder: Class to build tables and databases
class DBBuilder():
    NameIdentifiers = {"UserTable": Identifier(TableNames.User.value),
                       "BuildingTable": Identifier(TableNames.Buiding.value),
                       "RoomTable": Identifier(TableNames.Room.value),
                       "BookingTable": Identifier(TableNames.Booking.value),
                       "CancellationTable": Identifier(TableNames.Cancellation.value),
                       "AdminAddLogTable": Identifier(TableNames.AdminAddLog.value),
                       "AdminEditLogTable": Identifier(TableNames.AdminEditLog.value),
                       "AdminDeleteLogTable": Identifier(TableNames.AdminDeleteLog.value),
                        
                       "BookingParticipantsCheckFunc": Identifier(DBFuncNames.CheckBookingParticipants.value),
                       "CancellationDateTimeCheckFunc": Identifier(DBFuncNames.CheckCancellationDateTime.value),
                       "BookingUserOverlapCheckFunc": Identifier(DBFuncNames.CheckBookingUserOverlap.value),
                       "AdminOnlyFunc": Identifier(DBFuncNames.CheckAdminOnly.value)}

    def __init__(self, dbTool: DBTool):
        self._dbTool = dbTool
    
    # _setExtensions(): Sets the required extensions in the database
    def _setExtensions(self):
        sql = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'
        self._dbTool.executeSQL(sql, commit = True)

    # _grantOwnership(table, closeConn, connData): Grants ownership to the table
    def _grantOwnership(self, table: str, closeConn: bool = True, connData: Optional[DBConnData] = None):
        sql = SQL(f"ALTER TABLE IF EXISTS {{table}} OWNER to {{dbuser}}").format(table = Identifier(table), 
                                                                                 dbuser = Identifier(self._dbTool._secrets.username))
        self._dbTool.executeSQL(sql, vars = vars, commit = True, connData = connData, closeConn = closeConn)

    # _buildTable(table, sql, vars, closeConn, connData): Builds some generic table
    def _buildTable(self, table: str, sql: Union[str, SQL], vars: Optional[Union[List[Any], Dict[str, Any]]] = None, connData: Optional[DBConnData] = None, 
                    closeConn: bool = True, installExtensions: bool = True) -> Tuple[DBConnData, Optional[psycopg2.extensions.cursor]]:

        if (installExtensions):
            self._setExtensions()

        connData, cursor, error = self._dbTool.executeSQL(sql, vars = vars, closeConn = False, commit = True, connData = connData)
        self._grantOwnership(table, closeConn = closeConn, connData = connData)

        return (connData, cursor)

    # _buildTableFromFile(table, identifiers, vars, closeConn, connData, installExtensions): Builds some generic table based on some file
    def _buildTableFromFile(self, table: str, file: str, identifiers: Optional[Dict[str, Identifier]] = None, 
                            vars: Optional[Union[List[Any], Dict[str, Any]]] = None, closeConn: bool = True, 
                            connData: Optional[DBConnData] = None, installExtensions: bool = True) -> Tuple[DBConnData, Optional[psycopg2.extensions.cursor]]:
        
        if (identifiers is None):
            identifiers = {}

        sql = self._dbTool.readSQLFile(file)
        sql = SQL(sql).format(**identifiers)
        return self._buildTable(table, sql, vars = vars, closeConn = closeConn, connData = connData, installExtensions = installExtensions)

    # _buildTrigger(sql, vars, closeConn, connData): Builds a trigger
    def _buildTrigger(self, sql: Union[str, SQL], vars: Optional[Union[List[Any], Dict[str, Any]]] = None, closeConn: bool = True, 
                      connData: Optional[DBConnData] = None) -> Tuple[DBConnData, Optional[psycopg2.extensions.cursor]]:

        connData, cursor, error = self._dbTool.executeSQL(sql, vars = vars, closeConn = closeConn, commit = True, connData = connData)
        return connData, cursor

    # _buildTriggerFromFile(file, vars, closeConn, connData): Builds a trigger based on some file
    def _buildTriggerFromFile(self, file: str, identifiers: Optional[Dict[str, Identifier]] = None, 
                              vars: Optional[Union[List[Any], Dict[str, Any]]] = None, closeConn: bool = True, 
                              connData: Optional[DBConnData] = None) -> Tuple[DBConnData, Optional[psycopg2.extensions.cursor]]:

        if (identifiers is None):
            identifiers = {}

        sql = self._dbTool.readSQLFile(file)
        sql = SQL(sql).format(**identifiers)
        return self._buildTrigger(sql, vars = vars, closeConn = closeConn, connData = connData)

    # ============================================================
    # =========== Triggers/ Trigger Functions ====================

    # buildCheckParticipantTrigger(connData): Build the trigger for checking participants in a booking
    def buildCheckParticipantTrigger(self, connData: Optional[DBConnData] = None, closeConn: bool = True):
        checkParticipantTriggerFile = os.path.join(Paths.SQLTriggerCreationFolder.value, "validBooking.sql")
        self._buildTriggerFromFile(checkParticipantTriggerFile, identifiers = self.NameIdentifiers, connData = connData, closeConn = closeConn)

    # buildValidCancellationTrigger(connData): Build the trigger for checking if a cancellation is valid
    def buildValidCancellationTrigger(self, connData: Optional[DBConnData] = None, closeConn: bool = True):
        checkCancelDateTriggerFile = os.path.join(Paths.SQLTriggerCreationFolder.value, "validCancellation.sql")
        self._buildTriggerFromFile(checkCancelDateTriggerFile, identifiers = self.NameIdentifiers, connData = connData, closeConn = closeConn)

    # buildAdminOnlyTriggerFunc(connData): Build the trigger function to check whether 
    def buildAdminOnlyTriggerFunc(self, connData: Optional[DBConnData] = None, closeConn: bool = True):
        sqlFile = os.path.join(Paths.SQLTriggerCreationFolder.value, "adminOnly.sql")
        self._buildTriggerFromFile(sqlFile, identifiers = self.NameIdentifiers, connData = connData, closeConn = closeConn)

    # buildAdminOnlyDeleteTrigger(connData): Build the trigger to check if the user is an admin when doing some deletions
    def buildAdminOnlyDeleteTrigger(self, connData: Optional[DBConnData] = None, closeConn: bool = True):
        sqlFile = os.path.join(Paths.SQLTriggerCreationFolder.value, "adminOnlyDelete.sql")
        self._buildTriggerFromFile(sqlFile, identifiers = self.NameIdentifiers, connData = connData, closeConn = closeConn)

    # buildAdminOnlyEditTrigger(connData): Build the trigger to check if the user is an admin when doing some edits
    def buildAdminOnlyEditTrigger(self, connData: Optional[DBConnData] = None, closeConn: bool = True):
        sqlFile = os.path.join(Paths.SQLTriggerCreationFolder.value, "adminOnlyEdit.sql")
        self._buildTriggerFromFile(sqlFile, identifiers = self.NameIdentifiers, connData = connData, closeConn = closeConn)

    # buildAdminOnlyInsertTrigger(connData): Build the trigger to check if the user is an admin when doing insertions
    def buildAdminOnlyInsertTrigger(self, connData: Optional[DBConnData] = None, closeConn: bool = True):
        sqlFile = os.path.join(Paths.SQLTriggerCreationFolder.value, "adminOnlyInsert.sql")
        self._buildTriggerFromFile(sqlFile, identifiers = self.NameIdentifiers, connData = connData, closeConn = closeConn)

    # ============================================================
    # ================= Tables ===================================


    # buildUserTable(installExtensions): Builds the table for the Users
    def buildUserTable(self, installExtensions: bool = True):
        sqlFile = os.path.join(Paths.SQLTableCreationFolder.value, "CreateUser.sql")
        self._buildTableFromFile(TableNames.User.value, sqlFile, identifiers = self.NameIdentifiers, installExtensions = installExtensions)

    # buildBuildingTable(installExtensions): Builds the table for the Buildings
    def buildBuildingTable(self, installExtensions: bool = True):
        sqlFile = os.path.join(Paths.SQLTableCreationFolder.value, "CreateBuilding.sql")
        self._buildTableFromFile(TableNames.Buiding.value, sqlFile, identifiers = self.NameIdentifiers, installExtensions = installExtensions)

    # buildRoomTable(installExtensions): Builds the table for the rooms
    def buildRoomTable(self, installExtensions: bool = True):
        sqlFile = os.path.join(Paths.SQLTableCreationFolder.value, "CreateRoom.sql")
        self._buildTableFromFile(TableNames.Room.value, sqlFile, identifiers = self.NameIdentifiers, installExtensions = installExtensions)

    # buildBookingTable(installExtensions): Builds the table for the bookings
    def buildBookingTable(self, installExtensions: bool = True, withTriggers: bool = True):
        sqlFile = os.path.join(Paths.SQLTableCreationFolder.value, "CreateBooking.sql")
        connData, cursor = self._buildTableFromFile(TableNames.Room.value, sqlFile, identifiers = self.NameIdentifiers, installExtensions = installExtensions, closeConn = not withTriggers)

        if (withTriggers):
            self.buildCheckParticipantTrigger(connData = connData)

    # buildCancellationTable(installExtensions, withTriggers): Builds the table for the cancellations
    def buildCancellationTable(self, installExtensions: bool = True, withTriggers: bool = True):
        sqlFile = os.path.join(Paths.SQLTableCreationFolder.value, "CreateCancellation.sql")
        connData, cursor = self._buildTableFromFile(TableNames.Room.value, sqlFile, identifiers = self.NameIdentifiers, installExtensions = installExtensions, closeConn = not withTriggers)

        if (withTriggers):
            self.buildValidCancellationTrigger(connData = connData)

    # buildAdminAddLogTable(installExtensions, withTriggerFunc, withTriggers): Builds the table for the admin addition log
    def buildAdminAddLogTable(self, installExtensions: bool = True, withTriggerFunc: bool = True, withTriggers: bool = True):
        sqlFile = os.path.join(Paths.SQLTableCreationFolder.value, "CreateAdminAddLog.sql")
        connData, cursor = self._buildTableFromFile(TableNames.AdminAddLog.value, sqlFile, identifiers = self.NameIdentifiers, installExtensions = installExtensions, closeConn = not (withTriggers or withTriggerFunc))

        if (withTriggerFunc):
            self.buildAdminOnlyTriggerFunc(connData = connData, closeConn = not withTriggers)

        if (withTriggers):
            self.buildAdminOnlyInsertTrigger(connData = connData)

    # buildAdminEditLogTable(installExtensions, withTriggerFunc, withTriggers): Builds the table for the admin edit log
    def buildAdminEditLogTable(self, installExtensions: bool = True, withTriggerFunc: bool = True, withTriggers: bool = True):
        sqlFile = os.path.join(Paths.SQLTableCreationFolder.value, "CreateAdminEditLog.sql")
        connData, cursor = self._buildTableFromFile(TableNames.AdminEditLog.value, sqlFile, identifiers = self.NameIdentifiers, installExtensions = installExtensions, closeConn = not (withTriggers or withTriggerFunc))

        if (withTriggerFunc):
            self.buildAdminOnlyTriggerFunc(connData = connData, closeConn = not withTriggers)

        if (withTriggers):
            self.buildAdminOnlyEditTrigger(connData = connData)

    # buildAdminDeleteLogTable(installExtensions): Builds the table for the admin delete log
    def buildAdminDeleteLogTable(self, installExtensions: bool = True, withTriggerFunc: bool = True, withTriggers: bool = True):
        sqlFile = os.path.join(Paths.SQLTableCreationFolder.value, "CreateAdminDeleteLog.sql")
        connData, cursor = self._buildTableFromFile(TableNames.AdminDeleteLog.value, sqlFile, identifiers = self.NameIdentifiers, installExtensions = installExtensions, closeConn = not (withTriggers or withTriggerFunc))

        if (withTriggerFunc):
            self.buildAdminOnlyTriggerFunc(connData = connData, closeConn = not withTriggers)

        if (withTriggers):
            self.buildAdminOnlyDeleteTrigger(connData = connData)

    # buildTables(): Builds all the necessary tables
    def buildTables(self, withTriggers: bool = True):
        self.buildUserTable()
        self.buildBuildingTable(installExtensions = False)
        self.buildRoomTable(installExtensions = False)
        self.buildBookingTable(installExtensions = False, withTriggers = withTriggers)
        self.buildCancellationTable(installExtensions = False, withTriggers = withTriggers)

        self.buildAdminAddLogTable(installExtensions = False, withTriggers = withTriggers, withTriggerFunc = withTriggers)
        self.buildAdminEditLogTable(installExtensions = False, withTriggers = withTriggers, withTriggerFunc = False)
        self.buildAdminDeleteLogTable(installExtensions = False, withTriggers = withTriggers, withTriggerFunc = False)

    # buildTriggers(); Builds all the necessary triggers
    def buildTriggers(self):
        connData = self._dbTool.getConn()
        self.buildCheckParticipantTrigger(connData = connData, closeConn = False)
        self.buildValidCancellationTrigger(connData = connData, closeConn = False)
        self.buildAdminOnlyTriggerFunc(connData = connData, closeConn = False)
        self.buildAdminOnlyDeleteTrigger(connData = connData, closeConn = False)
        self.buildAdminOnlyEditTrigger(connData = connData, closeConn = False)
        self.buildAdminOnlyInsertTrigger(connData = connData)

    # buildDB(database): Creates a database
    def buildDB(self, database: Optional[str] = None):
        if (database is None):
            database = self._dbTool.database

        sqlFile = os.path.join(Paths.SQLDBCreationFolder.value, "CreateDatabase.sql")
        identifiers = {"DatabaseName": Identifier(database), "OwnerName": Identifier(self._dbTool._secrets.username)}

        sql = self._dbTool.readSQLFile(sqlFile)
        sql = SQL(sql).format(**identifiers)

        connData = DBConnData(conn = self._dbTool.connectDB(defaultDB = True))
        connData.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # Needed for creating/deleting databases

        self._dbTool.executeSQL(sql, vars = vars, connData = connData)

    # build(createDatabase): Build the all the required database and tabless
    def build(self, createDB: bool = False):
        if (createDB):
            self.buildDB()

        self.buildTables()

    # ============================================================