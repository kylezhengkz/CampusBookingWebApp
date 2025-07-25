import sys
import signal
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Optional, Iterable, List, Dict, Any, Tuple, Union
from datetime import datetime

import PyUtils as PU

from .constants.EnvironmentModes import EnvironmentModes
from .Config import Config
from .model.RoomService import RoomService
from .model.BuildingService import BuildingService
from .model.BookingService import BookingService
from .model.UserService import UserService
from .model.DashboardService import DashboardService
from .view.LogView import LogView

class App():
    def __init__(self, env: EnvironmentModes, isDebug: bool = False):
        self._isInitalized = False
        self._env = env
        self._app: Optional[Flask] = None
        self._config = Config.load(env)
        self._isDebug = isDebug

        self._dbTool = PU.DBTool(self._config.dbSecrets, database = self._config.database, useConnPool = True)

        self._logView = LogView(verbose = isDebug)
        self._logView.includePrefix = False

        self._buildingService = BuildingService(self._dbTool, view = self._logView)
        self._roomService = RoomService(self._dbTool, view = self._logView)
        self._bookingService = BookingService(self._dbTool, view = self._logView)
        self._userService = UserService(self._dbTool, view = self._logView)
        self._dashService = DashboardService(self._dbTool, view = self._logView)


    # Reference: See the __call__ operator in app.py of Flask's source code
    #   Needed to be served by some WSGI server
    def __call__(self, environ, start_response) -> Iterable[bytes]:
        return self._app.wsgi_app(environ, start_response)

    @property
    def app(self):
        return self._app
    
    @property
    def env(self):
        return self._env
    
    @property
    def port(self):
        return self._config.port
    
    @property
    def isDebug(self) -> bool:
        return self._isDebug
    
    @isDebug.setter
    def isDebug(self, newIsDebug: bool):
        self._isDebug = newIsDebug
        self._logView.verbose = newIsDebug

    def print(self, *args, **kwargs):
        self._logView.print(*args, **kwargs)

    def initialize(self):
        if (self._isInitalized):
            return
        
        self._isInitalized = True
        self.registerShutdown()

        app = Flask(__name__)
        cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
        app.config['CORS_HEADERS'] = 'Content-Type'

        @app.route('/')
        def index():
            return 'This is the backend server for the room booking app.'
        
        @app.route("/viewBuildings", methods=["GET"])
        def viewBuildings() -> List[Dict[str, Any]]:
            queryParams = {}
            db_operation = request.args.get("db_operation")
            
            if db_operation == "filter":
                buildingName = request.args.get("buildingName")
                addressLine1 = request.args.get("addressLine1")
                addressLine2 = request.args.get("addressLine2")
                city = request.args.get("city")
                province = request.args.get("province")
                country = request.args.get("country")
                postalCode = request.args.get("postalCode")
                response = self._buildingService.fetchBuildings(buildingName, addressLine1, addressLine2, 
                    city, province, country, postalCode)
            else:
                response = self._buildingService.fetchBuildings()
            
            return response
        
        @app.route("/viewAvailableRooms", methods=["GET"])
        def viewAvailableRooms() -> List[Dict[str, Any]]:
            
            response = []
            db_operation = request.args.get("db_operation")

            if db_operation == "filter":
                buildingId = request.args.get("building_id")
                roomName = request.args.get("room_name")
                minCapacity = request.args.get("min_capacity")
                maxCapacity = request.args.get("max_capacity")
                startTime = request.args.get("start_time")
                endTime = request.args.get("end_time")
                response = self._roomService.fetchAvailableRooms(buildingId, roomName, minCapacity, maxCapacity, startTime, endTime)
            else:
                response = self._roomService.fetchAvailableRooms()

            return response
    
        @app.route("/viewRoomsByBuildingID", methods=["GET"])
        def getRoomsByBuildingID() -> List[Dict[str, Any]]:
            response = []
            buildingId = request.args.get("building_id")
            print(buildingId)
            response = self._roomService.fetchRoomsByBuildingID(buildingId)
            print("INTERCEPT", response)
            return response
        
        @app.route("/addRoom", methods=["POST"])
        def addRoom():
            data = request.get_json()
            print("RECEIVED IN ADD", data)
            return self._roomService.addRoom(data["roomName"], data["capacity"], data["buildingID"], data["userID"])
        
        @app.route("/editRoom", methods=["POST"])
        def editRoom():
            data = request.get_json()
            print("RECEIVED IN EDIT", data)
            return self._roomService.editRoom(data["roomID"], data["roomName"], data["capacity"], data["userID"])
        
        @app.route("/deleteRoom", methods=["POST"])
        def deleteRoom():
            data = request.get_json()
            print("RECEIVED IN DELETE", data)
            return self._roomService.deleteRoom(data["roomID"], data["userID"] )
    
        @app.route("/viewAdminLog", methods=["POST"])
        def viewAdminLog():
            data = request.get_json()
            print("RECEIVED IN VIEWADMINLOG", data)
            return self._userService.viewAdminLog(data["userID"] )
        
        @app.route("/bookRoom", methods=["POST"])
        def bookRoom():
            data = request.get_json()

            if not data:
                return jsonify({ "success": False, "message": "No JSON data received" }), 400

            try:
                userId = data.get("user_id")
                roomId = data.get("room_id")
                startDateTimeStr = data.get("start_time")
                endDateTimeStr = data.get("end_time")
                participants = data.get("participants")

                if not all([userId, roomId, startDateTimeStr, endDateTimeStr]):
                    return jsonify({ "success": False, "message": "Missing required fields" }), 400

                start_dt = datetime.fromisoformat(startDateTimeStr)
                end_dt = datetime.fromisoformat(endDateTimeStr)


                # Call booking service
                success, message, bookingId = self._bookingService.bookRoom(userId, roomId, start_dt, end_dt, participants)
                # self.print(" BookingService.bookRoom returned ->", success, message, bookingId)

                return jsonify({
                    "success": success,
                    "message": message,
                    "booking_id": bookingId
                }), 200 if success else 400

            except Exception as e:
                self.print(f" Booking validation failed: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": str(e) or "Booking failed due to an unknown error."
                }), 400

        
        @app.route("/cancelBooking", methods=["POST"])
        def cancelBooking():
            data = request.get_json()
            if not data:
                return jsonify({ "success": False, "message": "No JSON data received" })

            bookingId = data.get("booking_id")
            userId = data.get("user_id")

            try:
                success, message = self._bookingService.cancelBooking(bookingId, userId)
                return jsonify({ "success": success, "message": message })
            except Exception as e:
                self.print(f"CancelBooking error: {str(e)}")
                return jsonify({ "success": False, "message": "Cancellation failed due to server error." })

        
        @app.route("/getFutureBookings", methods=["GET"])
        def getFutureBookings():
            userId = request.args.get("userId")
            self.print(f"[GET] /getFutureBookings - userId: {userId}")
            return self._bookingService.getFutureBookings(userId)

        @app.route("/getBookingsAndCancellations", methods=["GET"])
        def getBookingsAndCancellations():
            userId = request.args.get("userId")
            self.print(f"/getBookingsAndCancellations - userId: {userId}", prefix = "[GET]")
            return self._bookingService.getBookingsAndCancellations(userId)

        @app.route("/signup", methods=["POST"])
        def signup():
            data = request.get_json()
            self.print(f"RECEIVED IN SIGNUP {data}")
                    
            return self._userService.signup(data["username"], data["email"], data["password"])
      
        @app.route("/login", methods=["POST"])
        def login():
            data = request.get_json()
            self.print(f"RECEIVED IN LOGIN {data}")
                    
            return self._userService.login(data["username"], data["password"])
        
        @app.route("/getDashboardMetrics", methods=["GET"])
        def getDashboardMetrics():
            userId = request.args.get("userId")
            self.print(f"/getDashboardMetrics - userId: {userId}", prefix = "[GET]")
            success, result = self._dashService.getDashboardMetrics(userId)
            return jsonify(result), 200 if success else 400
        
        @app.route("/getBookingFrequency", methods=["POST"])
        def getBookingFrequency() -> Tuple[bool, Union[str, List[Dict[str, Any]]]]:
            data = request.get_json()

            userId = data.get("userId")
            startDateTime = data.get("startDateTime")
            endDateTime = data.get("endDateTime")
            queryLimit = data.get("queryLimit")

            try:
                userId  = uuid.UUID(userId)
            except ValueError:
                return [False, "Invalid UUID format for user ID"]
            
            if (startDateTime is not None):
                startDateTime = PU.DateTimeTool.strToDateTime(startDateTime)

            if (endDateTime is not None):
                endDateTime = PU.DateTimeTool.strToDateTime(endDateTime)

            if (queryLimit is not None):
                queryLimit = int(queryLimit)
            
            return self._dashService.getBookingFrequency(userId, startDateTime, endDateTime, queryLimit = queryLimit)


        @app.route("/updateUsername", methods=["POST"])
        def updateUsername() -> Tuple[bool, str]:
            data = request.get_json()
            
            userId = data.get("userId")
            newUsername = data.get("newUsername")

            try:
                userId  = uuid.UUID(userId)
            except ValueError:
                return [False, "Invalid UUID format for user ID"]

            if (not newUsername):
                return [False, "Missing old or new username."]

            return self._userService.updateUsername(userId, newUsername)

        @app.route("/updatePassword", methods=["POST"])
        def updatePassword() -> Tuple[bool, str]:
            data = request.get_json()

            userId = data.get("userId")
            newPassword = data.get("newPassword")
            oldPassword = data.get("oldPassword")

            try:
                userId  = uuid.UUID(userId)
            except ValueError:
                return [False, "Invalid UUID format for user ID"]

            if (newPassword is None or oldPassword is None):
                return [False, "Missing required fields."]

            return self._userService.updatePassword(userId, oldPassword, newPassword)


        self._app = app
        return app

    def shutdown(self, sig: Optional[int] = None, frame: Optional[int] = None):
        self._dbTool.closeDBPools()
        sys.exit(0)

    def registerShutdown(self):
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

    def run(self, *args, **kwargs):
        self._app.run(port = self.port, *args, debug = self._isDebug, **kwargs)