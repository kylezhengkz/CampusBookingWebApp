import os
from datetime import datetime, timezone
import pandas as pd
import pytz
from typing import Optional, Dict, Any, List

import PyUtils as PU

from .BaseAPIService import BaseAPIService

import uuid

class RoomService(BaseAPIService):
    
    @staticmethod
    def _safe_uuid(value):
        try:
            return str(uuid.UUID(value))
        except (ValueError, TypeError):
            return None
    
    def _getModifyRoomError(self, errorMsg: str) -> str:
        if ("duplicate key" in errorMsg):
          return "Room name already exists in building"
        if ("Non-admin" in errorMsg):
          return "Non-admin attempted to execute restricted query"
    
    def fetchRoomsByBuildingID(self, buildingId):
        sqlFile = os.path.join(PU.Paths.SQLFeaturesFolder.value, "R6/GetRoomsByBuildingID.sql")
        sql = PU.DBTool.readSQLFile(sqlFile)
        params = {
            'building_id': RoomService._safe_uuid(buildingId),
        }
        
        sqlEngine = self._dbTool.getSQLEngine()
        result = pd.read_sql(sql, sqlEngine, params = params)
        
        return result.to_dict('records')
    
    # fetchAvailableRooms(roomName, minCapacity, maxCapacity, startTimeStr, endTimeStr): Retrieves all the available rooms
    def fetchAvailableRooms(self, buildingId: Optional[str] = None, roomName: Optional[str] = None, minCapacity:Optional[str] = None, maxCapacity: Optional[str] = None, 
                            startTimeStr: Optional[str] = None, endTimeStr: Optional[str] = None) -> List[Dict[str, Any]]:
        
        useCurrent = True
        current_datetime = datetime.now(timezone.utc)

        if (startTimeStr is not None and endTimeStr is not None):
            useCurrent = False

            try:
                dtStartTime = PU.DateTimeTool.strToDateTime(startTimeStr, tzinfo = pytz.utc)
                dtEndTime = PU.DateTimeTool.strToDateTime(endTimeStr, tzinfo = pytz.utc)
            except ValueError:
                useCurrent = True

        sqlFile = os.path.join(PU.Paths.SQLFeaturesFolder.value, "R6/R6.sql")
        sql = PU.DBTool.readSQLFile(sqlFile)
        
        params = {
            'room_name': f'%{roomName}%' if roomName and roomName.strip() != '' else None,
            'min_capacity': int(minCapacity) if minCapacity is not None and minCapacity.strip() != "" else None,
            'max_capacity': int(maxCapacity) if maxCapacity is not None and maxCapacity.strip() != "" else None,
            'start_time': current_datetime if useCurrent else dtStartTime,
            'end_time': current_datetime if useCurrent else dtEndTime
        }
        
        sqlEngine = self._dbTool.getSQLEngine()
        result = pd.read_sql(sql, sqlEngine, params = params)

        return result.to_dict('records')

    def addRoom(self, roomName, capacity, buildingID, userID):
        sqlPath = os.path.join(PU.Paths.SQLFeaturesFolder.value, "AF3/AddRoom.sql")
        try:
            with open(sqlPath, 'r') as f:
                deleteRoomSQL = f.read()
        except FileNotFoundError:
            return {
              "addStatus": False
            }
        
        connData, cursor, error = self._dbTool.executeSQL(deleteRoomSQL, 
                                                          vars = {
                                                                  "roomName": roomName,
                                                                  "capacity": capacity,
                                                                  "buildingID": buildingID,
                                                                  "userID": userID
                                                                  },
                                                          commit = True, closeConn = True,
                                                          raiseException = False)
                
        if (error is not None):
            errorMsg = self._getModifyRoomError(f"{error}")
            return {
              "addStatus": False,
              "errorMessage": errorMsg
            }
        else:
            return {
              "addStatus": True
            }
            
    def editRoom(self, roomID, roomName, capacity, userID):
        sqlPath = os.path.join(PU.Paths.SQLFeaturesFolder.value, "AF3/EditRoom.sql")
        try:
            with open(sqlPath, 'r') as f:
                editRoomSQL = f.read()
        except FileNotFoundError:
            return {
              "editStatus": False
            }
        
        connData, cursor, error = self._dbTool.executeSQL(editRoomSQL, 
                                                          vars = {
                                                                  "roomID": roomID,
                                                                  "roomName": roomName,
                                                                  "capacity": capacity,
                                                                  "userID": userID
                                                                  },
                                                          commit = True, closeConn = True,
                                                          raiseException = False)
        
        if (error is not None):
            errorMsg = self._getModifyRoomError(f"{error}")
            return {
              "editStatus": False,
              "errorMessage": errorMsg
            }
        else:
            return {
              "editStatus": True
            }
            
    def deleteRoom(self, roomID, userID):
        sqlPath = os.path.join(PU.Paths.SQLFeaturesFolder.value, "AF3/DeleteRoom.sql")
        try:
            with open(sqlPath, 'r') as f:
                deleteRoomSQL = f.read()
        except FileNotFoundError:
            return {
              "deleteStatus": False
            }
        
        connData, cursor, error = self._dbTool.executeSQL(deleteRoomSQL, 
                                                          vars = {
                                                                  "roomID": roomID,
                                                                  "userID": userID
                                                                  },
                                                          commit = True, closeConn = True,
                                                          raiseException = False)
        
        if (error is not None):
            errorMsg = self._getModifyRoomError(f"{error}")
            return {
              "deleteStatus": False,
              "errorMessage": errorMsg
            }
        else:
            return {
              "deleteStatus": True
            }