import os
import uuid
import pandas as pd
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any, Union

import PyUtils as PU
from .BaseAPIService import BaseAPIService
from ..view.BaseView import BaseView


class DashboardService(BaseAPIService):
    def __init__(self, dbTool: PU.DBTool, view: Optional[BaseView] = None):
        super().__init__(dbTool, view = view)

        self._prefix = "[DASH]"
        self._errorPrefix = "[DASH SQL ERROR]"

    def print(self, *args, **kwargs):
        prefix = self._prefix
        super().print(*args, **kwargs, prefix = prefix)

    def printError(self, *args, **kwargs):
        prefix = self._errorPrefix
        super().print(*args, **kwargs, prefix = prefix)

    def getDashboardMetrics(self, user_id: Optional[str]) -> Tuple[bool, dict]:
        try:
            userUUID = uuid.UUID(user_id)
        except:
            return [False, "Invalid UUID format for user ID."]

        sqlPath = os.path.join(PU.Paths.SQLFeaturesFolder.value, "AF2/AF2.sql")

        if not os.path.exists(sqlPath):
            return [False, f"Dashboard SQL file not found at {sqlPath}"]

        try:
            query = PU.DBTool.readSQLFile(sqlPath)
            self.print(f"Running getDashboardMetrics for {user_id}")
            self.print(f"SQL Path: {sqlPath}")
        except Exception as e:
            return [False, f"Error reading SQL file: {e}"]

        try:
            connData, cursor, error = self._dbTool.executeSQL(query,
                                                              vars={"user_id": str(userUUID)},
                                                              commit=False, closeConn=False)

            result = cursor.fetchone()
            self.print(f"Query result: {result}")
            connData.putConn()

            if result:
                return [True, {
                    "avg_duration_mins": result[0],
                    "most_booked_hour": result[1]
                }]
            else:
                return [True, "No booking data found."]
        except Exception as e:
            self.printError(f"{e}")
            return [False, f"SQL execution error: {e}"]
        
    def getBookingFrequency(self, userId: uuid.UUID, startDateTime: Optional[datetime], endDateTime: Optional[datetime], queryLimit: Optional[int]) -> Tuple[bool, Union[str, List[Dict[str, Any]]]]:
        if (startDateTime is not None and endDateTime is not None and startDateTime > endDateTime):
            return [False, "Query end datetime cannot be earlier than the query start datetime"]
        elif (queryLimit is not None and queryLimit < 0):
            return [False, "Query limit must be non-negative"]
        
        sqlFile = os.path.join(PU.Paths.SQLFeaturesFolder.value, "AF1/AF1.sql")
        sql = PU.DBTool.readSQLFile(sqlFile)

        if (queryLimit is not None):
            sql = f"{sql[:-1]} LIMIT %(queryLimit)s;"

        params = {
            'userId': userId,
            'startDateTime': startDateTime,
            'endDateTime': endDateTime,
            'queryLimit': queryLimit
        }

        sqlEngine = self._dbTool.getSQLEngine()
        result = pd.read_sql(sql, sqlEngine, params = params)
        result = result.to_dict('records')

        return [True, result]