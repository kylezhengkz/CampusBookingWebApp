import os
from datetime import datetime, timezone
import pandas as pd
import pytz
from typing import Optional, Dict, Any, List

import PyUtils as PU

from .BaseAPIService import BaseAPIService


class RoomService(BaseAPIService):
    
    # fetchAvailableRooms(roomName, minCapacity, maxCapacity, startTimeStr, endTimeStr): Retrieves all the available rooms
    def fetchAvailableRooms(self, roomName: Optional[str] = None, minCapacity:Optional[str] = None, maxCapacity: Optional[str] = None, 
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

    def deleteRoom(self, roomID):
        sqlPath = os.path.join(PU.Paths.SQLFeaturesFolder.value, "ModifyRooms/DeleteRoom.sql")
        try:
            with open(sqlPath, 'r') as f:
                deleteRoomSQL = f.read()
        except FileNotFoundError:
            return {
              "loginStatus": False,
              "errorMessage": f"Login SQL file not found at {sqlPath}"
            }
        
        connData, cursor, error = self._dbTool.executeSQL(deleteRoomSQL, 
                                                          vars = {
                                                                  "roomID": roomID
                                                                  },
                                                          commit = True, closeConn = False,
                                                          raiseException = False)
        
        if (error is not None):
            return {
              "deleteStatus": True
            }
        else:
            return {
              "deleteStatus": False
            }
        